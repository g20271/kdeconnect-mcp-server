#!/usr/bin/env python3
"""Test script for official MCP protocol server"""

import json
import subprocess
import sys

def send_mcp_request(method: str, params: dict = None, request_id: int = 1):
    """Send MCP protocol request"""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request["params"] = params

    request_json = json.dumps(request)
    print(f"\n>>> MCP Request: {method}")
    print(f"    {request_json}")

    # Send to MCP server
    proc = subprocess.Popen(
        ["python3", "/home/aka/discord-bot-sessions/kanri/kdeconnect-mcp-server/mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = proc.communicate(input=request_json + "\n", timeout=5)

    if stderr:
        print(f"    [stderr]: {stderr.strip()}")

    if stdout:
        response = json.loads(stdout.strip())
        print(f"<<< MCP Response:")
        print(f"    {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response

    return None


def main():
    DEVICE_ID = "ff516277615c48c597002a1155bed4f4"

    print("=" * 70)
    print("KDE Connect MCP Server - Official Protocol Test")
    print("=" * 70)

    # Test 1: Initialize
    send_mcp_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    })

    # Test 2: List tools
    send_mcp_request("tools/list", {})

    # Test 3: Call tool - list devices
    send_mcp_request("tools/call", {
        "name": "kdeconnect_list_devices",
        "arguments": {}
    }, request_id=3)

    # Test 4: Call tool - get battery
    send_mcp_request("tools/call", {
        "name": "kdeconnect_get_battery",
        "arguments": {"device_id": DEVICE_ID}
    }, request_id=4)

    # Test 5: Call tool - get now playing
    send_mcp_request("tools/call", {
        "name": "kdeconnect_get_now_playing",
        "arguments": {"device_id": DEVICE_ID}
    }, request_id=5)

    # Test 6: Call tool - send notification
    send_mcp_request("tools/call", {
        "name": "kdeconnect_send_notification",
        "arguments": {
            "device_id": DEVICE_ID,
            "message": "✅ Official MCP Protocol Server Test Success!"
        }
    }, request_id=6)

    print("\n" + "=" * 70)
    print("✅ All official MCP protocol tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
