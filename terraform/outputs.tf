output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.rabbit_hole.public_ip
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.rabbit_hole.id
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i your-key.pem ec2-user@${aws_instance.rabbit_hole.public_ip}"
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name (public briefing URL base)"
  value       = "https://${aws_cloudfront_distribution.rabbit_hole.domain_name}"
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.rabbit_hole.id
}
