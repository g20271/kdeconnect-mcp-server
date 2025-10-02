# KDE Connect MCP Server

A Model Context Protocol (MCP) server that provides integration with KDE Connect, allowing you to interact with your connected devices through AI assistants.

## Features

- **Device Discovery**: List all available KDE Connect devices
- **Messaging**: Send SMS messages to paired devices
- **Device Control**: Pair/unpair devices, make devices ring for location
- **File Transfer**: Send files to connected devices
- **Battery Monitoring**: Get battery status from connected devices
- **Notifications**: Send notifications to devices

## Prerequisites

- KDE Connect installed and running on your system
- Python 3.8 or higher
- At least one paired KDE Connect device

## Installation

1. Clone or download this MCP server
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Add this server to your MCP client configuration. For Claude Desktop, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kdeconnect": {
      "command": "python",
      "args": ["/path/to/kdeconnect-mcp-server/mcp_server.py"]
    }
  }
}
```

## Available Tools

### `list_devices`
List all available KDE Connect devices with their pairing and reachability status.

**Parameters:**
- `only_paired` (boolean, optional): Only show paired devices
- `only_reachable` (boolean, optional): Only show reachable devices

### `send_message`
Send an SMS message to a paired device.

**Parameters:**
- `device_id` (string, required): ID of the target device
- `message` (string, required): Message to send

### `get_device_battery`
Get battery information from a connected device.

**Parameters:**
- `device_id` (string, required): ID of the target device

### `get_now_playing`
Get currently playing media information from a device.

**Parameters:**
- `device_id` (string, required): ID of the target device

### `media_control`
Control media playback on a device (play, pause, next, previous, stop).

**Parameters:**
- `device_id` (string, required): ID of the target device
- `action` (string, required): Media control action ("play", "pause", "playpause", "next", "previous", "stop")

### `set_volume`
Set media volume on a device.

**Parameters:**
- `device_id` (string, required): ID of the target device
- `volume` (number, required): Volume level (0-100)

### `seek_media`
Seek to a specific position in currently playing media.

**Parameters:**
- `device_id` (string, required): ID of the target device
- `position` (number, required): Position in seconds to seek to

### `send_notification`
Send a notification to a device.

**Parameters:**
- `device_id` (string, required): ID of the target device
- `title` (string, required): Notification title
- `text` (string, required): Notification text

### `pair_device`
Send a pairing request to a device.

**Parameters:**
- `device_id` (string, required): ID of the device to pair with

### `unpair_device`
Unpair from a device.

**Parameters:**
- `device_id` (string, required): ID of the device to unpair from

### `find_device`
Make a device ring/vibrate to help locate it.

**Parameters:**
- `device_id` (string, required): ID of the device to find

### `send_file`
Send a file to a connected device.

**Parameters:**
- `device_id` (string, required): ID of the target device
- `file_path` (string, required): Path to the file to send

## Usage Examples

1. **List all devices:**
   ```
   Use the list_devices tool to see all available KDE Connect devices
   ```

2. **Send a message:**
   ```
   Use send_message with device_id "your_device_id" and message "Hello from AI!"
   ```

3. **Find your phone:**
   ```
   Use find_device with your phone's device_id to make it ring
   ```

4. **Send a file:**
   ```
   Use send_file to transfer a document to your device
   ```

5. **Control media playback:**
   ```
   Use media_control with action "playpause" to toggle playback
   Use get_now_playing to see what's currently playing
   ```

6. **Adjust volume:**
   ```
   Use set_volume with volume 50 to set volume to 50%
   ```

## Advanced D-Bus Integration

For full media control functionality, the server can be extended with D-Bus integration. See `dbus_integration_example.py` for a complete implementation that provides:

- Real-time media player detection
- Detailed now-playing information (title, artist, album, artwork)
- Precise volume and seek controls
- Multiple player support

To use D-Bus integration:
1. Install D-Bus Python: `pip install dbus-python`
2. Run on a Linux system with KDE Connect daemon
3. Ensure proper D-Bus permissions

## Troubleshooting

- **"kdeconnect-cli not found"**: Make sure KDE Connect is installed and the CLI tools are in your PATH
- **Device not listed**: Ensure devices are paired and within network range
- **Permission errors**: Check that KDE Connect has proper permissions on your system
- **Media controls not working**: For full functionality, use the D-Bus integration example
- **D-Bus errors**: Ensure KDE Connect daemon is running and accessible via D-Bus

## Technical Architecture

This MCP server uses the KDE Connect CLI (`kdeconnect-cli`) to interact with the KDE Connect daemon. It provides a bridge between the MCP protocol and KDE Connect's functionality.

### Key Components

- **KdeConnectMCPServer**: Main server class handling MCP protocol
- **Tool Handlers**: Individual functions for each KDE Connect operation
- **CLI Wrapper**: Async interface to kdeconnect-cli commands

The server communicates with KDE Connect through the command line interface, parsing outputs and formatting them for MCP clients.

## Development

To extend this server:

1. Add new tool definitions in `_setup_handlers()`
2. Implement corresponding handler methods
3. Update the CLI wrapper if needed for new kdeconnect-cli commands

## License

MIT License - See LICENSE file for details.