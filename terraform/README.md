# Terraform Setup for Rabbit Hole

This directory contains Terraform configuration to launch and configure the Rabbit Hole agent on EC2.

## Prerequisites

1. **AWS account** with credentials configured locally (`aws configure`)
2. **EC2 key pair** already created in AWS (e.g., `your-key.pem`)
3. **Terraform** installed (`brew install terraform` on Mac)
4. **GitHub repo** pushed and public (or update git clone URL in user_data.sh)
5. **Your public IP address** (for SSH security group — get from https://www.whatismyip.com/)

## Setup

1. Copy `terraform.tfvars.example` to `terraform.tfvars`:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` and fill in your values:
   - `key_pair_name` — name of your EC2 key pair in AWS
   - `ssh_access_cidr` — your IP in CIDR format (e.g., `203.0.113.42/32`) from whatismyip.com
   - `s3_bucket_name` — unique S3 bucket name (e.g., `rabbit-hole-briefings-yourname`)
   - `anthropic_api_key` — your Anthropic API key
   - `telegram_bot_token` — your Telegram bot token
   - `telegram_chat_id` — your Telegram chat ID

   (S3 bucket and CloudFront distribution will be created automatically)

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Review the plan:
   ```bash
   terraform plan
   ```

5. Apply:
   ```bash
   terraform apply
   ```

   Terraform will output the public IP and SSH command.

## After Launch

Once the instance is running, you can test it manually:

```bash
ssh -i your-key.pem ec2-user@<public-ip>
cd rabbit-hole
source venv/bin/activate
source .env
python3 generate.py --topic "Your test topic"
```

## Cron Job

The cron job is automatically set up by `user_data.sh` and runs daily at 7:30am UTC. Check the logs:

```bash
ssh -i your-key.pem ec2-user@<public-ip>
tail -f ~/rabbit-hole/logs/cron.log
```

## Cleanup

To destroy the instance:

```bash
terraform destroy
```

## Notes

- The `user_data.sh` script assumes your GitHub repo is public. Update the `git clone` URL if needed.
- Terraform state is stored locally. For team setups, use S3 backend.
- IAM policy allows full S3 access to your bucket. Lock it down further if desired.
