import asyncio

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext
from multiprocessing import Queue
from model import *

import config, parser

users = []
bot: Bot
message_queue: Queue

issues: list[Issue] = []

async def check_new_reports(context: CallbackContext):
	if not message_queue.empty():
		message = message_queue.get()
		issue = Issue(message["date"], message["data"])
		await notify_users(issue)


async def start(update: Update, context: CallbackContext):
	await bot.send_message(update.message.from_user.id, "Hi!")


async def subscribe(update: Update, context: CallbackContext):
	user = update.message.from_user.id
	if user not in users:
		users.append(user)
		await bot.send_message(user, "Подписка оформлена")
	else:
		await bot.send_message(user, "Ты уже подписчик")


async def unsubscribe(update: Update, context: CallbackContext):
	user = update.message.from_user.id
	if user in users:
		users.remove(user)
		await bot.send_message(user, "Подписка отменена")
	else:
		await bot.send_message(user, "Ты не подписчик")


async def notify_users(issue: Issue):
	if len(users) > 0:
		tasks = []
		for user in users:
			tasks.append(asyncio.create_task(bot.send_message(
				user,
				parser.parse_issue_text(issue),
				parse_mode='HTML'
			)))
		await asyncio.wait(tasks)


def run_bot(mq):
	global message_queue
	message_queue = mq
	application = Application.builder().token(config.token).build()

	# on different commands - answer in Telegram
	application.add_handler(CommandHandler("start", start))
	application.add_handler(CommandHandler("subscribe", subscribe))
	application.add_handler(CommandHandler("unsubscribe", unsubscribe))

	global bot
	bot = application.bot

	application.job_queue.run_repeating(check_new_reports, 1)

	application.run_polling(allowed_updates=Update.ALL_TYPES)
