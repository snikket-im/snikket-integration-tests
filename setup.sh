#!/bin/bash

set -xeo pipefail

TEST_NAME="${1-dev}"

CONFIG_DIR="${CONFIG_DIR-/etc/snikket-integration-tests}"
DOMAIN="${TEST_NAME}.test.snikket.dev"
CONFIG_SECRET=$(uuidgen)

echo "Setting up..."

pushd terraform-server

terraform init

terraform apply \
  -auto-approve \
  -var-file="${CONFIG_DIR}/terraform-env.tfvars" \
  -var-file="${CONFIG_DIR}/terraform-server.tfvars" \
  -var "domain=${DOMAIN}" \
  -var "config_secret=${CONFIG_SECRET}"

popd

while sleep 15 && ! curl -so/dev/null "https://${DOMAIN}/"; do
  echo "Waiting for Snikket to become available...";
done

INVITES_API_KEY=$(curl -s "https://${DOMAIN}/api-key-${CONFIG_SECRET}")

echo "$INVITES_API_KEY" > invites-api-key
