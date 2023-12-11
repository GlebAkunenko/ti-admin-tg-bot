import asyncio

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes, CallbackQueryHandler
from multiprocessing import Queue
from model import *

import config, parser
import responce_controller as controller

users = []
bot: Bot
message_queue: Queue

class Event:
	def __init__(self, id: str):
		self.id = id
		self.issues = []
		self.user_issue_message: dict[tuple, list[Message]] = {}

	def __hash__(self):
		return hash(self.id)

	async def on_delete(self, issue: Issue, sender: str):
		tasks = []
		for user, issue in self.user_issue_message:
			for message in self.user_issue_message[(user, issue)]:
				tasks.append(asyncio.create_task(bot.edit_message_text(
					parser.parse_accept(issue, sender),
					user,
					message.message_id,
					parse_mode='HTML',
					reply_markup=None
				)))
		await asyncio.wait(tasks)

	async def on_skip_issue(self, issue, sender: str):
		tasks = []
		for user, issue in self.user_issue_message:
			for message in self.user_issue_message[(user, issue)]:
				tasks.append(asyncio.create_task(bot.edit_message_text(
					parser.parse_deny(issue, sender),
					user,
					message.message_id,
					parse_mode='HTML',
					reply_markup=None
				)))
		await asyncio.wait(tasks)


events: dict[str, Event] = {}
issues: dict[str, Issue] = {}

keyboard = [[
	InlineKeyboardButton("✅ Пропустить ✅", callback_data="OK"),
	InlineKeyboardButton("❌ Удалить ❌", callback_data="BAN"),
]]


async def check_new_reports(context: CallbackContext):
	if not message_queue.empty():
		message = message_queue.get()
		issue = Issue(message["date"], message["data"])
		if issue.eventID not in events:
			events[issue.eventID] = Event(issue.eventID)
		events[issue.eventID].issues.append(issue)
		issues[issue.eventID] = issue
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
	async def send(user, issue: Issue):
		message = await bot.send_message(
			user,
			parser.parse_issue_text(issue),
			parse_mode='HTML',
			reply_markup=InlineKeyboardMarkup(keyboard)
		)
		l = events[issue.eventID].user_issue_message
		if not l.get((user, issue)):
			l[user, issue] = []
		l[user, issue].append(message)
	if len(users) > 0:
		tasks = []
		for user in users:
			tasks.append(asyncio.create_task(send(user, issue)))
		await asyncio.wait(tasks)


async def on_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	query = update.callback_query
	issue_id = query.message.text.split('\n')[0]
	if issue_id not in issues:
		await query.answer("Ошибка")
	else:
		issue = issues[issue_id]
		event = events[issue.eventID]
		match query.data:
			case "OK":
				await event.on_skip_issue(issue, query.from_user.full_name)
				await controller.deny_issue(issue)
				del issues[issue_id]
				event.issues.remove(issue)
			case "BAN":
				await event.on_delete(issue, query.from_user.full_name)
				await controller.accept_issue(issue)
				del events[issue.eventID]
				del issues[issue_id]
		await query.answer()


def run_bot(mq):
	global message_queue
	message_queue = mq
	application = Application.builder().token(config.token).build()

	# on different commands - answer in Telegram
	application.add_handler(CommandHandler("start", start))
	application.add_handler(CommandHandler("subscribe", subscribe))
	application.add_handler(CommandHandler("unsubscribe", unsubscribe))
	application.add_handler(CallbackQueryHandler(on_button_click))

	global bot
	bot = application.bot

	application.job_queue.run_repeating(check_new_reports, 1)

	application.run_polling(allowed_updates=Update.ALL_TYPES)
