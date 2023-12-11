import asyncio

from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, ContextTypes, CallbackQueryHandler
from multiprocessing import Queue
from model import *

import config, parser
import responce_controller as controller

users = []
bot: Bot
message_queue: Queue

issues: dict[str, Issue] = {}

keyboard = [[
	InlineKeyboardButton("✅ Пропустить ✅", callback_data="OK"),
	InlineKeyboardButton("❌ Удалить ❌", callback_data="BAN"),
]]


async def check_new_reports(context: CallbackContext):
	if not message_queue.empty():
		message = message_queue.get()
		issue = Issue(message["date"], message["data"])
		issues[issue.id] = issue
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
		issue.message = await bot.send_message(
			user,
			parser.parse_issue_text(issue),
			parse_mode='HTML',
			reply_markup=InlineKeyboardMarkup(keyboard)
		)
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
		match query.data:
			case "OK":
				await query.edit_message_text(parser.parse_deny(issue, query.from_user.full_name), parse_mode="HTML")
				# tasks.append(controller.deny_issue(issue))
			case "BAN":
				await query.edit_message_text(parser.parse_accept(issue, query.from_user.full_name), parse_mode="HTML")
				# tasks.append(controller.accept_issue(issue))
		await query.answer()
		del issues[issue_id]


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
