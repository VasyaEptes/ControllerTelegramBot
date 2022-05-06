# from pyrogram import Client
import asyncio


QUERY_ARRAY = ["Фонды", "🔝 ТОП 100", "Список фондов", "Инвестиции", "Категории", "Аналитика", "Статистика рынка",
               "События", "Новые токены", "Эмиссия", "Капитализация", "Техподдержка", "Инструкция", "Категории",
               "Написать", "Политика", "Оферта", "Назад", "Аккаунт", "Инфо", "Настройки", "Язык", "Аккаунт",
               "Избранное", "Портфель", "Оплата", "Сигналы", "Сигналы(Инфо)", "Назад"]
QUERY_BRANCH_TEST = [["Настройки", "Капитализация"], ["События"]]


async def messanger(app):
    async with app.client as client:
    # async with Client("my_account", api_id, api_hash) as cli:
        while True:
            for n, word in enumerate(QUERY_ARRAY):
                request_message = word
                print(n, request_message)
                app.seq = request_message
                await client.send_message(app.bot_name, request_message)
                app.status_next = False
                while app.status_next is False:
                    await asyncio.sleep(0.1)
            print('the cycle has been completed successfully')
            if app.status_work is True:
                app.sms(f'Бот {app.config["my_bot_name"]}: Успешно пройден весь цикл запросов. Ошибок не обнаружено')
            else:
                app.sms(f'Бот {app.config["my_bot_name"]}: Успешно пройден весь цикл запросов. Есть ошибки (см. error.log')
            app.status_next = True
            app.waiting = True
            print('сплю')
            await asyncio.sleep(60*10)
            app.waiting = False
            app.status_work = True

