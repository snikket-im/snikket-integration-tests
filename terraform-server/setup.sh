#!/bin/bash

DOMAIN="${tf_domain}"
ESCAPED_DOMAIN=$(echo "$DOMAIN" | lua -e 'print((io.read():gsub("%W", function (c) return ("%%%02x"):format(c:byte())end)))')
EMAIL="${tf_admin_email}"
CONFIG_SECRET="${tf_config_secret}"

if [[ "${tf_import_test_data}" == "true" ]]; then
	install -d "/var/lib/snikket/prosody/$ESCAPED_DOMAIN"
	wget https://prosody.im/files/prosody-test-data.tar.gz
	tar xzf prosody-test-data.tar.gz -C "/var/lib/snikket/prosody/$ESCAPED_DOMAIN"
fi

curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod a+x /usr/local/bin/docker-compose

git clone https://github.com/snikket-im/snikket-selfhosted /opt/snikket

cd /opt/snikket

tee docker-compose.override.yml <<EOF
---
services:
  snikket_portal:
    image: ${tf_container_repo}/snikket-web-portal:${tf_version}
  snikket_proxy:
    image: ${tf_container_repo}/snikket-web-proxy:${tf_version}
  snikket_certs:
    image: ${tf_container_repo}/snikket-cert-manager:${tf_version}
  snikket_server:
    image: ${tf_container_repo}/snikket:${tf_version}
EOF

tee snikket.conf <<EOF

# The primary domain of your Snikket instance
SNIKKET_DOMAIN=${tf_domain}

# An email address where the admin can be contacted
# (also used to register your Let's Encrypt account to obtain certificates)
SNIKKET_ADMIN_EMAIL=${tf_admin_email}

# Enable features used for integration testing
SNIKKET_TWEAK_TEST_MODE=1

EOF

# Install service to save/restore certificates
tee /etc/systemd/system/snikket-ci-certs.service <<EOF
[Unit]
Description=Back up/restore certificates to S3
DefaultDependencies=no
Requires=network-online.target network.target
Before=shutdown.target reboot.target halt.target

[Service]
Type=oneshot
KillMode=none
ExecStart=-/usr/bin/aws s3 sync "s3://${tf_certs_bucket}/${tf_domain}/" "/var/lib/snikket/letsencrypt/"
ExecStop=/usr/bin/aws s3 sync "/var/lib/snikket/letsencrypt/" "s3://${tf_certs_bucket}/${tf_domain}/"
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now snikket-ci-certs.service

# Sometimes the shutdown trick doesn't work, so run a sync in 5min
systemd-run --on-active=300 /usr/bin/aws s3 sync "/var/lib/snikket/letsencrypt/" "s3://${tf_certs_bucket}/${tf_domain}/"


if ! host "$DOMAIN"; then
	while sleep 15 && ! host "$DOMAIN"; do
		echo "Waiting for DNS ($DOMAIN)...";
	done
fi

docker-compose up -d

# Generate invite API key and publish it at the SECRET location
API_KEY=$(docker exec -i snikket bash -c "prosodyctl mod_invites_api $DOMAIN create")
echo "$API_KEY" | docker exec -i snikket-proxy bash -c "cat > /var/www/html/static/api-key-$CONFIG_SECRET"
