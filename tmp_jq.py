#!/usr/bin/env python3
"""Small jq-compatible shim for the AgentBase helper scripts used in this workspace."""

from __future__ import annotations

import json
import sys
from urllib.parse import quote


def load_input(files: list[str]) -> object:
    data = ""
    if files:
        with open(files[0], "r", encoding="utf-8") as fh:
            data = fh.read()
    else:
        data = sys.stdin.read()
    if not data.strip():
        return None
    return json.loads(data)


def get_path(data: object, path: str) -> object:
    current = data
    for part in path.split("."):
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def emit(value: object, raw: bool = False, compact: bool = False) -> None:
    if raw:
        if value is None:
            print("")
        elif isinstance(value, (dict, list)):
            print(json.dumps(value, separators=(",", ":") if compact else None))
        else:
            print(value)
        return
    print(json.dumps(value, separators=(",", ":") if compact else None, ensure_ascii=False))


def parse_args(argv: list[str]) -> tuple[dict[str, str], dict[str, object], bool, bool, bool, str | None, list[str]]:
    args: dict[str, str] = {}
    json_args: dict[str, object] = {}
    raw = False
    null_input = False
    compact = False
    filter_expr = None
    files: list[str] = []
    i = 0
    while i < len(argv):
        item = argv[i]
        if item == "-r":
            raw = True
            i += 1
        elif item == "-c":
            compact = True
            i += 1
        elif item == "-e":
            i += 1
        elif item == "-n":
            null_input = True
            i += 1
        elif item == "-Rn":
            null_input = True
            i += 1
        elif item == "--arg":
            args[argv[i + 1]] = argv[i + 2]
            i += 3
        elif item == "--argjson":
            json_args[argv[i + 1]] = json.loads(argv[i + 2])
            i += 3
        elif filter_expr is None:
            filter_expr = item
            i += 1
        else:
            files.append(item)
            i += 1
    return args, json_args, raw, null_input, compact, filter_expr, files


def main() -> int:
    args, json_args, raw, null_input, compact, filt, files = parse_args(sys.argv[1:])
    if filt is None:
        return 0

    data = None if null_input else load_input(files)
    f = " ".join(filt.split())

    simple_defaults = {
        ".client_id // empty": ("client_id", ""),
        ".client_secret // empty": ("client_secret", ""),
        ".exp // 0": ("exp", 0),
        ".access_token // empty": ("access_token", ""),
        ".error // .message // empty": ("error", ""),
        ".registryUrl // empty": ("registryUrl", ""),
        ".username // empty": ("username", ""),
        ".secret // empty": ("secret", ""),
        ".password // empty": ("password", ""),
        ".repository // empty": ("repository", ""),
        ".data.key // .key // empty": ("data.key", ""),
    }
    if f in simple_defaults:
        path, default = simple_defaults[f]
        value = get_path(data, path)
        if value in (None, "") and f == ".error // .message // empty":
            value = get_path(data, "message")
        emit(default if value is None else value, raw=True, compact=compact)
        return 0

    if f == ".":
        emit(data, raw=raw, compact=compact)
        return 0

    if f == '{"client_id": $cid, "client_secret": $csec}':
        emit({"client_id": args["cid"], "client_secret": args["csec"]}, compact=compact)
        return 0

    if f.startswith("{minReplicas:"):
        emit(
            {
                "minReplicas": int(args["minReplicas"]),
                "maxReplicas": int(args["maxReplicas"]),
                "cpuUtilization": int(args["cpuUtil"]),
                "memoryUtilization": int(args["memUtil"]),
            },
            compact=compact,
        )
        return 0

    if "{name: $name, description: $description" in f:
        emit(
            {
                "name": args["name"],
                "description": args["description"],
                "imageUrl": args["imageUrl"],
                "flavorId": args["flavorId"],
                "command": [],
                "args": [],
                "environmentVariables": json_args["environmentVariables"],
                "autoscaling": json_args["autoscaling"],
            },
            compact=compact,
        )
        return 0

    if "{imageUrl: $imageUrl, flavorId: $flavorId" in f:
        emit(
            {
                "imageUrl": args["imageUrl"],
                "flavorId": args["flavorId"],
                "description": args["description"],
                "command": [],
                "args": [],
                "environmentVariables": json_args["environmentVariables"],
                "autoscaling": json_args["autoscaling"],
            },
            compact=compact,
        )
        return 0

    if f == ". + {imageAuth: {enabled: true, username: $user, password: $pass}}":
        assert isinstance(data, dict)
        data["imageAuth"] = {"enabled": True, "username": args["user"], "password": args["pass"]}
        emit(data, compact=compact)
        return 0

    if f == ". + {networkConfig: $nc}":
        assert isinstance(data, dict)
        data["networkConfig"] = json_args["nc"]
        emit(data, compact=compact)
        return 0

    if f.startswith("{mode: $mode, routeCidrs: $routeCidrs}"):
        out = {"mode": args["mode"], "routeCidrs": json_args["routeCidrs"]}
        if args.get("vpcId"):
            out["vpcId"] = args["vpcId"]
        if args.get("subnetId"):
            out["subnetId"] = args["subnetId"]
        emit(out, compact=compact)
        return 0

    if f == "$s|@uri":
        emit(quote(args["s"], safe=""), raw=True)
        return 0

    if f.startswith("if .listData then"):
        if isinstance(data, dict) and isinstance(data.get("listData"), list):
            for item in data["listData"]:
                if isinstance(item, dict):
                    item.pop("image", None)
        elif isinstance(data, dict):
            data.pop("image", None)
        emit(data, compact=compact)
        return 0

    sys.stderr.write(f"jq shim unsupported filter: {f}\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
