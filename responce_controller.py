from model import Issue

from firebase import delete_event

async def accept_issue(issue: Issue):
	delete_event(issue.eventID)


async def deny_issue(issue: Issue):
	...