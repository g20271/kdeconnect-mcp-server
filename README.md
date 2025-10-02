# KDE Connect MCP Server

A Model Context Protocol (MCP) server built with FastMCP that provides seamless integration with KDE Connect, allowing AI assistants to control your Android/iOS devices.

## ✨ Features

### Device Management
- 📱 **Device Discovery**: List all paired and reachable devices
- 🔋 **Battery Monitoring**: Check battery level and charging status
- 🔔 **Notifications**: View and send notifications

### Media Control
- 🎵 **Playback Control**: Play, pause, skip tracks
- 📻 **Player Management**: Switch between media players (YouTube, Spotify, etc.)
- 🔍 **Auto-Detection**: Automatically detect active media players
- 📊 **Now Playing**: Get current track information

### File & Content Sharing
- 📤 **File Transfer**: Send files to devices
- 🔗 **URL Sharing**: Share links that open in device browser
- 📥 **Received Files**: List and open files received from devices

### Device Location
- 🔊 **Ring Device**: Make device ring at maximum volume to locate it

## 🚀 Quick Start

### Prerequisites

- **Linux** with KDE Connect installed
- **Python 3.12+**
- At least one **paired KDE Connect device**

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/g20271/kdeconnect-mcp-server.git
   cd kdeconnect-mcp-server
   ```

2. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Verify KDE Connect is running:
   ```bash
   kdeconnect-cli --list-available
   ```

### Configuration for Claude Desktop

Add to your `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kdeconnect": {
      "command": "/path/to/kdeconnect-mcp-server/venv/bin/python3",
      "args": [
        "/path/to/kdeconnect-mcp-server/mcp_server.py"
      ]
    }
  }
}
```

Replace `/path/to/` with the actual path to your installation.

## 🛠️ Available Tools (14)

### Device Management
1. **`list_devices`** - List all paired and reachable devices
2. **`get_battery`** - Get battery status (level, charging)
3. **`get_notifications`** - Get all active notifications
4. **`ring_device`** - Make device ring to locate it

### Media Control
5. **`get_now_playing`** - Get current media information
6. **`media_control`** - Control playback (Play, Pause, Next, Previous, Stop)
7. **`get_media_players`** - List available media players
8. **`set_media_player`** - Switch active media player
9. **`detect_active_player`** - Auto-detect which player is playing

### File & Content Sharing
10. **`share_file`** - Send file to device
11. **`share_url`** - Send URL to device
12. **`list_received_files`** - List files received from device
13. **`open_file`** - Open received file

### Notifications
14. **`send_notification`** - Send notification to device

## 💬 Usage Examples

Ask Claude:

- "Show me all my KDE Connect devices"
- "What's the battery level on my phone?"
- "Pause the music on my phone"
- "Send this file to my tablet"
- "Make my phone ring, I can't find it"
- "What's currently playing on my phone?"

## 🏗️ Technical Architecture

### Framework
- **FastMCP 2.12+**: High-level Python framework for MCP servers
- **Pydantic**: Input validation with detailed schemas
- **D-Bus**: Direct integration with KDE Connect daemon

### Key Components

```
mcp_server.py (675 lines)
├── KDEConnectDBus (290 lines)
│   └── D-Bus interface layer
├── Pydantic Models (80 lines)
│   └── Input validation schemas
└── Tool Definitions (280 lines)
    └── 14 tools with @mcp.tool() decorators
```

### Input Validation

Each tool uses Pydantic models with:
- Type checking
- Field descriptions
- Value constraints (min/max, regex patterns)
- Literal types for enums

Example:
```python
class MediaControlInput(BaseModel):
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device"
    )
    action: Literal["Play", "Pause", "PlayPause", "Next", "Previous", "Stop"] = Field(
        ...,
        description="Media control action to perform"
    )
```

## 🔧 Development

### Project Structure

```
kdeconnect-mcp-server/
├── mcp_server.py         # Main server implementation
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Package configuration
├── README.md            # This file
├── SETUP.md             # Detailed setup guide
└── test_mcp.py          # Test utilities
```

### Extending the Server

1. Define a Pydantic model for input validation
2. Create a tool function with `@mcp.tool()` decorator
3. Add comprehensive docstring
4. Implement the logic using `KDEConnectDBus`

Example:
```python
class NewToolInput(BaseModel):
    device_id: str = Field(..., description="Device ID")

@mcp.tool()
def new_tool(input: NewToolInput) -> Dict[str, Any]:
    """
    Brief description

    Detailed explanation of what this tool does.

    Args:
        input: Tool input parameters

    Returns:
        Description of return value
    """
    return kdeconnect.some_method(input.device_id)
```

## 🐛 Troubleshooting

### Server doesn't start
```bash
# Check Python version (requires 3.12+)
python3 --version

# Verify FastMCP installation
source venv/bin/activate
python3 -c "from fastmcp import FastMCP; print('OK')"

# Check system dbus-python
python3 -c "import dbus; print('OK')"
```

### No devices found
```bash
# Verify KDE Connect daemon is running
ps aux | grep kdeconnect

# Check device pairing
kdeconnect-cli --list-available

# Restart daemon if needed
killall kdeconnectd
/usr/lib/x86_64-linux-gnu/libexec/kdeconnectd &
```

### D-Bus errors
```bash
# Install required system packages
sudo apt install python3-dbus python3-gi kdeconnect
```

## 📋 Requirements

### System Requirements
- Linux (Ubuntu 24.04+ recommended)
- KDE Connect 24.x+
- D-Bus

### Python Requirements
- Python 3.12+
- fastmcp >= 1.0.0
- dbus-python >= 1.2.0 (system package)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Integrates with [KDE Connect](https://kdeconnect.kde.org/)
- Follows the [Model Context Protocol](https://modelcontextprotocol.io/) specification

---

**Made with ❤️ and Claude Code**
