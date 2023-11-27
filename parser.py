from model import Issue
import json
from datetime import datetime

def format_field(string: str, key: str) -> str:
	return string if string != "" else f"{key} отсутствует"


def format_date(dt: datetime) -> str:
	return f"{dt.date().day}.{dt.date().month} {dt.time().hour}:{dt.time().minute}"


def parse_issue_text(issue: Issue) -> str:
	data: dict[str] = issue.info
	with open('test.txt', 'w', encoding='utf-8') as f:
		json.dump(data, f)
	sender = data['sender']
	date = issue.id
	issue = data['issue']
	event = json.loads(data['event'].replace("'", '"').replace('\n', r'\n').replace('\t', r'\t'))
	f = format_field
	return f"""
Событие номер <code>{event['eventID']}</code>
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
