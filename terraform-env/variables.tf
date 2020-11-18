variable "aws_region" {
  default = "eu-west-1"
}

variable "certs_bucket" {
  description = "S3 bucket for certificate backups"
}

variable "allowed_ip" {
  description = "IP address permitted to provision test servers"
}

variable "dns_zone" {
  description = "DNS zone to allow creation of records"
}

variable "vpc_id" {
  description = "Identifier of the VPC to deploy to"
}

variable "key_name" {
  description = "Name of an EC2 keypair to allow SSH to the instance"
}
