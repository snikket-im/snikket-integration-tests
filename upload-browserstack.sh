#!/bin/bash

CONFIG_DIR="${CONFIG_DIR-/etc/snikket-integration-tests}"

if [[ "$#" != 2 ]]; then
	echo "Usage: $0 APP_NAME FILE/URL"
	exit 1;
fi

BROWSERSTACK_CREDS=$(
	jq -r '.["browserstack.user"]+":"+.["browserstack.key"]' \
	"${CONFIG_DIR}/browserstack-auth.json"
)

case "$2" in
"https://"*)
	APP_LOCATION="url=$2"
;;
*)
	APP_LOCATION="file=@$2"
;;
esac

curl -u "$BROWSERSTACK_CREDS" \
-X POST "https://api-cloud.browserstack.com/app-automate/upload" \
-F "$APP_LOCATION" \
-F "custom_id=$1"
