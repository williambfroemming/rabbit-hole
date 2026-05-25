# AI Weekly Scan

## Purpose
Generate a weekly digest of the AI ecosystem — model releases, research, open source, risks, policy, benchmarks, community pulse, and developer trends. Publishes to S3/CloudFront as a shareable URL, delivers a 3-bullet summary to Telegram.

## How It Works
1. 10 parallel Claude Sonnet agents each research one topic area (2 web searches each)
2. All source URLs are HTTP-validated — dead or wrong URLs dropped
3. An editorial review agent fact-checks specific claims (GitHub repos, model versions, benchmark scores) using up to 6 targeted verification searches — removes anything it can't confirm
4. Claude generates the full HTML digest from `prompts/ai_weekly_scan.md`
5. HTML uploaded to S3, history updated for week-over-week deduplication
6. Telegram notification sent with 3-bullet summary + link

## Running
```bash
# Install dependencies
pip install -r requirements.txt

# Dry run (research + HTML locally, no S3 or Telegram)
python generate_weekly.py --dry-run

# Live run
python generate_weekly.py
```

## Scheduled
Runs every Monday at 9 AM UTC via GitHub Actions (`.github/workflows/ai-weekly-scan.yml`).
Manual trigger: Actions tab → AI Weekly Scan → Run workflow.

## Environment Variables
Set as GitHub Actions secrets:
- `ANTHROPIC_API_KEY`
- `S3_BUCKET`
- `CLOUDFRONT_BASE`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` + `AWS_DEFAULT_REGION`

For local dry runs, set `ANTHROPIC_API_KEY` only.

## Output
- HTML: `https://d1m43j2of227l.cloudfront.net/weekly/YYYY-MM-DD-ai-weekly-scan.html`
- S3: `s3://rabbit-hole-briefings-bfroemming/weekly/`
- History (dedup): `s3://rabbit-hole-briefings-bfroemming/weekly/history.json`

## Infrastructure
- S3 + CloudFront managed by `terraform/` — still active, do not destroy
- EC2 instance (`i-0117df9d3b176b747`) — no longer used, can be decommissioned
- GitHub Actions replaced EC2 cron

## Never
- Include claims without a verifiable source URL
- Skip the editorial review step
- Send Telegram if S3 upload failed
