#!/bin/bash

CONFIG_DIR="${CONFIG_DIR-/etc/snikket-integration-tests}"

if [[ "$#" != 1 ]]; then
	echo "Usage: $0 FILENAME"
	exit 1;
fi

SAUCELABS_CREDS=$(
	jq -r '.["saucelabs.user"]+":"+.["saucelabs.key"]' \
	"${CONFIG_DIR}/saucelabs-auth.json"
)

APP_LOCATION="payload=@$1"

curl -u "$SAUCELABS_CREDS" \
-X POST 'https://api.us-west-1.saucelabs.com/v1/storage/upload' \
-F "$APP_LOCATION" | jq .item.id
