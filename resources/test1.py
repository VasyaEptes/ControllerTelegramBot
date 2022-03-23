from telegram.ext import Updater
import logging
# импортируем обработчик CommandHandler,
# который фильтрует сообщения с командами
from telegram.ext import CommandHandler
# импортируем обработчик `MessageHandler` и класс с фильтрами
from telegram.ext import MessageHandler, Filters


TOKEN = "2137599085:AAGh8yURj1mCWTwFzPly1agq3tOwuPYAY74"
CHAT_ID = -721779109
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    # `bot.send_message` это метод Telegram API
    # `update.effective_chat.id` - определяем `id` чата,
    # откуда прилетело сообщение
    print(update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I'm a bot, please talk to me!")


def _help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Ничем не могу помочь!")


# говорим обработчику, если увидишь команду `/start`,
# то вызови функцию `start()`
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', _help)
# добавляем этот обработчик в `dispatcher`
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
# говорим экземпляру `Updater`,
# слушай сервера Telegram.
updater.start_polling()


# функция обратного вызова
def echo(update, context):
    # добавим в начало полученного сообщения строку 'ECHO: '
    text = 'ECHO: ' + update.message.text
    print(update.effective_chat.id)
    # `update.effective_chat.id` - определяем `id` чата,
    # откуда прилетело сообщение
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


# говорим обработчику `MessageHandler`, если увидишь текстовое
# сообщение (фильтр `Filters.text`)  и это будет не команда
# (фильтр ~Filters.command), то вызови функцию `echo()`
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
# регистрируем обработчик `echo_handler` в экземпляре `dispatcher`
dispatcher.add_handler(echo_handler)




