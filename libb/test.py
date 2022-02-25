import telegram

TOKEN = "5281042924:AAEGuj3sddLcWniZdZJo8NL5Y09rFbDGDiU"
bot = telegram.Bot(token=TOKEN)
print(bot.get_me())
updates = bot.get_updates()
# print([upd.message.text for upd in updates])
chat_id = bot.get_updates()[-1].message.chat_id
print(chat_id)
bot.send_message(chat_id=f'{chat_id}@Web3Space_bot', text="ok")
