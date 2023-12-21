import json
from datetime import datetime


class Issue:
	def __init__(self, datetime: datetime, info: dict):
		self.datetime = datetime
		self.info = info
		self.event = json.loads(info["event"].replace("'", '"').replace('\n', r'\n').replace('\t', r'\t'))
		self.eventID = self.event["eventID"]

	def __hash__(self):
		return hash((self.eventID, self.info['issue']))
