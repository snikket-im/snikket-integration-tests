#!/bin/bash

set -xeo pipefail

TEST_NAME="${1-dev}"

CONFIG_DIR="${CONFIG_DIR-/etc/snikket-integration-tests}"
DOMAIN="${TEST_NAME}.test.snikket.dev"
INVITES_API_KEY=$(cat invites-api-key)

ALL_OK=1
for device_config in devices/*.json; do
	if ! ./tests/snikket-android.py \
	  --driver-url=https://hub-cloud.browserstack.com/wd/hub \
	  --caps-file="${CONFIG_DIR}/browserstack-auth.json" \
	  --caps-file="$device_config" \
	  --cap browserstack.appium_version=1.17.0 \
	  --cap project="$(basename "$PWD")" \
	  --cap build="Build $BUILD_NUM" \
	  --cap name="$(basename "${device_config%.json}")" \
	  --cap app="SnikketFDroid" \
	  "$DOMAIN" "$INVITES_API_KEY"; then
		ALL_OK=0;
	fi
done

if [[ "$ALL_OK" != "1" ]]; then
	echo "FAIL";
	exit 1;
fi

echo "PASS"
exit 0;
