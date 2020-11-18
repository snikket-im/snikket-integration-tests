provider "aws" {
  version = "~> 3.0"
  region  = var.aws_region
}

provider "template" {
  version = "~> 2.2.0"
}
