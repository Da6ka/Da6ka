# Telegram channel export

Exports all posts of a Telegram channel you are a member of (private channels included)
to `channel_export.json` and `channel_export.md`, using your own account via the Telegram API.

Everything runs locally: the login code, the password and the session file stay on your computer.

## 1. Get API keys (once)

1. Open https://my.telegram.org and log in with your phone number.
2. Go to **API development tools** and create an app (any name and short name, platform: Desktop).
3. Copy `api_id` and `api_hash`. Treat them like a password.

## 2. Install

```bash
cd tg_export
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Run

```bash
python export_channel.py "https://t.me/+INVITE_HASH"
```

The script asks for `api_id`, `api_hash`, your phone number, the login code Telegram sends you,
and the 2FA password if you have one. Next runs reuse `tg_export.session` and do not ask again.

## 4. Share the result

Upload `channel_export.json` (or `channel_export.md`) to Google Drive and share the link with Claude.

## Security

- Never send the login code, `api_hash` or `tg_export.session` to anyone. The session file gives full access to the account.
- When finished, delete `tg_export.session` and end the session in Telegram:
  Settings > Devices > terminate the one named after your API app.
