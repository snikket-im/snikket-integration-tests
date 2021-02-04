import random, string, re
from collections import namedtuple
import requests
try:
    import json
except ImportError:
    import simplejson as json

Account = namedtuple('Account', 'username jid password')

def add_caps_from_file(current_caps, caps_filename):
	with open(caps_filename, 'r') as caps_file:
		new_caps = json.loads(caps_file.read())
		for cap_name in new_caps:
			current_caps[cap_name] = new_caps[cap_name]

def get_caps_from_file(caps_filename):
	with open(caps_filename, 'r') as caps_file:
		return json.loads(caps_file.read())

def randomword(length):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))

def generate_random_username(prefix="auto-"):
	return prefix + randomword(8)

def generate_random_password():
	return randomword(12)

def get_new_invite_url(domain, invite_key):
	r = requests.get("https://%s/invites_api?key=%s" % (domain, invite_key))
	print("https://%s/invites_api?key=%s" % (domain, invite_key))
	if r.status_code != 201:
		print(r.status_code)
	assert r.status_code == 201
	return r.headers["location"]

def get_new_invite_token(domain, invite_key):
	return get_new_invite_url(domain, invite_key).split("/")[4]

def get_new_invite_uri(domain, invite_key):
	return "xmpp:%s?register;preauth=%s" % (domain, get_new_invite_token(domain, invite_key))

def get_new_account(username, domain, invite_key):
	password = generate_random_password()
	url = get_new_invite_url(domain, invite_key) + '/register'
	invite_page = requests.get(url)
	csrf_token = re.search(
		r'name="csrf_token" type="hidden" value="([^"]*)"',
		invite_page.text,
		re.M
	).group(1)
	token = url.split("/")[4]
	r = requests.post(url, cookies=invite_page.cookies, data = {
		'csrf_token': csrf_token,
		'localpart': username,
		'password': password,
		'password_confirm': password
	})
	assert r.status_code == 200
	return Account(username, username+"@"+domain, password)

