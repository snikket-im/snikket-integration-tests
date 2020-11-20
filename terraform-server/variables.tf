variable "domain" {
  description = "The base domain of the service"
}

variable "dns_zone" {
  description = "The Route53 zone to add records to"
}

variable "admin_email" {
  description = "Valid email address for the admin of the service"
}

variable "key_name" {
  description = "Name of an EC2 keypair to allow SSH to the instance"
}

variable "snikket_version" {
  description = "The Snikket branch/tag to deploy"
  default     = "dev"
}

variable "snikket_container_repo" {
  description = "The Snikket container repo to deploy"
  default     = "snikket"
}

variable "import_test_data" {
  description = "Set to 'true' to bootstrap the server with test accounts"
  default     = "false"
}

variable "aws_region" {
  description = "AWS region to deploy to"
}

variable "aws_zone" {
  description = "AWS availability zone to deploy to"
}

variable "vpc_id" {
  description = "Identifier of the VPC to deploy to"
}

variable "config_secret" {
  description = "Secret key used to initialize e.g. API keys"
}

variable "certs_bucket" {
  description = "Name of an S3 bucket where certificates are backed up to"
}

variable "allowed_ip" {
  description = "IP address to restrict SSH to"
}
