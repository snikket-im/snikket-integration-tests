#!/bin/bash

set -xeo pipefail

CONFIG_DIR="${CONFIG_DIR-/etc/snikket-integration-tests}"

echo "Shutting down..."

pushd terraform-server

terraform destroy \
  -auto-approve \
  -var-file="${CONFIG_DIR}/terraform-env.tfvars" \
  -var-file="${CONFIG_DIR}/terraform-server.tfvars" \
  -var "domain=${DOMAIN}" \
  -var "config_secret=n/a"

popd

test -f invites-api-key && rm invites-api-key
