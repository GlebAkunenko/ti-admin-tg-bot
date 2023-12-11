from model import Issue
import json
from datetime import datetime

def format_field(string: str, key: str) -> str:
	return string if string != "" else f"{key} отсутствует"


def format_date(dt: datetime) -> str:
	return f"{dt.date().day}.{dt.date().month} {dt.time().hour}:{dt.time().minute}"


def parse_issue_text(issue: Issue) -> str:
	sender = issue.info['sender']
	date = issue.datetime
	event = issue.event
	issue = issue.info['issue']
	f = format_field

	# WARING. Button callback query matches with event id in first line of message!
	return f"""
<code>{event['eventID']}</code>

<b>{event['title']}</b>

<b>Жалоба:</b> <i>{issue}</i>
от {sender}
{format_date(date)}

<i>Описание:</i>

{f(event['fullDescription'], "Полное описание")}

{f(event['briefDescription'], "Краткое описание")}

<i>Адрес:</i>

{f(event['address'], "Адрес")}

{f(event['addressInfo'], "Информация по адресу")}
"""


def parse_deny(issue: Issue, admin_id: str) -> str:
	body = parse_issue_text(issue)
	return body + "\n\n" + "✅ Жалоба игнорирована ✅" + "\n" + f"<i>Модератор: {admin_id}</i>"


def parse_accept(issue: Issue, admin_id: str) -> str:
	body = parse_issue_text(issue)
	return body + "\n\n" + "❌ Пост заблокирован ❌" + "\n" + f"<i>Модератор: {admin_id}</i>"