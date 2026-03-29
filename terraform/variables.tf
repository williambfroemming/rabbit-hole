variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_pair_name" {
  description = "Name of the SSH key pair (must already exist in AWS)"
  type        = string
}

variable "ssh_access_cidr" {
  description = "CIDR block for SSH access (your IP/32)"
  type        = string
  default     = "0.0.0.0/0" # Change this to your IP for security
}

variable "s3_bucket_name" {
  description = "S3 bucket name (will be created automatically)"
  type        = string
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}

variable "telegram_bot_token" {
  description = "Telegram bot token"
  type        = string
  sensitive   = true
}

variable "telegram_chat_id" {
  description = "Telegram chat ID"
  type        = string
  sensitive   = true
}
