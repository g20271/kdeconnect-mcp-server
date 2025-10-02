# KDE Connect MCP Server セットアップガイド

## 🎯 概要

FastMCPフレームワークを使用したKDE Connect MCPサーバー。
Claude CodeなどのMCPクライアントで使用可能。

## ✅ 実装内容

### フレームワーク
- **FastMCP 2.12+**: Pythonの高速MCPフレームワーク
- **D-Bus統合**: KDE Connectの全機能にアクセス
- **14ツール**: デバイス制御の包括的なツール群

## 📦 利用可能なTools（14個）

1. **list_devices** - デバイス一覧取得
2. **get_battery** - バッテリー状態取得
3. **get_now_playing** - 再生中メディア情報取得
4. **media_control** - メディア制御（Play/Pause/Next/Previous/Stop）
5. **send_notification** - 通知送信
6. **share_url** - URL共有
7. **share_file** - ファイル共有
8. **ring_device** - デバイスを鳴らす
9. **get_media_players** - メディアプレイヤー一覧
10. **set_media_player** - アクティブプレイヤー設定
11. **detect_active_player** - 再生中プレイヤー自動検出
12. **get_notifications** - 通知一覧取得
13. **list_received_files** - 受信ファイル一覧
14. **open_file** - ファイルを開く

## 🔧 Claude Codeセットアップ

### 1. 依存関係をインストール

```bash
cd /home/user/kdeconnect-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# システムのdbus-pythonを使用（venvにはインストール不要）
```

### 2. 設定ファイルを開く

```bash
nano ~/.config/Claude/claude_desktop_config.json
```

### 3. MCPサーバーを追加

```json
{
  "mcpServers": {
    "kdeconnect": {
      "command": "/home/user/kdeconnect-mcp-server/venv/bin/python3",
      "args": [
        "/home/user/kdeconnect-mcp-server/mcp_server.py"
      ]
    }
  }
}
```

### 4. Claude Code再起動

設定を反映させるため、Claude Codeを完全に再起動します。

## 🧪 テスト方法

### サーバー起動確認
```bash
source venv/bin/activate
python3 mcp_server.py
# FastMCPロゴが表示されればOK（Ctrl+Cで終了）
```

### デバイス接続確認
```bash
kdeconnect-cli --list-available
# デバイスIDをメモする
```


## 🎯 Claude Codeでの使い方

### デバイス一覧取得
```
KDE Connectのデバイスを表示して
```

### バッテリー確認
```
スマホのバッテリー残量を教えて
```

### メディア制御
```
スマホで再生中の曲をスキップして
```

### 通知送信
```
スマホに「作業開始」と通知して
```

### URL共有
```
https://example.com をスマホに送って
```

### ファイル共有
```
/path/to/document.pdf をスマホに送って
```

### デバイスを探す
```
スマホを鳴らして探して
```

## 🔍 トラブルシューティング

### MCPサーバーが認識されない

1. **設定ファイルのJSONが正しいか確認**
   ```bash
   cat ~/.config/Claude/claude_desktop_config.json | jq .
   ```

2. **パスが正しいか確認**
   ```bash
   ls -la /home/user/kdeconnect-mcp-server/mcp_server.py
   ```

3. **実行権限確認**
   ```bash
   chmod +x /home/user/kdeconnect-mcp-server/mcp_server.py
   ```

### D-Busエラー

```bash
# KDE Connect デーモン起動確認
ps aux | grep kdeconnect

# 起動していない場合
/usr/lib/x86_64-linux-gnu/libexec/kdeconnectd &
```

### Python依存関係

```bash
# 必要なパッケージ確認
python3 -c "import dbus; print('dbus: OK')"
source venv/bin/activate
python3 -c "from fastmcp import FastMCP; print('FastMCP: OK')"
```

システムパッケージとして必要：
```bash
sudo apt install python3-dbus python3-gi kdeconnect
```

## ✅ 動作確認済み環境

- **OS**: Ubuntu 24.04 (Noble)
- **Python**: 3.12+
- **FastMCP**: 2.12.4
- **KDE Connect**: 24.x
- **Claude Code**: 最新版
- **デバイス**: Poco F7 (Android)

## 🎉 完了

FastMCPフレームワークを使用したKDE Connect MCPサーバーが完成！
Claude Codeから直接スマートフォンを制御できます！
