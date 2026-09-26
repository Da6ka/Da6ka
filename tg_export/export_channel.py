"""Export a Telegram channel (including a private one) to JSON and Markdown.

Runs on your own computer, under your own Telegram account.
The login code and the session file never leave your machine.

Usage:
    python export_channel.py "https://t.me/+INVITE_HASH"
    python export_channel.py @public_channel_name
"""
import asyncio
import json
import os
import sys
from getpass import getpass

from telethon import TelegramClient
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.types import ChatInviteAlready, ChatInvitePeek

SESSION = "tg_export"  # creates tg_export.session next to the script, keep it private


def invite_hash(link):
    for prefix in ("https://t.me/+", "http://t.me/+", "t.me/+", "https://t.me/joinchat/", "t.me/joinchat/"):
        if link.startswith(prefix):
            return link[len(prefix):].strip("/")
    return None


async def resolve(client, link):
    h = invite_hash(link)
    if not h:
        return await client.get_entity(link)
    info = await client(CheckChatInviteRequest(h))
    if isinstance(info, (ChatInviteAlready, ChatInvitePeek)):
        return info.chat
    sys.exit("You are not a member of this channel. Join it in Telegram first, then rerun.")


def media_kind(msg):
    if msg.photo:
        return "photo"
    if msg.video:
        return "video"
    if msg.document:
        return "document"
    if msg.poll:
        return "poll"
    if msg.web_preview:
        return "link_preview"
    return None


async def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    link = sys.argv[1]

    api_id = os.environ.get("TG_API_ID") or input("api_id: ")
    api_hash = os.environ.get("TG_API_HASH") or getpass("api_hash: ")

    async with TelegramClient(SESSION, int(api_id), api_hash) as client:
        channel = await resolve(client, link)
        title = getattr(channel, "title", str(channel.id))
        print(f"Exporting: {title}")

        posts = []
        async for msg in client.iter_messages(channel, reverse=True):
            if msg.action:  # service messages: pinned, title changed, etc.
                continue
            posts.append({
                "id": msg.id,
                "date": msg.date.isoformat(),
                "text": msg.message or "",
                "media": media_kind(msg),
                "views": msg.views,
                "forwards": msg.forwards,
                "replies": msg.replies.replies if msg.replies else None,
                "reply_to": msg.reply_to.reply_to_msg_id if msg.reply_to else None,
                "grouped_id": msg.grouped_id,
            })
            if len(posts) % 200 == 0:
                print(f"  {len(posts)} posts...")

    with open("channel_export.json", "w", encoding="utf-8") as f:
        json.dump({"channel": title, "posts": posts}, f, ensure_ascii=False, indent=2)

    with open("channel_export.md", "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        for p in posts:
            if not p["text"] and not p["media"]:
                continue
            f.write(f"## {p['date'][:16].replace('T', ' ')} (#{p['id']})\n\n")
            if p["media"]:
                f.write(f"[{p['media']}]\n\n")
            f.write(p["text"] + "\n\n")

    print(f"Done: {len(posts)} posts -> channel_export.json, channel_export.md")


if __name__ == "__main__":
    asyncio.run(main())
