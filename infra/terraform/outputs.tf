output "vpc_id" {
  description = "SupportFlow VPC ID"
  value       = aws_vpc.supportflow.id
}

output "public_subnet_id" {
  description = "SupportFlow public subnet ID"
  value       = aws_subnet.public.id
}

output "web_security_group_id" {
  description = "SupportFlow web security group ID"
  value       = aws_security_group.web.id
}