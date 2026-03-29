#!/usr/bin/env python3
"""
Telegram bot listener for adding topics to queue.json.
Runs as a background service on EC2, polls for incoming messages.
"""
import os
import sys
import json
import time
import requests
import boto3
from pathlib import Path
from botocore.exceptions import ClientError, BotoCoreError


OFFSET_FILE = "bot_offset.txt"
QUEUE_FILE = "queue.json"
LOG_FILE = "logs/bot.log"


def log(msg):
    """Log to file and stdout."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    Path(LOG_FILE).parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_offset():
    """Read the last processed update ID."""
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, "r") as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None
    return None


def save_offset(offset):
    """Save the last processed update ID."""
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))


def load_queue():
    """Load queue.json from S3 (with fallback to local file on first run)."""
    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        log("ERROR: S3_BUCKET not set")
        return {"queue": [], "topics_done": []}

    s3 = boto3.client("s3")

    try:
        obj = s3.get_object(Bucket=bucket, Key="data/queue.json")
        return json.loads(obj["Body"].read())
    except s3.exceptions.NoSuchKey:
        # First run — fallback to local file and migrate to S3
        try:
            with open(QUEUE_FILE, "r") as f:
                data = json.load(f)
            # Write to S3 immediately
            s3.put_object(Bucket=bucket, Key="data/queue.json",
                         Body=json.dumps(data, indent=2),
                         ContentType="application/json")
            log("✓ Migrated queue.json to S3")
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"queue": [], "topics_done": []}
    except (ClientError, BotoCoreError) as e:
        log(f"ERROR: S3 access failed: {e}")
        return {"queue": [], "topics_done": []}


def save_queue(data):
    """Save queue.json to S3."""
    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        log("ERROR: S3_BUCKET not set")
        return

    s3 = boto3.client("s3")

    try:
        s3.put_object(Bucket=bucket, Key="data/queue.json",
                     Body=json.dumps(data, indent=2),
                     ContentType="application/json")
    except (ClientError, BotoCoreError) as e:
        log(f"ERROR: Could not write queue.json to S3: {e}")


def send_telegram(bot_token, chat_id, text):
    """Send a message to Telegram."""
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
        if not resp.ok:
            log(f"ERROR: Telegram API returned {resp.status_code}: {resp.text}")
            return False
        return True
    except requests.RequestException as e:
        log(f"ERROR: Telegram request failed: {e}")
        return False


def poll_updates(bot_token, chat_id, offset=None, timeout=30):
    """Poll Telegram for new messages."""
    params = {"timeout": timeout, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/getUpdates",
            json=params,
            timeout=timeout + 5,
        )
        if not resp.ok:
            log(f"ERROR: getUpdates returned {resp.status_code}")
            return []
        data = resp.json()
        if not data.get("ok"):
            log(f"ERROR: Telegram error: {data.get('description', 'unknown')}")
            return []
        return data.get("result", [])
    except requests.RequestException as e:
        log(f"ERROR: Poll request failed: {e}")
        return []


def main():
    """Main polling loop."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        log("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        sys.exit(1)

    log("✓ Bot listener started")

    offset = get_offset()
    if offset:
        log(f"Resuming from update_id {offset}")

    while True:
        try:
            updates = poll_updates(bot_token, chat_id, offset=offset)

            for update in updates:
                update_id = update.get("update_id")
                message = update.get("message")

                if not message:
                    continue

                # Only process messages from the chat owner (chat_id)
                if message.get("chat", {}).get("id") != int(chat_id):
                    continue

                text = message.get("text", "").strip()
                if not text:
                    continue

                # Ignore bot's own messages and commands
                if text.startswith("/"):
                    continue

                # Add topic to queue
                queue_data = load_queue()
                queue_data["queue"].append(text)
                save_queue(queue_data)

                position = len(queue_data["queue"])
                log(f"✓ Added topic (position {position}): {text}")

                # Reply to user
                reply = f"✅ Added to queue (position {position}): \"{text}\""
                send_telegram(bot_token, chat_id, reply)

                # Update offset for next poll
                offset = update_id + 1
                save_offset(offset)

        except Exception as e:
            log(f"ERROR: Unexpected error in poll loop: {e}")
            time.sleep(5)  # Back off before retrying


if __name__ == "__main__":
    main()
