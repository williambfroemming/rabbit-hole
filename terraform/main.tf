terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Get default VPC and subnet
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_caller_identity" "current" {}

# Security group for SSH access
resource "aws_security_group" "rabbit_hole" {
  name        = "rabbit-hole-sg"
  description = "Security group for Rabbit Hole agent"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_access_cidr]
    description = "SSH access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "rabbit-hole"
  }
}

# IAM role for EC2 to write to S3
resource "aws_iam_role" "rabbit_hole" {
  name = "rabbit-hole-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for S3 access
resource "aws_iam_role_policy" "rabbit_hole_s3" {
  name = "rabbit-hole-s3"
  role = aws_iam_role.rabbit_hole.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.rabbit_hole.arn,
          "${aws_s3_bucket.rabbit_hole.arn}/*"
        ]
      }
    ]
  })
}

# IAM instance profile
resource "aws_iam_instance_profile" "rabbit_hole" {
  name = "rabbit-hole-profile"
  role = aws_iam_role.rabbit_hole.name
}

# EC2 instance
resource "aws_instance" "rabbit_hole" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  iam_instance_profile   = aws_iam_instance_profile.rabbit_hole.name
  vpc_security_group_ids = [aws_security_group.rabbit_hole.id]
  subnet_id              = data.aws_subnets.default.ids[0]
  associate_public_ip_address = true

  tags = {
    Name = "rabbit-hole-agent"
  }

  # Optional: add user data to auto-install deps
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    s3_bucket        = aws_s3_bucket.rabbit_hole.id
    cloudfront_base  = "https://${aws_cloudfront_distribution.rabbit_hole.domain_name}"
    telegram_token   = var.telegram_bot_token
    telegram_chat_id = var.telegram_chat_id
    api_key          = var.anthropic_api_key
  }))
}

# S3 bucket for briefings
resource "aws_s3_bucket" "rabbit_hole" {
  bucket = var.s3_bucket_name

  tags = {
    Name = "rabbit-hole-briefings"
  }
}

# CloudFront will serve the bucket (no public policy needed)

# Origin Access Control for CloudFront to access S3
resource "aws_cloudfront_origin_access_control" "rabbit_hole" {
  name                              = "rabbit-hole-oac"
  description                       = "OAC for Rabbit Hole S3"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# Bucket policy allowing CloudFront OAC to read
resource "aws_s3_bucket_policy" "rabbit_hole" {
  bucket = aws_s3_bucket.rabbit_hole.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontOAC"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.rabbit_hole.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/${aws_cloudfront_distribution.rabbit_hole.id}"
          }
        }
      }
    ]
  })
}

# CloudFront distribution for S3
resource "aws_cloudfront_distribution" "rabbit_hole" {
  origin {
    domain_name            = aws_s3_bucket.rabbit_hole.bucket_regional_domain_name
    origin_id              = "S3Origin"
    origin_access_control_id = aws_cloudfront_origin_access_control.rabbit_hole.id
  }

  enabled = true
  is_ipv6_enabled = true

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Origin"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "rabbit-hole"
  }
}

# Get latest Amazon Linux 2 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}
