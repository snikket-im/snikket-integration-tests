data "aws_caller_identity" "current" {}

data "aws_route53_zone" "selected" {
  name = "${var.dns_zone}."
}

resource "aws_s3_bucket" "snikket_certs" {
  bucket = var.certs_bucket
  acl    = "private"

  lifecycle_rule {
    enabled = true
    expiration {
      days = 60
    }
  }
}

resource "aws_iam_role" "snikket_ci_runner" {
  name = "snikket_ci_runner"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "snikket_ci_runner" {
  role       = aws_iam_role.snikket_ci_runner.name
  policy_arn = aws_iam_policy.snikket_ci.arn
}

resource "aws_iam_instance_profile" "snikket_ci_runner" {
  name = "snikket_ci_runner"
  role = aws_iam_role.snikket_ci_runner.name
}

resource "aws_iam_policy" "snikket_ci" {
  name        = "snikket-integration-tests"
  path        = "/"
  description = "Permissions required to successfully run the Snikket end-to-end integration tests"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:RevokeSecurityGroupIngress",
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:TerminateInstances",
                "ec2:CreateSecurityGroup",
                "ec2:CreateTags",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:DeleteSecurityGroup",
                "ec2:RunInstances"
            ],
            "Resource": [
                "arn:aws:ec2:*:${data.aws_caller_identity.current.account_id}:subnet/*",
                "arn:aws:ec2:*:${data.aws_caller_identity.current.account_id}:security-group/*",
                "arn:aws:ec2:*:${data.aws_caller_identity.current.account_id}:network-interface/*",
                "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:vpc/${var.vpc_id}",
                "arn:aws:ec2:*:${data.aws_caller_identity.current.account_id}:volume/*",
                "arn:aws:ec2:*:${data.aws_caller_identity.current.account_id}:instance/*",
                "arn:aws:ec2:${var.aws_region}:${data.aws_caller_identity.current.account_id}:key-pair/${var.key_name}",
                "arn:aws:ec2:*::image/*"
            ],
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "${var.allowed_ip}"
                }
            }
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "ec2:DescribeNetworkInterfaces",
            "Resource": "*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "${var.allowed_ip}"
                }
            }
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeImages",
                "ec2:DescribeInstances",
                "ec2:DescribeTags",
                "ec2:DescribeVpcs",
                "ec2:DescribeInstanceAttribute",
                "ec2:DescribeVolumes",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeSubnets",
                "ec2:DescribeVpcAttribute",
                "ec2:DescribeRouteTables",
                "ec2:DescribeInstanceCreditSpecifications",
                "ec2:DescribeSecurityGroups"
            ],
            "Resource": "*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "${var.allowed_ip}"
                }
            }
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": [
                "route53:GetChange",
                "route53:GetHostedZone",
                "route53:ChangeResourceRecordSets",
                "s3:PutObjectVersionTagging",
                "s3:ListBucket",
                "route53:ListTagsForResource",
                "s3:PutObject",
                "s3:GetObjectAcl",
                "s3:GetObject",
                "iam:PassRole",
                "s3:PutObjectRetention",
                "s3:PutObjectVersionAcl",
                "route53:ListResourceRecordSets",
                "s3:PutObjectTagging",
                "s3:DeleteObject",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${aws_iam_role.snikket_ci_runner.name}",
                "arn:aws:route53:::change/*",
                "arn:aws:route53:::hostedzone/${data.aws_route53_zone.selected.zone_id}",
                "arn:aws:s3:::${var.certs_bucket}/*",
                "arn:aws:s3:::${var.certs_bucket}"
            ]
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": "route53:ListHostedZones",
            "Resource": "*"
        }
    ]
}
EOF
}
