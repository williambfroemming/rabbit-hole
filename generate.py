#!/usr/bin/env python3
"""
Rabbit Hole: Daily briefing generator.
Researches a topic, generates themed HTML, uploads to S3, sends Telegram.
"""
import os
import sys
import json
import re
import argparse
from datetime import datetime, date
from urllib.parse import urlparse

import anthropic
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from telegram import send_briefing


# Configuration
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 8,
}

RESEARCH_SYSTEM_PROMPT = """You are a research assistant. You MUST conduct exactly 6 to 8 web searches on the topic from meaningfully different angles before writing your research summary.

Angles to cover:
1. Origins and historical background
2. Mechanism or how it works
3. A controversy, paradox, or surprising fact
4. Modern impact or current state
5. Current debates or cutting-edge developments
6. Primary sources, academic research, or expert perspectives
7-8. Additional perspectives that deepen understanding

Do not stop searching until you have completed AT LEAST 6 searches. After all searches are complete, write a detailed, comprehensive research summary that synthesizes the findings. Include specific facts, figures, and surprising details."""

MAX_RESEARCH_TURNS = 12  # safety cap


def require_env(name, allow_missing=False):
    """Get environment variable or fail loudly."""
    val = os.environ.get(name)
    if not val and not allow_missing:
        print(f"ERROR: Required environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return val


def make_slug(topic):
    """Convert topic to URL-safe slug."""
    slug = topic.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug[:80]


def extract_publication(url):
    """Extract domain name from URL as publication."""
    try:
        domain = urlparse(url).netloc
        domain = domain.replace("www.", "")
        return domain.title()
    except Exception:
        return "Unknown"


def run_research(client, topic):
    """Research phase: run 6-8 web searches and collect sources."""
    messages = [
        {
            "role": "user",
            "content": f"Research this topic thoroughly with multiple searches: {topic}",
        }
    ]

    all_text_blocks = []
    sources = []
    seen_urls = set()
    search_count = 0
    turn = 0

    while turn < MAX_RESEARCH_TURNS:
        turn += 1
        try:
            # Use Haiku for research to conserve tokens on rate limit
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=3000,
                system=RESEARCH_SYSTEM_PROMPT,
                tools=[WEB_SEARCH_TOOL],
                messages=messages,
            )
        except anthropic.APIError as e:
            print(f"ERROR: Claude research call failed: {e}", file=sys.stderr)
            sys.exit(1)

        # Process response blocks
        for block in response.content:
            if block.type == "text":
                all_text_blocks.append(block.text)
            elif block.type == "server_tool_use" and block.name == "web_search":
                search_count += 1
                query = block.input.get("query", "")
                print(f"  Search {search_count}: {query}")
            elif block.type == "web_search_tool_result":
                # Extract URLs from search results
                if isinstance(block.content, list):
                    for result in block.content:
                        if hasattr(result, "url") and result.url not in seen_urls:
                            seen_urls.add(result.url)
                            title = getattr(result, "title", "Untitled")
                            publication = extract_publication(result.url)
                            sources.append(
                                {
                                    "url": result.url,
                                    "title": title,
                                    "publication": publication,
                                }
                            )

        # Stop if model is done
        if response.stop_reason == "end_turn":
            break

        # Continue agentic loop if model used a tool
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
        else:
            break

    research_summary = "\n\n".join(all_text_blocks)
    print(f"✓ Research complete: {search_count} searches, {len(sources)} sources")
    return research_summary, sources


def build_sources_block(sources):
    """Format sources as markdown list for prompt template."""
    if not sources:
        return "No sources collected."
    lines = []
    for i, s in enumerate(sources, 1):
        lines.append(
            f"{i}. [{s['title']}]({s['url']}) — {s['publication']}"
        )
    return "\n".join(lines)


def generate_html(client, topic, research_summary, sources, url):
    """Generate themed HTML page."""
    with open("prompts/deep_dive.md", "r") as f:
        template = f.read()

    filled = (
        template.replace("{{TOPIC}}", topic)
        .replace("{{RESEARCH}}", research_summary)
        .replace("{{SOURCES}}", build_sources_block(sources))
        .replace("{{URL}}", url)
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10000,
            messages=[{"role": "user", "content": filled}],
        )
    except anthropic.APIError as e:
        print(f"ERROR: Claude HTML generation failed: {e}", file=sys.stderr)
        sys.exit(1)

    html = response.content[0].text.strip()

    # Strip markdown fences if present
    if html.startswith("```"):
        html = re.sub(r"^```[a-z]*\n?", "", html)
        html = re.sub(r"\n?```$", "", html)
    html = html.strip()

    return html


def upload_to_s3(bucket, s3_key, html, topic):
    """Upload HTML to S3."""
    try:
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=html.encode("utf-8"),
            ContentType="text/html",
            CacheControl="max-age=86400",
            Metadata={
                "topic": topic,
                "generated": datetime.utcnow().isoformat(),
            },
        )
    except (BotoCoreError, ClientError) as e:
        print(f"ERROR: S3 upload failed: {e}", file=sys.stderr)
        sys.exit(1)


def load_queue():
    """Load queue.json."""
    try:
        with open("queue.json", "r") as f:
            data = json.load(f)
        return data.get("queue", []), data.get("topics_done", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Could not load queue.json: {e}", file=sys.stderr)
        sys.exit(1)


def load_topics_done():
    """Load topics_done.json."""
    try:
        with open("topics_done.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not load topics_done.json: {e}", file=sys.stderr)
        sys.exit(1)


def save_queue(queue):
    """Save queue.json."""
    data = {"queue": queue, "topics_done": []}
    try:
        with open("queue.json", "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"ERROR: Could not save queue.json: {e}", file=sys.stderr)
        sys.exit(1)


def save_topics_done(topics_done):
    """Save topics_done.json."""
    try:
        with open("topics_done.json", "w") as f:
            json.dump(topics_done, f, indent=2)
    except IOError as e:
        print(f"ERROR: Could not save topics_done.json: {e}", file=sys.stderr)
        sys.exit(1)


def generate_topic(client, topics_done_list):
    """Use Claude to generate a surprising new topic."""
    done_topics = [t.get("topic", "") for t in topics_done_list]
    done_str = ", ".join(done_topics) if done_topics else "None yet"

    prompt = f"""Generate a single surprising, niche, or lesser-known topic for a daily deep-dive briefing.
The topic should be fascinating and researchable but not obvious.

Already done: {done_str}

Reply with only the topic name, nothing else."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except anthropic.APIError as e:
        print(f"ERROR: Topic generation failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Rabbit Hole: Daily briefing generator")
    parser.add_argument("--dry-run", action="store_true", help="Skip S3 and Telegram")
    parser.add_argument(
        "--topic",
        default=None,
        help="Override: use this topic instead of queue",
    )
    args = parser.parse_args()

    # Validate environment
    api_key = require_env("ANTHROPIC_API_KEY")

    if args.dry_run:
        s3_bucket = os.environ.get("S3_BUCKET", "dry-run-bucket")
        cloudfront_base = os.environ.get("CLOUDFRONT_BASE", "https://dry-run.example.com")
    else:
        s3_bucket = require_env("S3_BUCKET")
        cloudfront_base = require_env("CLOUDFRONT_BASE")
        require_env("TELEGRAM_BOT_TOKEN")
        require_env("TELEGRAM_CHAT_ID")

    # Create output directory
    os.makedirs("output", exist_ok=True)

    client = anthropic.Anthropic(api_key=api_key)

    # Get topic
    if args.topic:
        topic = args.topic
        print(f"Using override topic: {topic}")
    else:
        queue, _ = load_queue()
        if queue:
            topic = queue[0]
            print(f"Processing topic from queue: {topic}")
        else:
            topics_done = load_topics_done()
            topic = generate_topic(client, topics_done)
            print(f"Generated new topic: {topic}")

    # Research
    print(f"\n→ Researching: {topic}")
    research_summary, sources = run_research(client, topic)

    # Pre-compute slug and URL
    today = date.today().isoformat()
    slug = make_slug(topic)
    filename = f"{today}-{slug}.html"
    s3_key = f"briefings/{filename}"
    url = f"{cloudfront_base.rstrip('/')}/{s3_key}"

    # Generate HTML
    print(f"→ Generating HTML...")
    # Trim research and sources to avoid rate limit on large payloads
    trimmed_research = research_summary[:3500]
    trimmed_sources = sources[:20]
    html = generate_html(client, topic, trimmed_research, trimmed_sources, url)

    # Save locally
    output_path = f"output/{filename}"
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✓ HTML saved to {output_path}")
    except IOError as e:
        print(f"ERROR: Could not write HTML: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"\nDRY RUN: Skipping S3 upload and Telegram")
        print(f"DRY RUN: Would upload to s3://{s3_bucket}/{s3_key}")
        print(f"DRY RUN: Public URL would be {url}")
        print(f"DRY RUN: Would send to Telegram")
        return topic, research_summary, sources, url

    # Upload to S3
    print(f"→ Uploading to S3...")
    upload_to_s3(s3_bucket, s3_key, html, topic)
    print(f"✓ S3 upload complete")

    # Update queue and archive
    if not args.topic:
        queue, _ = load_queue()
        queue.pop(0)
        save_queue(queue)

    topics_done = load_topics_done()
    topics_done.append(
        {
            "topic": topic,
            "date": today,
            "url": url,
            "source_count": len(sources),
        }
    )
    save_topics_done(topics_done)
    print(f"✓ Archived to topics_done.json")

    # Send Telegram
    print(f"→ Sending Telegram notification...")
    send_briefing(topic, research_summary, sources, url)

    print(f"\n✅ Complete: {topic}")
    print(f"   Public URL: {url}")

    return topic, research_summary, sources, url


if __name__ == "__main__":
    main()
