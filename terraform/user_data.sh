#!/bin/bash
set -e

# Update system
apt-get update
apt-get install -y python3-pip python3-venv git

# Clone repo
cd /home/ubuntu
git clone https://github.com/yourusername/rabbit-hole.git rabbit-hole
cd rabbit-hole

# Create venv and install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with secrets
cat > .env << EOF
export ANTHROPIC_API_KEY="${api_key}"
export S3_BUCKET="${s3_bucket}"
export CLOUDFRONT_BASE="${cloudfront_base}"
export TELEGRAM_BOT_TOKEN="${telegram_token}"
export TELEGRAM_CHAT_ID="${telegram_chat_id}"
EOF

# Create logs directory
mkdir -p logs

# Set up cron job (5:30am Pacific = 12:30pm UTC)
(crontab -l 2>/dev/null || true; echo "30 12 * * * cd /home/ubuntu/rabbit-hole && source venv/bin/activate && source .env && python3 generate.py >> logs/cron.log 2>&1") | crontab -

# Fix permissions
chown -R ubuntu:ubuntu /home/ubuntu/rabbit-hole

echo "Rabbit Hole agent setup complete. First run scheduled for 5:30am Pacific."
