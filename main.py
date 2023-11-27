from multiprocessing import Process, Queue
# from threading import Thread
from bot import run_bot
from server import run_flask

if __name__ == "__main__":

	messages_queue = Queue()

	flask_process = Process(target=run_flask, args=(messages_queue,))
	bot_process = Process(target=run_bot, args=(messages_queue,))

	flask_process.start()
	bot_process.start()

	flask_process.join()
	bot_process.join()

	# queue = []
	#
	# flask_thread = Thread(target=run_flask, args=(queue, ))
	# bot_thread = Thread(target=run_bot, args=(queue, ))
	#
	# flask_thread.start()
	# bot_thread.start()
	#
	# flask_thread.join()
	# bot_thread.join()
