import asyncio
from telethon import errors
import time

from telethon import TelegramClient, events
t = 0
n = 0
request_message = ''


QUERY_BRANCH_1 = ["Фонды", "Список фондов", "Инвестиции", "Категории", "Назад"]
QUERY_BRANCH_2 = ["Аналитика", "Статистика рынка", "🔝 ТОП 100", "Категории", "События", "Новые токены", "Эмиссия",
                  "Капитализация", "Назад"]
QUERY_BRANCH_3 = ["Техподдержка", "Инструкция", "Написать", "Политика", "Оферта", "Назад"]
QUERY_BRANCH_4 = ["Аккаунт", "Инфо", "Настройки", "Язык", "Аккаунт", "Избранное", "Портфель", "Оплата", "Сигналы",
                  "Сигналы(Инфо)", "Назад"]
QUERY_ARRAY = [QUERY_BRANCH_1, QUERY_BRANCH_2, QUERY_BRANCH_3]
QUERY_BRANCH_TEST = [["🔝 ТОП 100"]]


async def run(app):
    global n
    '''Создание клиента'''
    client = TelegramClient('anon', app.app_id, app.app_hash)
    """Создание событий для постоянного мониторинга сообщений"""
    @client.on(events.NewMessage(chats=(app.bot_name)))
    async def normal_handler(event):
        global t, request_message
        """Получение ответа"""
        # response = event.message.to_dict()
        sender = await event.get_sender()
        response = await client.get_messages(sender.username)
        # print(response)
        from_id = None
        """Получаем id сообщения"""
        if response[-1].to_dict().get('peer_id') is not None:
            from_id = response[-1].to_dict().get('peer_id').get('user_id')
        """Получаем ссылку из сообщения. если она есть"""
        url = ''
        if response[-1].to_dict().get('entities') is not None and response[-1].to_dict().get('entities') != []:
            url = response[-1].to_dict().get('entities').get('url')
        """Считаем время ответа"""
        t = (time.time()) - t
        """Забираем сообщения из ответа"""
        response_message = response[-1].to_dict()['message']
        print(response_message, url)
        client_id = app.config['telegram_client']['id']
        """Проверяем, что сообщение пришло от бота web3space и время ответа """
        if from_id != client_id and t > 1:
            app.log_error.error(f'Request: {request_message}, From_id: {from_id}, Error: timeout error')
        else:
            app.log_debug.debug(f'Request: {request_message}, From_id: {from_id}, Execution time: {t}')
        await response_processing(app=app, response=response_message, client=client)
        """Проверяем ответ на наличие нужного заголовка и запускаем циклы нажатия на кнопки"""
        if '🏆 🔝 Топ 100' in response_message:
            pass
            await click_loop(app=app, client=client, event=event, text='▶', count_check_string=4)
            await click_loop(app=app, client=client, event=event, text='◀', count_check_string=4)
            await click_one(app=app, client=client, event=event, text='Сравнить все')
            await click_loop(app=app, client=client, event=event, text='▶', count_check_string=4)
            await click_loop(app=app, client=client, event=event, text='◀', count_check_string=4)
        if 'Фонды 7дн 30дн Баллы Тикер' in response_message or 'Фонды сегодня' in response_message or\
                '📶 Категории' in response_message or 'Топ токенов с эмиссией 100-90 %' in response_message:
            await click_loop(app=app, client=client, event=event, text='▶', count_check_string=4)
            await click_loop(app=app, client=client, event=event, text='◀', count_check_string=4)
        if 'Топ токенов с капитализацией' in response_message:
            await click_loop(app=app, client=client, event=event, text='▶', count_check_string=5)
            await click_loop(app=app, client=client, event=event, text='◀', count_check_string=5)
        if '🏆 🔝 События' in response_message or '🏆 🔝 Топ 10 новых токенов 30 дней' in response_message:
            await click_loop(app=app, client=client, event=event, text='▶', count_check_string=2)
            await click_loop(app=app, client=client, event=event, text='◀', count_check_string=2)
    """Запускаем клиент"""
    await client.start()
    """В цикле посылаем команды из массива команд"""
    for query in QUERY_ARRAY:
        while n < len(query):
            global request_message
            request_message = query[n]
            print(n, request_message)
            await send_one_message(app=app, client=client, message=query[n])
            await asyncio.sleep(5)
    """Клиент продолжит работы. пока не будет остановлен вручную"""
    await client.run_until_disconnected()


async def click_loop(app, client, event, text, count_check_string):
    sender = await event.get_sender()
    messages = await client.get_messages(sender.username)
    first_last_coin_of_message = ''
    index = 0
    while True:
        t_start = (time.time())
        await messages[0].click(text=text)
        await asyncio.sleep(1)
        messages = await client.get_messages(sender.username)
        t_finish = (time.time())
        if t_finish - t_start > 2:
            app.log_error.error(f'Click button: {text}, Execution time: {t_finish - t_start}, Error: timeout error')
        else:
            app.log_debug.debug(f'Click button: {text}, Execution time: {t_finish - t_start}')
        message = messages[-1].to_dict().get('message')
        last_coin_of_message = message.split('\n')[count_check_string]
        print(message.split('\n'))
        await asyncio.sleep(2)
        if last_coin_of_message == first_last_coin_of_message:
            print(f'finish click on button "{text}"')
            break
        if index == 0:
            first_last_coin_of_message = last_coin_of_message
            index = 1


async def click_one(app, client, event, text):
    sender = await event.get_sender()
    messages = await client.get_messages(sender.username)
    t_start = (time.time())
    await messages[0].click(text=text)
    await asyncio.sleep(1)
    messages = await client.get_messages(sender.username)
    t_finish = (time.time())
    if t_finish - t_start > 2:
        app.log_error.error(f'Click button: {text}, Execution time: {t_finish - t_start}, Error: timeout error')
    else:
        app.log_debug.debug(f'Click button: {text}, Execution time: {t_finish - t_start}')
    message = messages[-1].to_dict().get('message')
    print(message.split('\n'))
    await asyncio.sleep(2)


async def send_one_message(app, client, message):
    global t
    while True:
        try:
            await client.send_message(app.bot_name, message)
            t = (time.time())
            break
        except errors.FloodWaitError as e:
            app.log_error.error(e, exc_info=True)
            print('Flood for', e.seconds)
            await asyncio.sleep(e.seconds)


async def response_processing(app, response, client):
    global n
    if 'Уважаемый пользователь' in response:
        messages = await client.get_messages(app.bot_name)
        await messages[0].click()
        await asyncio.sleep(3)
    else:
        n += 1
