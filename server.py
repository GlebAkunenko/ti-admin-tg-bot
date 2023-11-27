import asyncio
from flask import Flask, request
import config
from multiprocessing import Queue
import parser
from datetime import datetime

app = Flask(__name__)
users = []
messages_queue: Queue
# messages_queue: list


def send_message(message):
	messages_queue.put({"date": datetime.now(), "data": message})
	# messages_queue.append(message)


@app.route(config.main_url, methods=['POST'])
async def get_report():
	# data = request.get_json()
	# Отправка сообщения пользователю
	send_message(parser.parse_json(request.get_json()))
	return "OK"


def run_flask(mq):
	global messages_queue
	messages_queue = mq
	app.run(host=config.host, port=config.port, debug=False)