from datetime import datetime
from enum import Enum

class IssueStatus(Enum):
	consideration = 0,
	accept = 1,
	denied = 2


class Issue:
	def __init__(self, id: datetime, info: str):
		self.id = id
		self.info = info
		self.status = IssueStatus.consideration