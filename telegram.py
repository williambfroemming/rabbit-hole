#!/usr/bin/env python3
"""
Telegram briefing notification.
Extracts 3 surprising facts from research and sends via Telegram Bot API.
"""
import os
import sys
import json
import requests
import anthropic


def extract_facts(client, topic, research_summary, sources):
    """Extract exactly 3 surprising facts with source attribution."""
    sources_text = "\n".join(
        f"- {s['title']} ({s['publication']}): {s['url']}"
        for s in sources
    )

    prompt = f"""From this research about "{topic}", extract exactly 3 surprising, counterintuitive, or little-known facts. Each fact must:
- Be a single sentence
- Come from one of the listed sources
- End with the publication name in parentheses, e.g. (BBC History)
- Only include verifiable facts with clear source attribution

Research:
{research_summary}

Sources:
{sources_text}

Return exactly 3 facts, one per line, numbered 1. 2. 3. with no other text."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except anthropic.APIError as e:
        print(f"ERROR: Claude fact extraction failed: {e}", file=sys.stderr)
        sys.exit(1)


def send_telegram(bot_token, chat_id, text):
    """Send message via Telegram Bot API."""
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=30,
        )
        if not resp.ok:
            print(
                f"ERROR: Telegram API returned {resp.status_code}: {resp.text}",
                file=sys.stderr,
            )
            sys.exit(1)
    except requests.RequestException as e:
        print(f"ERROR: Telegram request failed: {e}", file=sys.stderr)
        sys.exit(1)


def send_briefing(topic, research_summary, sources, url):
    """Main entry point: extract facts and send Telegram message."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY is not set", file=sys.stderr)
        sys.exit(1)

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN is not set", file=sys.stderr)
        sys.exit(1)

    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("ERROR: TELEGRAM_CHAT_ID is not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    facts = extract_facts(client, topic, research_summary, sources)

    message = f"""🕳 *Today's rabbit hole: {topic}*

{facts}

[Read the full deep dive →]({url})"""

    send_telegram(bot_token, chat_id, message)
    print(f"✓ Telegram message sent for: {topic}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Send Telegram briefing notification"
    )
    parser.add_argument("--topic", required=True, help="Topic name")
    parser.add_argument("--url", required=True, help="S3 URL of the briefing")
    parser.add_argument(
        "--research",
        default="",
        help="Research summary (for standalone use; normally passed from generate.py)",
    )
    parser.add_argument(
        "--sources",
        default="[]",
        help="JSON array of source objects (for standalone use; normally passed from generate.py)",
    )

    args = parser.parse_args()

    try:
        sources = json.loads(args.sources)
    except json.JSONDecodeError:
        print("ERROR: --sources must be valid JSON", file=sys.stderr)
        sys.exit(1)

    send_briefing(args.topic, args.research, sources, args.url)
