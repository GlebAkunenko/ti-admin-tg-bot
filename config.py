import json

with open("config.json", 'r') as f:
	_d = json.load(f)
	token = _d['token']
	host = _d['host']
	port = _d['port']
	main_url = _d['main_url']