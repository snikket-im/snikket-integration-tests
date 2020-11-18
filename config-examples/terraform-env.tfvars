# The AWS region to operate in
aws_region = "eu-west-1"

# The VPC id that resources will be deployed to
vpc_id     = "vpc-abcdef123"

# The zone name that DNS records will be created in
dns_zone    = "test.example.com"

# The S3 bucket name where certificates will be stored
# between test runs
certs_bucket = "my-certs-bucket"

# The name of a keypair in AWS EC2 that will be configured
# on the server. The tests do not SSH into the server, so
# the private key does not need to be available to them.
key_name    = "my-keypair"

# The IP address that certain AWS API calls will be restricted
# to. An additional layer of security in case access keys leak.
# Note that not all API calls are IP-restricted.
allowed_ip = "aaa.bbb.ccc.ddd"
