# from pyrogram import Client
import asyncio


QUERY_ARRAY = ["Фонды", "Список фондов", "Инвестиции", "Категории", "Аналитика", "Статистика рынка", "Категории",
               "События", "Новые токены", "Эмиссия", "Капитализация", "🔝 ТОП 100", "Техподдержка", "Инструкция",
               "Написать", "Политика", "Оферта", "Назад", "Аккаунт", "Инфо", "Настройки", "Язык", "Аккаунт",
               "Избранное", "Портфель", "Оплата", "Сигналы", "Сигналы(Инфо)", "Назад"]
QUERY_BRANCH_TEST = [["Настройки", "Капитализация"], ["События"]]


async def messanger(app):
    async with app.client as cli:
    # async with Client("my_account", api_id, api_hash) as cli:
        while True:
            for n, word in enumerate(QUERY_ARRAY):
                request_message = word
                print(n, request_message)
                await cli.send_message(app.bot_name, request_message)
                while app.status_next is False:
                    await asyncio.sleep(1)
                app.status_next = False
            print('the cycle has been completed successfully')
            if app.status_work is True:
                app.sms(f'Бот {app.config["my_bot_name"]}: Успешно пройден весь цикл запросов. Ошибок не обнаружено')
            else:
                app.sms(f'Бот {app.config["my_bot_name"]}: Успешно пройден весь цикл запросов. Есть ошибки (см. error.log')