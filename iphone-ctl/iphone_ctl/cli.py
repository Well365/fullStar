import argparse
import json
import sys
from pathlib import Path

from iphone_ctl.core.exceptions import IOSkitError
from iphone_ctl.core.idevice import list_devices
from iphone_ctl.core.tools import resolve_binary
from iphone_ctl.core.wda import WdaClient
from iphone_ctl.ops.device import IOSDevice


def _json(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_devices(args) -> int:
    devices = list_devices()
    if args.json:
        _json([{"udid": d.udid} for d in devices])
        return 0
    if not devices:
        print("no devices")
        return 0
    for d in devices:
        print(d.udid)
    return 0


def cmd_shot(args) -> int:
    dev = IOSDevice(udid=args.udid, wda_url=args.wda_url, bundle_id=args.bundle_id)
    path = dev.screenshot(args.output, via_wda=args.via_wda)
    if args.json:
        _json(dev.info_dict(path))
    else:
        print(f"screenshot: {path}")
        print(f"udid: {dev.udid}")
    return 0


def cmd_analyze(args) -> int:
    dev = IOSDevice(udid=args.udid, wda_url=args.wda_url, bundle_id=args.bundle_id)
    _json(dev.analyze(via_wda_shot=args.via_wda))
    return 0


def cmd_tap(args) -> int:
    dev = IOSDevice(udid=args.udid, wda_url=args.wda_url, bundle_id=args.bundle_id)
    dev.tap(args.x, args.y, bundle_id=args.bundle_id)
    print(f"tap: ({args.x}, {args.y}) udid={dev.udid}")
    return 0


def cmd_swipe(args) -> int:
    dev = IOSDevice(udid=args.udid, wda_url=args.wda_url, bundle_id=args.bundle_id)
    dev.swipe(args.x1, args.y1, args.x2, args.y2, duration=args.duration, bundle_id=args.bundle_id)
    print(f"swipe: ({args.x1},{args.y1})→({args.x2},{args.y2}) {args.duration}s")
    return 0


def cmd_wda_status(args) -> int:
    client = WdaClient(base_url=args.wda_url, bundle_id=args.bundle_id)
    data = client.status()
    if args.json:
        _json(data)
    else:
        print(json.dumps(data, indent=2))
    return 0


def cmd_which(args) -> int:
    tools = {}
    for name in ("idevice_id", "idevicescreenshot", "iproxy"):
        try:
            tools[name] = str(resolve_binary(name))
        except IOSkitError:
            tools[name] = ""
    if args.json:
        _json(tools)
    else:
        for k, v in tools.items():
            print(f"{k}: {v or '(missing)'}")
    return 0


def cmd_proxy_hint(args) -> int:
    udid = args.udid or "$IOS_UDID"
    print("Run in a separate terminal (keep open while using WDA):")
    print(f"  iproxy 8100 8100 -u {udid}")
    print("Then: iphone-ctl wda status")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="iphone-ctl", description="iOS device toolkit (WDA + idevice)")
    parser.add_argument("--udid", "-u", help="Device UDID (or IOS_UDID)")
    parser.add_argument("--wda-url", default=None, help="WDA base URL (default IOS_WDA_URL)")
    parser.add_argument("--bundle-id", "-b", help="Bundle ID for WDA session")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("which", help="Show libimobiledevice binary paths")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_which)

    p = sub.add_parser("devices", help="List connected devices")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_devices)

    p = sub.add_parser("shot", help="Screenshot (default: idevicescreenshot)")
    p.add_argument("-o", "--output", type=Path)
    p.add_argument("--via-wda", action="store_true", help="Use WDA /screenshot instead")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_shot)

    p = sub.add_parser("analyze", help="Screenshot JSON for AI vision loop")
    p.add_argument("--via-wda", action="store_true")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("tap", help="Coordinate tap via WDA")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)
    p.set_defaults(func=cmd_tap)

    p = sub.add_parser("swipe", help="Coordinate swipe via WDA")
    p.add_argument("x1", type=int)
    p.add_argument("y1", type=int)
    p.add_argument("x2", type=int)
    p.add_argument("y2", type=int)
    p.add_argument("--duration", type=float, default=0.3)
    p.set_defaults(func=cmd_swipe)

    wda = sub.add_parser("wda", help="WebDriverAgent helpers")
    wda_sub = wda.add_subparsers(dest="wda_cmd", required=True)
    p = wda_sub.add_parser("status", help="GET /status")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_wda_status)
    p = wda_sub.add_parser("proxy", help="Print iproxy command")
    p.set_defaults(func=cmd_proxy_hint)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except IOSkitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
