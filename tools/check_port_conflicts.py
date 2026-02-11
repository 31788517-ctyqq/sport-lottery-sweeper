#!/usr/bin/env python3
"""
Check port listener conflicts on Windows and show owning processes.

Examples:
  python tools/check_port_conflicts.py --port 8001
  python tools/check_port_conflicts.py --port 8001 --host 127.0.0.1
"""
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Listener:
    local_addr: str
    local_port: int
    state: str
    pid: int
    command_line: str = ""


NETSTAT_LINE = re.compile(
    r"^\s*TCP\s+(\S+):(\d+)\s+(\S+):(\S+)\s+(\S+)\s+(\d+)\s*$",
    re.IGNORECASE,
)


def run(cmd: List[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    return (proc.stdout or "") + (proc.stderr or "")


def get_listeners() -> List[Listener]:
    output = run(["netstat", "-ano", "-p", "TCP"])
    listeners: List[Listener] = []
    for line in output.splitlines():
        m = NETSTAT_LINE.match(line)
        if not m:
            continue
        local_addr, local_port, _remote_addr, _remote_port, state, pid = m.groups()
        if state.upper() != "LISTENING":
            continue
        listeners.append(
            Listener(
                local_addr=local_addr,
                local_port=int(local_port),
                state=state.upper(),
                pid=int(pid),
            )
        )
    return listeners


def get_command_line(pid: int) -> str:
    ps_cmd = (
        "Get-CimInstance Win32_Process "
        f"-Filter \"ProcessId={pid}\" | "
        "Select-Object -ExpandProperty CommandLine"
    )
    output = run(["powershell", "-NoProfile", "-Command", ps_cmd]).strip()
    return output


def host_matches_listener(host: str, local_addr: str) -> bool:
    if local_addr in ("0.0.0.0", "::"):
        return True
    return host == local_addr


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check port listener conflicts on Windows.")
    parser.add_argument("--port", type=int, required=True, help="Port to inspect")
    parser.add_argument("--host", default=None, help="Host to match (e.g. 127.0.0.1)")
    args = parser.parse_args(argv)

    listeners = [l for l in get_listeners() if l.local_port == args.port]
    if not listeners:
        print(f"No listeners found on port {args.port}.")
        return 0

    for l in listeners:
        l.command_line = get_command_line(l.pid)

    print(f"Listeners on port {args.port}: {len(listeners)}")
    for l in listeners:
        print(f"- {l.local_addr}:{l.local_port} PID={l.pid}")
        if l.command_line:
            print(f"  CMD: {l.command_line}")
        else:
            print("  CMD: <unknown>")

    if args.host:
        matched = [l for l in listeners if host_matches_listener(args.host, l.local_addr)]
        print("")
        print(f"Host match for {args.host}:{args.port}: {len(matched)}")
        for l in matched:
            print(f"- {l.local_addr}:{l.local_port} PID={l.pid}")
            print(f"  CMD: {l.command_line or '<unknown>'}")

        if len(matched) > 1:
            print("")
            print("Warning: multiple listeners match this host; routing can be non-deterministic.")

    if len(listeners) > 1:
        print("")
        print("Warning: multiple listeners detected on the same port.")
        print("Consider stopping the unexpected process before testing.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
