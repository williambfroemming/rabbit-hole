#!/usr/bin/env python3
"""
AI Weekly Scan: research the AI ecosystem, generate a digest HTML, upload to S3, send Telegram.
Runs weekly (Monday mornings via GitHub Actions).
"""
import os
import sys
import json
import re
import argparse
from datetime import datetime, date, timedelta

import anthropic
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from telegram import send_weekly_briefing


# Configuration
WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 20,
}

MAX_RESEARCH_TURNS = 28
HISTORY_S3_KEY = "weekly/history.json"
HISTORY_MAX_WEEKS = 4  # keep rolling 4-week window


def get_week_range():
    """Return (week_range_str, iso_week_str, monday_date) for the current ISO week."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    def fmt(d):
        return d.strftime("%-d %b").lstrip("0")  # "5 May" style

    month_mon = monday.strftime("%b")
    month_sun = sunday.strftime("%b")
    year = sunday.strftime("%Y")

    if month_mon == month_sun:
        week_range = f"{monday.day}–{sunday.day} {month_sun} {year}"
    else:
        week_range = f"{monday.day} {month_mon} – {sunday.day} {month_sun} {year}"

    iso_week = monday.strftime("%Y-W%V")
    return week_range, iso_week, monday


def build_research_system_prompt(recent_coverage_text):
    """Build the research system prompt, injecting recent coverage for deduplication."""
    dedup_block = ""
    if recent_coverage_text.strip():
        dedup_block = f"""
IMPORTANT — DEDUPLICATION:
The following stories were already covered in the past 3–4 weeks. Do NOT include them as new items.
If there is a significant new development on one of these stories, include it with a clear "UPDATE:" prefix.

{recent_coverage_text}

"""

    return f"""You are an AI industry analyst conducting a comprehensive weekly scan of the AI ecosystem.
You MUST conduct at least 15 web searches covering each of the following topic areas before writing your summary.
Run searches in a diverse order — do not cluster all searches on one topic.

REQUIRED SEARCH AREAS (run 1–2 searches per area):
1. Major AI lab model releases this week (OpenAI, Anthropic, Google DeepMind, Meta, Mistral)
2. Trending AI/ML research papers this week (arXiv, Papers With Code, Semantic Scholar)
3. Trending GitHub AI/ML repositories and HuggingFace model releases this week
4. How developers are using AI agents and agentic workflows in production
5. AI safety incidents, production failures, hallucinations with real consequences, new exploits or jailbreaks
6. AI policy and regulation news (EU AI Act, US executive actions, China AI policy, copyright lawsuits)
7. New model benchmark results, leaderboard changes, API pricing updates this week
8. Developer community discussions on HackerNews, r/LocalLLaMA, Twitter/X about AI tools this week
9. High-quality AI tutorials, YouTube videos, technical deep-dives trending this week
10. New features in enterprise AI tools: Microsoft Copilot, Claude Code, Cursor, GitHub Copilot, major cloud AI platforms
{dedup_block}
After completing ALL searches, write a detailed research summary organized by topic area.
For each item include: what happened, why it matters, and a source citation.
Be specific — include model names, benchmark scores, star counts, pricing figures where available.
Include at least one concrete "try this" suggestion for the week."""


def require_env(name, allow_missing=False):
    """Get environment variable or fail loudly."""
    val = os.environ.get(name)
    if not val and not allow_missing:
        print(f"ERROR: Required environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return val


def run_research(client, week_range, recent_coverage_text):
    """Run agentic web search loop. Returns (research_summary, sources)."""
    print(f"Starting research for: {week_range}")
    system_prompt = build_research_system_prompt(recent_coverage_text)

    messages = [
        {
            "role": "user",
            "content": f"Conduct a comprehensive AI weekly scan for the week of {week_range}. "
                       f"Research all required topic areas with at least 15 searches total.",
        }
    ]

    all_text_blocks = []
    sources = []
    seen_urls = set()
    search_count = 0

    for turn in range(MAX_RESEARCH_TURNS):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            system=system_prompt,
            tools=[WEB_SEARCH_TOOL],
            messages=messages,
        )

        for block in response.content:
            if hasattr(block, "type"):
                if block.type == "text":
                    all_text_blocks.append(block.text)
                elif block.type == "server_tool_use":
                    search_count += 1
                    print(f"  Search {search_count}: {getattr(block, 'input', {}).get('query', '...')}")
                elif block.type == "web_search_tool_result":
                    for result in getattr(block, "content", []):
                        if hasattr(result, "url") and result.url not in seen_urls:
                            seen_urls.add(result.url)
                            sources.append(
                                {
                                    "url": result.url,
                                    "title": getattr(result, "title", ""),
                                    "publication": _extract_publication(result.url),
                                }
                            )

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

    research_summary = "\n\n".join(all_text_blocks)
    print(f"Research complete: {search_count} searches, {len(sources)} sources")
    return research_summary, sources


def _extract_publication(url):
    """Extract a clean publication name from a URL."""
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower()
        host = host.replace("www.", "")
        parts = host.split(".")
        return parts[0].capitalize() if parts else host
    except Exception:
        return url


def build_sources_block(sources):
    """Format sources list for template injection."""
    lines = []
    for i, s in enumerate(sources, 1):
        pub = f" ({s['publication']})" if s.get("publication") else ""
        title = s.get("title") or s["url"]
        lines.append(f"{i}. [{title}]({s['url']}){pub}")
    return "\n".join(lines)


def build_recent_coverage_text(history):
    """Format recent coverage history as a plain-text list for the system prompt."""
    if not history:
        return ""
    lines = []
    for entry in history:
        lines.append(f"Week of {entry['week']}:")
        for item in entry.get("items", []):
            lines.append(f"  - {item}")
    return "\n".join(lines)


def build_recent_coverage_html(history):
    """Format recent coverage as a compact list for the HTML template."""
    if not history:
        return "(No prior coverage — first run)"
    lines = []
    for entry in history:
        lines.append(f"Week of {entry['week']}:")
        for item in entry.get("items", []):
            lines.append(f"  - {item}")
    return "\n".join(lines)


def generate_html(client, week_range, research_summary, sources, url, recent_coverage_html):
    """Fill prompt template and call Claude to generate the HTML page."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "ai_weekly_scan.md")
    with open(prompt_path, "r") as f:
        template = f.read()

    filled = (
        template
        .replace("{{WEEK_RANGE}}", week_range)
        .replace("{{RESEARCH}}", research_summary[:8000])
        .replace("{{SOURCES}}", build_sources_block(sources[:30]))
        .replace("{{URL}}", url)
        .replace("{{RECENT_COVERAGE}}", recent_coverage_html)
    )

    print("Generating HTML...")
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=16000,
        messages=[{"role": "user", "content": filled}],
    )

    html = response.content[0].text.strip()
    # Strip markdown fences if present
    if html.startswith("```"):
        html = re.sub(r"^```[a-z]*\n?", "", html)
        html = re.sub(r"\n?```$", "", html)
    return html


def extract_weekly_items(client, research_summary):
    """Extract a flat list of this week's story headlines for history storage."""
    prompt = f"""From this AI weekly scan research, list the 10–15 main stories as short plain-text headlines.
One per line. No bullet characters, no numbering, no markdown. Just the headline.
Example: "OpenAI releases o3-mini with 60% cost reduction"

Research:
{research_summary[:5000]}

Return only the headlines, one per line."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        items = [line.strip() for line in text.splitlines() if line.strip()]
        return items
    except anthropic.APIError as e:
        print(f"WARNING: Could not extract weekly items for history: {e}", file=sys.stderr)
        return []


def load_history(s3_client, bucket):
    """Load weekly coverage history from S3. Returns list of week dicts."""
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=HISTORY_S3_KEY)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return []
        raise


def save_history(s3_client, bucket, history):
    """Save updated history to S3."""
    s3_client.put_object(
        Bucket=bucket,
        Key=HISTORY_S3_KEY,
        Body=json.dumps(history, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )


def upload_html(s3_client, bucket, s3_key, html, week_range):
    """Upload HTML to S3 with correct headers."""
    s3_client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=html.encode("utf-8"),
        ContentType="text/html; charset=utf-8",
        CacheControl="public, max-age=86400",
        Metadata={"week": week_range, "generated": date.today().isoformat()},
    )


def make_slug(week_range):
    """Generate a filename-safe slug from the week range."""
    slug = week_range.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:60]


def main():
    parser = argparse.ArgumentParser(description="Generate AI Weekly Scan digest")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate HTML locally; skip S3 upload and Telegram")
    args = parser.parse_args()

    api_key = require_env("ANTHROPIC_API_KEY")
    bucket = require_env("S3_BUCKET", allow_missing=args.dry_run)
    cloudfront_base = require_env("CLOUDFRONT_BASE", allow_missing=args.dry_run)

    if not args.dry_run:
        require_env("TELEGRAM_BOT_TOKEN")
        require_env("TELEGRAM_CHAT_ID")

    client = anthropic.Anthropic(api_key=api_key)

    week_range, iso_week, monday = get_week_range()
    print(f"Week: {week_range} ({iso_week})")

    os.makedirs("output", exist_ok=True)

    # --- Load history ---
    history = []
    s3_client = None
    if not args.dry_run:
        s3_client = boto3.client("s3")
        try:
            history = load_history(s3_client, bucket)
            print(f"Loaded {len(history)} weeks of history")
        except (BotoCoreError, ClientError) as e:
            print(f"WARNING: Could not load history: {e}", file=sys.stderr)

    recent_coverage_text = build_recent_coverage_text(history)
    recent_coverage_html = build_recent_coverage_html(history)

    # --- Research ---
    research_summary, sources = run_research(client, week_range, recent_coverage_text)

    # --- Compute paths ---
    slug = make_slug(week_range)
    filename = f"{monday.isoformat()}-ai-weekly-scan.html"
    s3_key = f"weekly/{filename}"
    url = f"{cloudfront_base.rstrip('/')}/weekly/{filename}" if cloudfront_base else f"file://output/{filename}"

    # --- Generate HTML ---
    html = generate_html(client, week_range, research_summary, sources, url, recent_coverage_html)

    # --- Save locally ---
    output_path = os.path.join("output", filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ HTML saved: {output_path}")

    if args.dry_run:
        print("Dry run complete. Skipping S3 upload and Telegram.")
        return

    # --- Upload to S3 ---
    try:
        upload_html(s3_client, bucket, s3_key, html, week_range)
        print(f"✓ Uploaded to S3: s3://{bucket}/{s3_key}")
    except (BotoCoreError, ClientError) as e:
        print(f"ERROR: S3 upload failed: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Update history ---
    try:
        items = extract_weekly_items(client, research_summary)
        history.append({"week": week_range, "items": items})
        history = history[-HISTORY_MAX_WEEKS:]  # keep rolling window
        save_history(s3_client, bucket, history)
        print(f"✓ History updated ({len(items)} items saved)")
    except Exception as e:
        print(f"WARNING: Could not update history: {e}", file=sys.stderr)

    # --- Send Telegram ---
    send_weekly_briefing(week_range, research_summary, sources, url)


if __name__ == "__main__":
    main()
