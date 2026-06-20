import platform
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Literal, Optional, Union

from tg_notify.core.exceptions import ScreenshotError

ScreenshotMode = Literal["full", "interactive", "window"]


def _ensure_macos() -> None:
    if platform.system() != "Darwin":
        raise ScreenshotError(
            f"Automatic screenshot is only supported on macOS (current: {platform.system()}). "
            "Capture manually and use photo(path) instead."
        )


def capture_screenshot(
    output_path: Optional[Union[str, Path]] = None,
    mode: ScreenshotMode = "full",
) -> Path:
    """Capture a screenshot and return the saved image path."""
    _ensure_macos()

    path = Path(output_path) if output_path else _default_output_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    command = ["screencapture", "-x"]
    if mode == "interactive":
        command.append("-i")
    elif mode == "window":
        command.append("-w")
    elif mode != "full":
        raise ScreenshotError(f"Unsupported screenshot mode: {mode}")

    command.append(str(path))
    _run_screencapture(command, cancelled_hint=True)
    _ensure_nonempty_image(path)
    return path


def capture_app_window(
    app: Optional[str] = None,
    *,
    app_path: Optional[Union[str, Path]] = None,
    bundle_id: Optional[str] = None,
    process_name: Optional[str] = None,
    wait_seconds: float = 2.0,
    window_index: int = 1,
    no_shadow: bool = False,
    output_path: Optional[Union[str, Path]] = None,
) -> Path:
    """Open an application, bring it to front, and capture a specific window."""
    _ensure_macos()

    if window_index < 1:
        raise ScreenshotError("window_index must be >= 1")

    launch_target, activate_name, proc_name = _resolve_app_target(
        app=app,
        app_path=app_path,
        bundle_id=bundle_id,
        process_name=process_name,
    )

    _launch_application(launch_target)

    path = Path(output_path) if output_path else _default_output_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    _wait_and_capture_app_window(
        activate_name=activate_name,
        process_name=proc_name,
        wait_seconds=wait_seconds,
        window_index=window_index,
        output_path=path,
        no_shadow=no_shadow,
    )
    _ensure_nonempty_image(path)
    return path


def _resolve_app_target(
    app: Optional[str],
    app_path: Optional[Union[str, Path]],
    bundle_id: Optional[str],
    process_name: Optional[str],
):
    if sum(bool(x) for x in (app, app_path, bundle_id)) != 1:
        raise ScreenshotError("Provide exactly one of: app, app_path, bundle_id")

    if app_path:
        path = Path(app_path)
        if path.suffix != ".app":
            raise ScreenshotError(f"app_path must end with .app: {path}")
        name = path.stem
        return (["open", str(path)], name, process_name or name)

    if bundle_id:
        if not app and not process_name:
            raise ScreenshotError(
                "bundle_id requires app (for activate) or process_name (for window lookup)"
            )
        activate = _canonical_app_name(app) if app else process_name
        proc = process_name or activate
        return (["open", "-b", bundle_id], activate, proc)

    assert app is not None
    canonical = _canonical_app_name(app)
    return (["open", "-a", canonical], canonical, process_name or canonical)


def _canonical_app_name(app: str) -> str:
    """Resolve app name from /Applications, case-insensitive (telegram -> Telegram)."""
    normalized = app.strip()
    if normalized.endswith(".app"):
        normalized = Path(normalized).stem

    hint_lower = normalized.lower()
    for apps_dir in (Path("/Applications"), Path.home() / "Applications"):
        if not apps_dir.is_dir():
            continue
        for bundle in apps_dir.glob("*.app"):
            if bundle.stem.lower() == hint_lower:
                return bundle.stem

    return normalized


def _launch_application(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise ScreenshotError(f"Failed to launch application: {command}") from exc
    except subprocess.CalledProcessError as exc:
        raise ScreenshotError(
            f"Failed to launch application ({' '.join(command)}): exit {exc.returncode}"
        ) from exc


def _wait_and_capture_app_window(
    activate_name: str,
    process_name: str,
    wait_seconds: float,
    window_index: int,
    output_path: Path,
    no_shadow: bool,
) -> None:
    deadline = time.time() + max(wait_seconds, 0.5)
    last_error = "unknown error"

    while time.time() < deadline:
        resolved_proc = _resolve_running_process_name(process_name) or process_name
        resolved_activate = _resolve_running_process_name(activate_name) or activate_name
        try:
            window_id = _get_window_id(resolved_proc, window_index, resolved_activate)
            _capture_by_window_id(window_id, output_path, no_shadow)
            return
        except ScreenshotError as exc:
            if _window_id_unsupported(exc):
                try:
                    bounds = _get_window_bounds(resolved_proc, window_index, resolved_activate)
                    _capture_by_bounds(bounds, output_path)
                    return
                except ScreenshotError as bounds_exc:
                    last_error = str(bounds_exc)
            else:
                last_error = str(exc)
        time.sleep(0.25)

    hint = ""
    canonical = _canonical_app_name(process_name)
    if process_name.lower() != canonical.lower():
        hint = f" Try: --app {canonical}"
    raise ScreenshotError(
        f"Timed out waiting for window {window_index} of '{process_name}': {last_error}.{hint}"
    )


def _window_id_unsupported(exc: ScreenshotError) -> bool:
    message = str(exc)
    lowered = message.lower()
    return (
        "-1728" in message
        or "id of window" in lowered
        or "不能获得" in message
        or "can't get id" in lowered
    )


def _capture_by_window_id(window_id: int, output_path: Path, no_shadow: bool) -> None:
    command = ["screencapture", "-x", "-l", str(window_id)]
    if no_shadow:
        command.insert(1, "-o")
    command.append(str(output_path))
    _run_screencapture(command)


def _capture_by_bounds(bounds: tuple[int, int, int, int], output_path: Path) -> None:
    x, y, width, height = bounds
    if width <= 0 or height <= 0:
        raise ScreenshotError(f"Invalid window bounds: {bounds}")
    region = f"{x},{y},{width},{height}"
    _run_screencapture(["screencapture", "-x", "-R", region, str(output_path)])


def _as_applescript_literal(s: str) -> str:
    """Quote + escape a string as an AppleScript string literal.

    Prevents AppleScript injection when interpolating app/process names: a value
    containing a double-quote would otherwise break out of the literal. Escapes
    backslash, double-quote, and newlines (which would split the source line).
    """
    esc = (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{esc}"'


def _get_window_bounds(process_name: str, window_index: int, activate_name: str) -> tuple[int, int, int, int]:
    act = _as_applescript_literal(activate_name)
    proc = _as_applescript_literal(process_name)
    idx = int(window_index)
    script = f"""
tell application {act} to activate
tell application "System Events"
    if not (exists process {proc}) then
        error "Process not running"
    end if
    tell process {proc}
        if (count of windows) < {idx} then
            error "Process has too few windows"
        end if
        set win to window {idx}
        set p to position of win
        set s to size of win
        return (item 1 of p as text) & "," & (item 2 of p as text) & "," & (item 1 of s as text) & "," & (item 2 of s as text)
    end tell
end tell
"""
    value = _run_osascript(script, context=f"get window bounds for '{process_name}'")
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4 or not all(part.lstrip("-").isdigit() for part in parts):
        raise ScreenshotError(f"Invalid window bounds for '{process_name}': {value!r}")
    return tuple(int(part) for part in parts)



def _list_process_names() -> list:
    result = _run_osascript(
        'tell application "System Events" to get name of every process',
        context="list processes",
    )
    return [part.strip() for part in result.split(",") if part.strip()]


def _resolve_running_process_name(hint: str):
    hint_lower = hint.lower()
    try:
        processes = _list_process_names()
    except ScreenshotError:
        return None

    exact = [name for name in processes if name.lower() == hint_lower]
    if len(exact) == 1:
        return exact[0]

    partial = [name for name in processes if hint_lower in name.lower()]
    if len(partial) == 1:
        return partial[0]

    return None


def _get_window_id(process_name: str, window_index: int, activate_name: str) -> int:
    act = _as_applescript_literal(activate_name)
    proc = _as_applescript_literal(process_name)
    idx = int(window_index)
    script = f'''
tell application {act} to activate
tell application "System Events"
    if not (exists process {proc}) then
        error "Process not running"
    end if
    tell process {proc}
        if (count of windows) < {idx} then
            error "Process has too few windows"
        end if
        return id of window {idx}
    end tell
end tell
'''
    value = _run_osascript(script, context=f"get window id for '{process_name}'")
    if not value.isdigit():
        raise ScreenshotError(f"Invalid window id returned for '{process_name}': {value!r}")
    return int(value)


def _run_osascript(script: str, context: str) -> str:
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise ScreenshotError("osascript not found on this system") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ScreenshotError(_format_osascript_error(context, detail)) from exc
    return result.stdout.strip()


def _format_osascript_error(context: str, detail: str) -> str:
    message = f"Could not {context}"
    if detail:
        message = f"{message}: {detail}"

    lowered = detail.lower()
    if "-25211" in detail or "assistive access" in lowered or "辅助访问" in detail:
        message += (
            "\n\n需要在 系统设置 → 隐私与安全性 → 辅助功能 中，"
            "授权当前终端（Terminal / iTerm / Cursor）。"
            "授权后若仍失败，请到 屏幕录制 中同样授权。"
        )
    return message


def _run_screencapture(command: list[str], cancelled_hint: bool = False) -> None:
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise ScreenshotError("screencapture command not found on this system") from exc
    except subprocess.CalledProcessError as exc:
        raise ScreenshotError(f"screencapture failed with exit code {exc.returncode}") from exc


def _ensure_nonempty_image(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ScreenshotError(f"Screenshot was not created at {path}.")


def _default_output_path() -> Path:
    handle = tempfile.NamedTemporaryFile(suffix=".png", prefix="tgkit-screenshot-", delete=False)
    handle.close()
    return Path(handle.name)
