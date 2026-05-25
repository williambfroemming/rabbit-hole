#!/usr/bin/env python3
"""
AI Weekly Scan: research the AI ecosystem, generate a digest HTML, upload to S3, send Telegram.
Runs weekly (Monday mornings via GitHub Actions).

Research architecture: map-reduce with parallel topic agents.
10 Claude instances run concurrently, each focused on one topic area (2 searches, small context).
Results are combined into a single research summary for HTML generation.
This avoids context window overflow entirely — each agent never exceeds ~20k tokens.
"""
import os
import sys
import json
import re
import argparse
import concurrent.futures
from datetime import date, timedelta

import anthropic
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from telegram import send_weekly_briefing


HISTORY_S3_KEY = "weekly/history.json"
HISTORY_MAX_WEEKS = 4

# Each topic gets its own isolated Claude call with this search tool (2 searches max)
TOPIC_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 2,
}
MAX_TOPIC_TURNS = 6  # safety cap per topic agent

# One entry per digest section — each becomes a parallel research agent
TOPIC_AREAS = [
    {
        "name": "Major AI Lab Releases",
        "section": "releases",
        "queries": [
            "OpenAI Anthropic Google DeepMind new model releases {week}",
            "Meta Mistral Cohere AI model announcements {week}",
        ],
    },
    {
        "name": "Research Papers",
        "section": "research",
        "queries": [
            "arXiv trending AI machine learning papers {week}",
            "papers with code trending AI research breakthrough {week}",
        ],
    },
    {
        "name": "Open Source",
        "section": "open-source",
        "queries": [
            "site:github.com AI ML trending repository stars 2026",
            "site:huggingface.co new model release downloads {week}",
        ],
    },
    {
        "name": "How Developers Are Building",
        "section": "building",
        "queries": [
            "AI agents agentic workflows production implementation {week}",
            "developers using LLMs automation real world patterns 2026",
        ],
    },
    {
        "name": "Risks and Failures",
        "section": "risks",
        "queries": [
            "AI hallucinations safety incidents production failures {week}",
            "AI jailbreak exploits vulnerabilities security issues {week}",
        ],
    },
    {
        "name": "Policy and Regulation",
        "section": "policy",
        "queries": [
            "EU AI Act enforcement AI regulation policy news {week}",
            "AI copyright lawsuit US China AI policy executive order {week}",
        ],
    },
    {
        "name": "Benchmarks and Evals",
        "section": "benchmarks",
        "queries": [
            "AI model benchmark results leaderboard comparison {week}",
            "LLM API pricing changes tokens cost comparison 2026",
        ],
    },
    {
        "name": "Community Pulse",
        "section": "community",
        "queries": [
            "HackerNews LocalLLaMA AI developer discussions {week}",
            "Twitter X AI developer community debates frustrations {week}",
        ],
    },
    {
        "name": "Learning Resources",
        "section": "learning",
        "queries": [
            "AI YouTube tutorials technical deep dives trending {week}",
            "AI development guides courses new techniques 2026",
        ],
    },
    {
        "name": "Enterprise Tools",
        "section": "enterprise",
        "queries": [
            "Claude Code Cursor GitHub Copilot new features {week}",
            "Microsoft Copilot enterprise AI platform updates {week}",
        ],
    },
]


def get_week_range():
    """Return (week_range_str, iso_week_str, monday_date) for the current ISO week."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    month_mon = monday.strftime("%b")
    month_sun = sunday.strftime("%b")
    year = sunday.strftime("%Y")

    if month_mon == month_sun:
        week_range = f"{monday.day}–{sunday.day} {month_sun} {year}"
    else:
        week_range = f"{monday.day} {month_mon} – {sunday.day} {month_sun} {year}"

    iso_week = monday.strftime("%Y-W%V")
    return week_range, iso_week, monday


def require_env(name, allow_missing=False):
    val = os.environ.get(name)
    if not val and not allow_missing:
        print(f"ERROR: Required environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return val


def _extract_publication(url):
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower().replace("www.", "")
        return host.split(".")[0].capitalize()
    except Exception:
        return url


def _strip_tool_results(content):
    """Replace web_search_tool_result payloads with a placeholder before storing in history.
    Keeps the tool_use block (so Claude knows what it searched) but drops the bulky result body.
    """
    stripped = []
    for block in content:
        if hasattr(block, "type") and block.type == "web_search_tool_result":
            stripped.append({
                "type": "web_search_tool_result",
                "tool_use_id": block.tool_use_id,
                "content": "[results extracted]",
            })
        else:
            stripped.append(block)
    return stripped


def research_one_topic(client, topic_area, week_range, dedup_context):
    """Single-topic agent: runs 2 searches in its own isolated context, returns a focused summary."""
    queries_formatted = "\n".join(
        f"- {q.replace('{week}', week_range)}" for q in topic_area["queries"]
    )

    dedup_note = ""
    if dedup_context:
        dedup_note = (
            f"\n\nAVOID repeating these recently-covered stories "
            f"(only include if significantly updated this week):\n{dedup_context}"
        )

    system = (
        f'You are an AI industry analyst. Your only task: research "{topic_area["name"]}" '
        f"developments for the week of {week_range}.\n\n"
        f"Run exactly these 2 web searches:\n{queries_formatted}\n\n"
        f"After both searches, write a 300–500 word focused summary covering:\n"
        f"- The 3–5 most significant developments\n"
        f"- For each: what happened, why it matters, specific details "
        f"(numbers, model names, benchmark scores, star counts)\n"
        f"- Source attribution for every claim{dedup_note}\n\n"
        f"LINKING RULES — follow exactly:\n"
        f"- For GitHub projects: always link to github.com/owner/repo directly, never to a news article or HN thread about it\n"
        f"- For HuggingFace models: always link to huggingface.co/org/model-name directly\n"
        f"- For arXiv papers: always link to arxiv.org/abs/XXXX.XXXXX directly\n"
        f"- For company announcements: link to the official blog post or press release, not third-party coverage\n"
        f"- If you cannot find the primary source URL, do not include the item\n\n"
        f"Be specific and factual. No hype language."
    )

    messages = [
        {"role": "user", "content": f"Research {topic_area['name']} for the week of {week_range}."}
    ]

    all_text = []
    sources = []
    seen_urls = set()

    for _ in range(MAX_TOPIC_TURNS):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2000,
                system=system,
                tools=[TOPIC_SEARCH_TOOL],
                messages=messages,
            )
        except anthropic.APIError as e:
            print(f"  WARNING: {topic_area['name']} API error: {e}", file=sys.stderr)
            break

        for block in response.content:
            if hasattr(block, "type"):
                if block.type == "text":
                    all_text.append(block.text)
                elif block.type == "server_tool_use":
                    print(f"  [{topic_area['name']}] searching: {getattr(block, 'input', {}).get('query', '...')}")
                elif block.type == "web_search_tool_result":
                    for result in getattr(block, "content", []):
                        if hasattr(result, "url") and result.url not in seen_urls:
                            seen_urls.add(result.url)
                            sources.append({
                                "url": result.url,
                                "title": getattr(result, "title", ""),
                                "publication": _extract_publication(result.url),
                            })

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": _strip_tool_results(response.content)})

    return {
        "name": topic_area["name"],
        "section": topic_area["section"],
        "summary": "\n\n".join(all_text),
        "sources": sources,
    }


def run_research(client, week_range, recent_coverage_text):
    """Map-reduce: run all topic agents in parallel, combine into one research summary."""
    print(f"Starting parallel research for: {week_range} ({len(TOPIC_AREAS)} topic agents)")

    all_sources = []
    seen_urls = set()
    topic_results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(TOPIC_AREAS)) as executor:
        future_to_topic = {
            executor.submit(research_one_topic, client, topic, week_range, recent_coverage_text): topic
            for topic in TOPIC_AREAS
        }
        for future in concurrent.futures.as_completed(future_to_topic):
            topic = future_to_topic[future]
            try:
                result = future.result()
                topic_results[result["section"]] = result
                print(f"  ✓ {result['name']} ({len(result['sources'])} sources)")
                for source in result["sources"]:
                    if source["url"] not in seen_urls:
                        seen_urls.add(source["url"])
                        all_sources.append(source)
            except Exception as e:
                print(f"  ERROR: {topic['name']} failed: {e}", file=sys.stderr)

    # Reassemble in section order
    sections = []
    for topic in TOPIC_AREAS:
        result = topic_results.get(topic["section"])
        if result and result["summary"].strip():
            sections.append(f"## {result['name']}\n\n{result['summary']}")

    research_summary = "\n\n---\n\n".join(sections)
    print(f"Research complete: {len(all_sources)} sources across {len(topic_results)}/{len(TOPIC_AREAS)} topics")
    return research_summary, all_sources


def build_sources_block(sources):
    lines = []
    for i, s in enumerate(sources, 1):
        pub = f" ({s['publication']})" if s.get("publication") else ""
        title = s.get("title") or s["url"]
        lines.append(f"{i}. [{title}]({s['url']}){pub}")
    return "\n".join(lines)


def build_recent_coverage_text(history):
    if not history:
        return ""
    lines = []
    for entry in history:
        lines.append(f"Week of {entry['week']}:")
        for item in entry.get("items", []):
            lines.append(f"  - {item}")
    return "\n".join(lines)


def build_recent_coverage_html(history):
    if not history:
        return "(No prior coverage — first run)"
    lines = []
    for entry in history:
        lines.append(f"Week of {entry['week']}:")
        for item in entry.get("items", []):
            lines.append(f"  - {item}")
    return "\n".join(lines)


def generate_html(client, week_range, research_summary, sources, url, recent_coverage_html):
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "ai_weekly_scan.md")
    with open(prompt_path, "r") as f:
        template = f.read()

    filled = (
        template
        .replace("{{WEEK_RANGE}}", week_range)
        .replace("{{RESEARCH}}", research_summary[:12000])
        .replace("{{SOURCES}}", build_sources_block(sources[:40]))
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
    if html.startswith("```"):
        html = re.sub(r"^```[a-z]*\n?", "", html)
        html = re.sub(r"\n?```$", "", html)
    # Convert non-ASCII to XML character references so the file is pure ASCII.
    # Eliminates all charset/encoding ambiguity regardless of how S3 or CloudFront serves it.
    html = html.encode("ascii", "xmlcharrefreplace").decode("ascii")
    return html


def extract_weekly_items(client, research_summary):
    prompt = (
        "From this AI weekly scan research, list the 10–15 main stories as short plain-text headlines.\n"
        "One per line. No bullets, no numbering, no markdown.\n"
        'Example: "OpenAI releases o3-mini with 60% cost reduction"\n\n'
        f"Research:\n{research_summary[:5000]}\n\nReturn only the headlines, one per line."
    )
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        return [line.strip() for line in text.splitlines() if line.strip()]
    except anthropic.APIError as e:
        print(f"WARNING: Could not extract weekly items for history: {e}", file=sys.stderr)
        return []


def load_history(s3_client, bucket):
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=HISTORY_S3_KEY)
        return json.loads(obj["Body"].read().decode("utf-8"))
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return []
        raise


def save_history(s3_client, bucket, history):
    s3_client.put_object(
        Bucket=bucket,
        Key=HISTORY_S3_KEY,
        Body=json.dumps(history, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json",
    )


def upload_html(s3_client, bucket, s3_key, html, week_range):
    s3_client.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=html.encode("utf-8"),
        ContentType="text/html; charset=utf-8",
        CacheControl="public, max-age=86400",
        Metadata={"week": week_range.replace("–", "-"), "generated": date.today().isoformat()},
    )


def make_slug(week_range):
    slug = re.sub(r"[^a-z0-9]+", "-", week_range.lower()).strip("-")
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

    # Load history
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

    # Research (parallel topic agents)
    research_summary, sources = run_research(client, week_range, recent_coverage_text)

    # Compute paths
    filename = f"{monday.isoformat()}-ai-weekly-scan.html"
    s3_key = f"weekly/{filename}"
    url = f"{cloudfront_base.rstrip('/')}/weekly/{filename}" if cloudfront_base else f"file://output/{filename}"

    # Generate HTML (research_summary is now 10x richer, no token truncation needed)
    html = generate_html(client, week_range, research_summary, sources, url, recent_coverage_html)

    # Save locally
    output_path = os.path.join("output", filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ HTML saved: {output_path} ({len(html):,} bytes)")

    if args.dry_run:
        print("Dry run complete. Skipping S3 upload and Telegram.")
        return

    # Upload to S3
    try:
        upload_html(s3_client, bucket, s3_key, html, week_range)
        print(f"✓ Uploaded to S3: s3://{bucket}/{s3_key}")
    except (BotoCoreError, ClientError) as e:
        print(f"ERROR: S3 upload failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Update history
    try:
        items = extract_weekly_items(client, research_summary)
        history.append({"week": week_range, "items": items})
        history = history[-HISTORY_MAX_WEEKS:]
        save_history(s3_client, bucket, history)
        print(f"✓ History updated ({len(items)} items saved)")
    except Exception as e:
        print(f"WARNING: Could not update history: {e}", file=sys.stderr)

    # Send Telegram (non-fatal — digest is already on S3)
    try:
        send_weekly_briefing(week_range, research_summary, sources, url)
    except SystemExit:
        print("WARNING: Telegram send failed — digest is live on S3 but no notification sent.", file=sys.stderr)


if __name__ == "__main__":
    main()
