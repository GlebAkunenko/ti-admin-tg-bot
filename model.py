import json
from datetime import datetime
from enum import Enum

class IssueStatus(Enum):
	consideration = 0,
	accept = 1,
	denied = 2


class Issue:
	def __init__(self, datetime: datetime, info: dict):
		self.datetime = datetime
		self.info = info
		self.event = json.loads(info["event"].replace("'", '"').replace('\n', r'\n').replace('\t', r'\t'))
		self.eventID = self.event["eventID"]
		self.status = IssueStatus.consideration
		self.message = None
		self.id = str(hash(datetime) + 2 * hash(self.eventID))