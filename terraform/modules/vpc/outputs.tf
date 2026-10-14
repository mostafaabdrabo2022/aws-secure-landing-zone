output "vpc_id" {
  value       = aws_vpc.this.id
  description = "The ID of the VPC"
}

output "public_subnet_id" {
  value       = aws_subnet.public.id
  description = "The ID of the Public Subnet"
}

output "private_subnet_id" {
  value       = aws_subnet.private.id
  description = "The ID of the Private Subnet"
}