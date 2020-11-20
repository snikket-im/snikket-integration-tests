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

mkdir /etc/snikket
cd /etc/snikket

tee docker-compose.yml <<EOF
---
version: "3.3"

services:
  snikket_web:
    image: ${tf_container_repo}/snikket-web-proxy:${tf_version}
    env_file: snikket.conf
    network_mode: host
    volumes:
      - "/var/lib/snikket:/snikket"
      - acme_challenges:/usr/share/nginx/html/.well-known/acme-challenge
    restart: "unless-stopped"
  snikket_certs:
    image: ${tf_container_repo}/snikket-cert-manager:${tf_version}
    env_file: snikket.conf
    volumes:
      - "/var/lib/snikket:/snikket"
      - acme_challenges:/var/www/.well-known/acme-challenge
    restart: "unless-stopped"
  snikket_server:
    container_name: snikket
    image: ${tf_container_repo}/snikket:${tf_version}
    network_mode: host
    volumes:
      - "/var/lib/snikket:/snikket"
    env_file: snikket.conf
    restart: "unless-stopped"

volumes:
  acme_challenges:

EOF

tee snikket.conf <<EOF

# The primary domain of your Snikket instance
SNIKKET_DOMAIN=${tf_domain}

# An email address where the admin can be contacted
# (also used to register your Let's Encrypt account to obtain certificates)
SNIKKET_ADMIN_EMAIL=${tf_admin_email}

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
docker exec -t snikket bash -c "prosodyctl mod_invites_api $DOMAIN create > /var/www/api-key-$CONFIG_SECRET"
