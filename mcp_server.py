#!/usr/bin/env python3
"""
KDE Connect MCP Server - FastMCP Implementation
Provides integration with KDE Connect devices through Model Context Protocol
"""

import sys
import os

# Import FastMCP first, before adding system paths
from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field
from fastmcp import FastMCP

# Add system site-packages for dbus-python after FastMCP import
sys.path.append('/usr/lib/python3/dist-packages')
import dbus
from dbus.mainloop.glib import DBusGMainLoop


# Initialize D-Bus
DBusGMainLoop(set_as_default=True)


class KDEConnectDBus:
    """D-Bus interface for KDE Connect"""

    BUS_NAME = "org.kde.kdeconnect"
    DAEMON_PATH = "/modules/kdeconnect"
    DEVICE_PATH_PREFIX = "/modules/kdeconnect/devices"

    def __init__(self):
        self.bus = dbus.SessionBus()
        self.daemon = self.bus.get_object(self.BUS_NAME, self.DAEMON_PATH)

    def _get_device_interface(self, device_id: str, plugin: str = None) -> dbus.Interface:
        """Get D-Bus interface for device/plugin"""
        path = f"{self.DEVICE_PATH_PREFIX}/{device_id}"
        if plugin:
            path += f"/{plugin}"
        obj = self.bus.get_object(self.BUS_NAME, path)
        return dbus.Interface(
            obj,
            f"org.kde.kdeconnect.device.{plugin}" if plugin else "org.kde.kdeconnect.device"
        )

    def _get_properties(self, device_id: str, plugin: str) -> dbus.Interface:
        """Get properties interface for plugin"""
        path = f"{self.DEVICE_PATH_PREFIX}/{device_id}/{plugin}"
        obj = self.bus.get_object(self.BUS_NAME, path)
        return dbus.Interface(obj, "org.freedesktop.DBus.Properties")

    def list_devices(self, reachable_only: bool = True, paired_only: bool = True) -> List[str]:
        """List all devices"""
        daemon_iface = dbus.Interface(self.daemon, "org.kde.kdeconnect.daemon")
        return list(daemon_iface.devices(paired_only, reachable_only))

    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Get device information"""
        path = f"{self.DEVICE_PATH_PREFIX}/{device_id}"
        obj = self.bus.get_object(self.BUS_NAME, path)
        props_iface = dbus.Interface(obj, "org.freedesktop.DBus.Properties")

        info = {
            "id": device_id,
            "name": str(props_iface.Get("org.kde.kdeconnect.device", "name")),
            "type": str(props_iface.Get("org.kde.kdeconnect.device", "type")),
            "is_paired": bool(props_iface.Get("org.kde.kdeconnect.device", "isPaired")),
            "is_reachable": bool(props_iface.Get("org.kde.kdeconnect.device", "isReachable"))
        }
        return info

    def get_battery(self, device_id: str) -> Dict[str, Any]:
        """Get battery status"""
        props = self._get_properties(device_id, "battery")
        return {
            "charge": int(props.Get("org.kde.kdeconnect.device.battery", "charge")),
            "is_charging": bool(props.Get("org.kde.kdeconnect.device.battery", "isCharging"))
        }

    def get_media_players(self, device_id: str) -> List[str]:
        """Get list of available media players"""
        props = self._get_properties(device_id, "mprisremote")
        try:
            players = props.Get("org.kde.kdeconnect.device.mprisremote", "playerList")
            return list(players) if players else []
        except:
            return []

    def set_media_player(self, device_id: str, player: str):
        """Set active media player"""
        props = self._get_properties(device_id, "mprisremote")
        props.Set("org.kde.kdeconnect.device.mprisremote", "player", player)

    def get_current_player(self, device_id: str) -> str:
        """Get current active player"""
        props = self._get_properties(device_id, "mprisremote")
        try:
            return str(props.Get("org.kde.kdeconnect.device.mprisremote", "player"))
        except:
            return ""

    def detect_active_player(self, device_id: str) -> Dict[str, Any]:
        """Detect which player is actually playing media"""
        import time

        players = self.get_media_players(device_id)
        current_player = self.get_current_player(device_id)
        props = self._get_properties(device_id, "mprisremote")

        active_players = []
        player_info = {}

        for player in players:
            try:
                # Switch to this player
                props.Set("org.kde.kdeconnect.device.mprisremote", "player", player)
                time.sleep(0.3)  # Wait for switch

                # Check if playing
                is_playing = bool(props.Get("org.kde.kdeconnect.device.mprisremote", "isPlaying"))
                title = str(props.Get("org.kde.kdeconnect.device.mprisremote", "title"))
                artist = str(props.Get("org.kde.kdeconnect.device.mprisremote", "artist"))

                player_info[player] = {
                    "is_playing": is_playing,
                    "has_media": bool(title or artist),
                    "title": title,
                    "artist": artist
                }

                if is_playing and (title or artist):
                    active_players.append(player)

            except Exception as e:
                player_info[player] = {"error": str(e)}

        # Restore original player
        if current_player:
            try:
                props.Set("org.kde.kdeconnect.device.mprisremote", "player", current_player)
            except:
                pass

        return {
            "active_players": active_players,
            "player_details": player_info,
            "original_player": current_player
        }

    def get_now_playing(self, device_id: str) -> Dict[str, Any]:
        """Get currently playing media information"""
        props = self._get_properties(device_id, "mprisremote")
        try:
            players = self.get_media_players(device_id)
            current_player = self.get_current_player(device_id)

            result = {
                "title": str(props.Get("org.kde.kdeconnect.device.mprisremote", "title")),
                "artist": str(props.Get("org.kde.kdeconnect.device.mprisremote", "artist")),
                "album": str(props.Get("org.kde.kdeconnect.device.mprisremote", "album")),
                "is_playing": bool(props.Get("org.kde.kdeconnect.device.mprisremote", "isPlaying")),
                "position": int(props.Get("org.kde.kdeconnect.device.mprisremote", "position")),
                "length": int(props.Get("org.kde.kdeconnect.device.mprisremote", "length")),
                "volume": int(props.Get("org.kde.kdeconnect.device.mprisremote", "volume")),
                "available_players": players,
                "current_player": current_player
            }
            return result
        except Exception as e:
            return {"error": str(e)}

    def media_control(self, device_id: str, action: str):
        """Control media playback"""
        iface = self._get_device_interface(device_id, "mprisremote")
        iface.sendAction(action)

    def send_ping(self, device_id: str, message: str = ""):
        """Send ping notification"""
        iface = self._get_device_interface(device_id, "ping")
        if message:
            iface.sendPing(message)
        else:
            iface.sendPing()

    def share_url(self, device_id: str, url: str):
        """Share URL to device"""
        iface = self._get_device_interface(device_id, "share")
        iface.shareUrl(url)

    def share_file(self, device_id: str, file_path: str):
        """Share file to device"""
        iface = self._get_device_interface(device_id, "share")
        file_url = f"file://{file_path}"
        iface.shareUrls([file_url])

    def ring_device(self, device_id: str):
        """Ring the device"""
        iface = self._get_device_interface(device_id, "findmyphone")
        iface.ring()

    def get_download_directory(self, device_id: str) -> str:
        """Get the download directory for received files"""
        import os
        home = os.path.expanduser("~")
        default_download = os.path.join(home, "Downloads")

        try:
            config_path = os.path.join(home, ".config", "kdeconnect", device_id + "_share", "config")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    for line in f:
                        if line.startswith("incoming_path="):
                            return line.split("=", 1)[1].strip()
        except:
            pass

        return default_download

    def list_received_files(self, device_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List recently received files from device"""
        import os
        import time

        download_dir = self.get_download_directory(device_id)

        if not os.path.exists(download_dir):
            return []

        files = []
        for filename in os.listdir(download_dir):
            filepath = os.path.join(download_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    "name": filename,
                    "path": filepath,
                    "size": stat.st_size,
                    "modified": time.ctime(stat.st_mtime),
                    "modified_timestamp": stat.st_mtime
                })

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x["modified_timestamp"], reverse=True)

        return files[:limit]

    def open_received_file(self, file_path: str):
        """Open a received file with default application"""
        import subprocess
        subprocess.Popen(["xdg-open", file_path])

    def get_notifications(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all active notifications with details"""
        iface = self._get_device_interface(device_id, "notifications")
        notification_ids = list(iface.activeNotifications())

        notifications = []
        for notif_id in notification_ids:
            try:
                # Get notification object
                notif_path = f"{self.DEVICE_PATH_PREFIX}/{device_id}/notifications/{notif_id}"
                notif_obj = self.bus.get_object(self.BUS_NAME, notif_path)
                notif_props = dbus.Interface(notif_obj, "org.freedesktop.DBus.Properties")

                # Get all properties
                notification = {
                    "id": notif_id,
                    "app_name": str(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "appName")),
                    "title": str(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "title")),
                    "text": str(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "text")),
                    "ticker": str(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "ticker")),
                    "dismissable": bool(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "dismissable")),
                    "has_icon": bool(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "hasIcon")),
                    "silent": bool(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "silent"))
                }

                # Try to get replyId if available
                try:
                    notification["reply_id"] = str(notif_props.Get("org.kde.kdeconnect.device.notifications.notification", "replyId"))
                except:
                    notification["reply_id"] = ""

                notifications.append(notification)
            except Exception as e:
                notifications.append({
                    "id": notif_id,
                    "error": str(e)
                })

        return notifications


# Initialize KDE Connect interface
kdeconnect = KDEConnectDBus()

# Create FastMCP server
mcp = FastMCP("KDE Connect MCP Server")


# ========== Pydantic Models for Input Validation ==========

class DeviceIdInput(BaseModel):
    """Input model for operations requiring a device ID"""
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device (use list_devices to find device IDs)"
    )


class MediaControlInput(BaseModel):
    """Input model for media control operations"""
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device"
    )
    action: Literal["Play", "Pause", "PlayPause", "Next", "Previous", "Stop"] = Field(
        ...,
        description="Media control action to perform"
    )


class NotificationInput(BaseModel):
    """Input model for sending notifications"""
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device"
    )
    message: str = Field(
        ...,
        description="The notification message to send",
        min_length=1,
        max_length=500
    )


class ShareUrlInput(BaseModel):
    """Input model for sharing URLs"""
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device"
    )
    url: str = Field(
        ...,
        description="The URL to share with the device",
        pattern=r'^https?://.+'
    )


class ShareFileInput(BaseModel):
    """Input model for sharing files"""
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device"
    )
    file_path: str = Field(
        ...,
        description="The absolute path to the file to share (e.g., /home/user/document.pdf)"
    )


class SetMediaPlayerInput(BaseModel):
    """Input model for setting media player"""
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device"
    )
    player: str = Field(
        ...,
        description="The name of the media player to activate (e.g., 'YouTube', 'Spotify', 'VLC')"
    )


class ListReceivedFilesInput(BaseModel):
    """Input model for listing received files"""
    device_id: str = Field(
        ...,
        description="The unique identifier of the KDE Connect device"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of files to return",
        ge=1,
        le=100
    )


class OpenFileInput(BaseModel):
    """Input model for opening files"""
    file_path: str = Field(
        ...,
        description="The absolute path to the file to open"
    )


# ========== Tool Definitions ==========

@mcp.tool()
def list_devices() -> Dict[str, Any]:
    """
    List all available KDE Connect devices

    Returns information about all paired and reachable KDE Connect devices,
    including their IDs, names, types, and connection status.

    Returns:
        A dictionary containing:
        - devices: List of device information dictionaries
        - count: Total number of devices found
    """
    devices = kdeconnect.list_devices()
    device_info = []
    for device_id in devices:
        try:
            info = kdeconnect.get_device_info(device_id)
            device_info.append(info)
        except Exception as e:
            device_info.append({"id": device_id, "error": str(e)})

    return {
        "devices": device_info,
        "count": len(device_info)
    }


@mcp.tool()
def get_battery(input: DeviceIdInput) -> Dict[str, Any]:
    """
    Get battery status from a device

    Retrieves the current battery level and charging status from the specified device.

    Args:
        input: Device identification

    Returns:
        Battery information including charge percentage and charging status
    """
    return kdeconnect.get_battery(input.device_id)


@mcp.tool()
def get_now_playing(input: DeviceIdInput) -> Dict[str, Any]:
    """
    Get currently playing media information

    Retrieves detailed information about the currently playing media on the device,
    including track title, artist, album, playback position, and available media players.

    Args:
        input: Device identification

    Returns:
        Media information including title, artist, album, playback status, and position
    """
    return kdeconnect.get_now_playing(input.device_id)


@mcp.tool()
def media_control(input: MediaControlInput) -> Dict[str, str]:
    """
    Control media playback on a device

    Send media control commands to the device to control playback of music, videos, or other media.

    Args:
        input: Device ID and media control action

    Returns:
        Status confirmation with the action that was performed
    """
    kdeconnect.media_control(input.device_id, input.action)
    return {"status": "success", "action": input.action}


@mcp.tool()
def send_notification(input: NotificationInput) -> Dict[str, str]:
    """
    Send a notification to a device

    Display a notification message on the target device. Useful for reminders,
    alerts, or sending quick messages.

    Args:
        input: Device ID and notification message

    Returns:
        Status confirmation
    """
    kdeconnect.send_ping(input.device_id, input.message)
    return {"status": "sent", "message": input.message}


@mcp.tool()
def share_url(input: ShareUrlInput) -> Dict[str, str]:
    """
    Share a URL to a device

    Send a URL to the device, which will typically open in the device's default browser.

    Args:
        input: Device ID and URL to share

    Returns:
        Status confirmation with the shared URL
    """
    kdeconnect.share_url(input.device_id, input.url)
    return {"status": "shared", "url": input.url}


@mcp.tool()
def share_file(input: ShareFileInput) -> Dict[str, str]:
    """
    Share a file to a device

    Transfer a file from this computer to the target device. The file will be
    saved to the device's configured download location.

    Args:
        input: Device ID and file path

    Returns:
        Status confirmation with the shared file path
    """
    kdeconnect.share_file(input.device_id, input.file_path)
    return {"status": "shared", "file": input.file_path}


@mcp.tool()
def ring_device(input: DeviceIdInput) -> Dict[str, str]:
    """
    Make a device ring to help locate it

    Trigger the device to ring with maximum volume, even if it's on silent mode.
    Useful for finding a lost phone or device.

    Args:
        input: Device identification

    Returns:
        Status confirmation
    """
    kdeconnect.ring_device(input.device_id)
    return {"status": "ringing"}


@mcp.tool()
def get_media_players(input: DeviceIdInput) -> Dict[str, Any]:
    """
    Get list of available media players on a device

    Retrieves all media player applications available on the device that support
    remote control through KDE Connect.

    Args:
        input: Device identification

    Returns:
        List of available players, current active player, and count
    """
    players = kdeconnect.get_media_players(input.device_id)
    current = kdeconnect.get_current_player(input.device_id)
    return {
        "available_players": players,
        "current_player": current,
        "count": len(players)
    }


@mcp.tool()
def set_media_player(input: SetMediaPlayerInput) -> Dict[str, str]:
    """
    Set the active media player on a device

    Switch to a specific media player for subsequent media control commands.
    Must be called before using media_control if multiple players are active.

    Args:
        input: Device ID and player name

    Returns:
        Status confirmation with the selected player
    """
    kdeconnect.set_media_player(input.device_id, input.player)
    return {
        "status": "player_set",
        "player": input.player
    }


@mcp.tool()
def detect_active_player(input: DeviceIdInput) -> Dict[str, Any]:
    """
    Automatically detect which media player is currently playing

    Scans all available media players to find which one is actively playing media.
    Returns detailed information about each player's state.

    Args:
        input: Device identification

    Returns:
        List of active players with their playback status and current media information
    """
    return kdeconnect.detect_active_player(input.device_id)


@mcp.tool()
def get_notifications(input: DeviceIdInput) -> Dict[str, Any]:
    """
    Get all active notifications from a device

    Retrieves all current notifications on the device, including app name,
    title, text content, and other metadata.

    Args:
        input: Device identification

    Returns:
        List of notifications with full details and count
    """
    notifications = kdeconnect.get_notifications(input.device_id)
    return {
        "notifications": notifications,
        "count": len(notifications)
    }


@mcp.tool()
def list_received_files(input: ListReceivedFilesInput) -> Dict[str, Any]:
    """
    List recently received files from a device

    Shows files that have been transferred from the device to this computer,
    sorted by most recent first.

    Args:
        input: Device ID and optional limit

    Returns:
        List of files with paths, sizes, modification times, and download directory
    """
    files = kdeconnect.list_received_files(input.device_id, input.limit)
    download_dir = kdeconnect.get_download_directory(input.device_id)
    return {
        "files": files,
        "count": len(files),
        "download_directory": download_dir
    }


@mcp.tool()
def open_file(input: OpenFileInput) -> Dict[str, str]:
    """
    Open a file with the default application

    Opens a file using the system's default application for that file type.
    Typically used to open files received from devices.

    Args:
        input: Absolute file path

    Returns:
        Status confirmation with the opened file path
    """
    kdeconnect.open_received_file(input.file_path)
    return {
        "status": "opened",
        "file_path": input.file_path
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
