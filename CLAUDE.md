# Rabbit Hole Agent

## Purpose
Generate daily interactive deep dives on interesting topics. Research thoroughly, surface surprising facts, produce polished themed HTML, publish to S3 as a shareable URL, deliver to Telegram.

## Workflow
1. Read queue.json — take the first topic. If empty, generate a surprising one that hasn't been done before.
2. Run 6-8 web searches from meaningfully different angles on the topic.
3. Collect and store all source URLs and publication names from search results.
4. Classify the topic into a theme family (see prompts/deep_dive.md).
5. Use prompts/deep_dive.md to generate the themed interactive HTML page with sources embedded.
6. Save to output/{slug}.html and upload to S3 with correct headers.
7. Send Telegram message with teaser + public S3 URL.
8. Move topic from queue.json to topics_done.json with metadata.

## Quality bar
- Must include at least 3 genuinely surprising facts with citations
- Every factual claim must link to a real source URL
- Visual design must reflect the topic's character — not a generic template
- Interactive — clickable chapters, not a wall of text
- Mobile-friendly (this is read on a phone)
- Fully shareable — OG tags, clean URL, share button

## Never
- Invent, assume, or state facts without a source URL to back them up
- Recycle topics already in topics_done.json
- Generate the HTML page without completing web research first
- Send to Telegram if the S3 upload failed
- Use hardcoded colors — always use theme CSS variables

## Environment variables required
- ANTHROPIC_API_KEY
- S3_BUCKET
- CLOUDFRONT_BASE
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- AWS credentials via standard boto3 chain (IAM role on EC2 or local AWS profile)

## Running
```bash
# Install dependencies
pip install -r requirements.txt

# Dry run (test HTML generation, no S3 or Telegram)
python generate.py --dry-run --topic "Your Topic"

# Live run
python generate.py

# Override topic (for testing)
python generate.py --topic "Your Topic"
```

## Scheduled (EC2)
```
30 12 * * * cd ~/rabbit-hole && source venv/bin/activate && source .env && python3 generate.py >> logs/cron.log 2>&1
```

## Infrastructure Notes
- **Always use Ubuntu 22.04 (jammy) on EC2**, not Amazon Linux 2
  - Amazon Linux 2 ships with Python 3.7 which is incompatible with modern dependencies
  - Ubuntu 22.04 has Python 3.10 out of the box
- Terraform deploys everything: EC2, S3, CloudFront, IAM roles, security groups, cron jobs
- See `terraform/README.md` for setup instructions
