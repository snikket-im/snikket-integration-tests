#!/bin/bash

set -eo pipefail

CONFIG_DIR="${CONFIG_DIR-/etc/snikket-integration-tests}"
DOMAIN="${DOMAIN-dev.test.snikket.dev}"
INVITES_API_KEY=$(cat invites-api-key)

ALL_OK=1

echo "Running tests..."
if ! ./tests/snikket-e2e.py \
  --saucelabs-config="${CONFIG_DIR}/saucelabs-auth.json" \
  --browserstack-config="${CONFIG_DIR}/browserstack-auth.json" \
  --cap browserstack.appium_version=1.17.0 \
  --cap project="${BUILD_PROJECT-$(basename "$PWD")}" \
  --cap build="Build $BUILD_NUM" \
  --cap name="Snikket end-to-end test (iOS)" \
  --cap app="${BUILD_APP_ID-SnikketFDroid}" \
  "$DOMAIN" "$INVITES_API_KEY"; then
	ALL_OK=0;
fi

if [[ "$ALL_OK" != "1" ]]; then
	echo "FAIL";
	exit 1;
fi

echo "PASS"
exit 0;
