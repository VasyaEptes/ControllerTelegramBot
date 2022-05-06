import asyncio
import time
import sys
import re
from telethon import TelegramClient, events

t = 0
n = 0
request_message = ''


async def run(app):
    global n
    '''Создание клиента'''
    client = TelegramClient('anon', app.app_id, app.app_hash)
    app.client = client
    """Создание событий для постоянного мониторинга сообщений"""
    try:
        @client.on(events.NewMessage(chats=(app.bot_name)))
        async def normal_handler(event):
            global t, request_message
            """Получение ответа"""
            # sender = await event.get_sender()
            # username = sender.username
            username = '@Web3Space_bot'
            response = await client.get_messages(username)
            from_id = None
            """Получаем id сообщения"""
            if response[-1].to_dict().get('peer_id') is not None:
                from_id = response[-1].to_dict().get('peer_id').get('user_id')
            """Считаем время ответа"""
            t_r = (time.time()) - t
            """Забираем сообщения из ответа"""
            # print(response[-1])
            response_message = response[-1].to_dict()['message']
            client_id = app.config['telegram_client']['id']
            # """Проверяем, что сообщение пришло от бота web3space и время ответа """
            # if from_id != client_id and t_r > 2:
            #     app.log_error.error(f'Request: {request_message}, From_id: {from_id}, time: {t_r}, Error: timeout error')
            # else:
            #     app.log_debug.debug(f'Request: {request_message}, From_id: {from_id}, Execution time: {t_r}')
            await response_processing(app=app, response=response_message, client=client)
            await data_processing(app=app, response=response_message)
            """Проверяем ответ на наличие нужного заголовка и запускаем циклы нажатия на кнопки"""
            if 'Топ 100' in response_message and 'Сравнение Топ 100' not in response_message:
                app.next_push = True
                await click_loop(app=app, client=client, event=event, texts=['▶', '◀', 'Сравнить все'],
                                 count_check_string=6)
                # app.next_push = False
            elif 'Сравнение Топ 100' in response_message:
                app.next_push = True
                await click_loop(app=app, client=client, event=event, texts=['▶', '◀', 'Финансы 2', '▶', '◀', "Гитхаб",
                                                                             '▶', '◀', "Твиттер", '▶', '◀'],
                                 count_check_string=6)
                app.next_push = False
                app.status_next = True
            elif 'Сравнение Топ 15' in response_message:
                app.next_push = True
                await click_loop(app=app, client=client, event=event, texts=['▶', '◀'],
                                 count_check_string=6)
                await asyncio.sleep(1)
                app.next_push = False
                app.status_next = True
            elif 'Фонды 7дн 30дн Баллы Тикер' in response_message or 'Фонды сегодня' in response_message or \
                    'Категории' in response_message or 'Топ токенов с эмиссией' in response_message:
                app.next_push = True
                await click_loop(app=app, client=client, event=event, texts=['▶', '◀'], count_check_string=4)
                await asyncio.sleep(1)
                app.next_push = False
                app.status_next = True
            elif 'Топ токенов с капитализацией' in response_message:
                app.next_push = True
                await click_loop(app=app, client=client, event=event, texts=['▶', '◀'], count_check_string=5)
                await asyncio.sleep(1)
                app.next_push = False
                app.status_next = True
            elif '🏆 🔝 События' in response_message or '🏆 🔝 Топ 10 новых токенов' in response_message:
                app.next_push = True
                await click_loop(app=app, client=client, event=event, texts=['▶', '◀'], count_check_string=4)
                await asyncio.sleep(1)
                app.next_push = False
                app.status_next = True
            else:
                await asyncio.sleep(1)
                app.status_next = True
            # app.status_next = True
    except Exception as e:
        app.log_error.error(e, exc_info=True)
        app.sms(f'Бот {app.config["my_bot_name"]} ERROR: Бот упал и требует вмешательства.')
    """Запускаем клиент"""
    try:
        await client.start()
        await client.run_until_disconnected()
    except Exception as e:
        app.log_error.error('Connection to Telegram failed 5 times \n', exc_info=True)
        app.sms(f'Бот {app.config["my_bot_name"]} ERROR: Не удалось подключиться к Telegram')
        sys.exit()
    """Клиент продолжит работы. пока не будет остановлен вручную"""


async def click_loop(app, client, event, texts, count_check_string=0):
    for text in texts:
        app.next_click = False
        count = 0
        sender = await event.get_sender()
        username = sender.username
        t_start = (time.time())
        messages = await client.get_messages(username)
        first_last_coin_of_message = ''
        index = 0
        if text in ['Сравнить все', 'Финансы 2', "Гитхаб", "Твиттер"]:
            print(text)
            try:
                await messages[0].click(text=text)
            except:
                print('ERROR click in method "click_one"')
            t_finish = (time.time())
            if t_finish - t_start > 2:
                app.log_error.error(f'Click button: {text}, Execution time: {t_finish - t_start}, Error: timeout error')
            else:
                app.log_debug.debug(f'Click button: {text}, Execution time: {t_finish - t_start}')
        else:
            while True:
                t_start = (time.time())
                if count == 10:
                    print(f'finish click on button "{text}"')
                    break
                print(text)
                try:
                    await messages[0].click(text=text)
                    count += 1
                except:
                    print('ERROR click in method "click_loop"')
                await asyncio.sleep(0.5)
                messages = await client.get_messages(username)
                message = messages[-1].to_dict().get('message')
                await data_processing(app=app, response=message)
                t_finish = (time.time())
                t_result = t_finish - t_start
                if t_result > 2:
                    app.log_error.error(f'Click button: {text}, Execution time: {t_result}, Error: timeout error')
                else:
                    app.log_debug.debug(f'Click button: {text}, Execution time: {t_result}')
                last_coin_of_message = message
                await asyncio.sleep(0.5)
                if last_coin_of_message == first_last_coin_of_message:
                    print(f'finish click on button "{text}"')
                    break
                if index == 0:
                    first_last_coin_of_message = last_coin_of_message
                    index = 1


async def data_processing(app, response):
    app.work_status = True
    if response is not None:
        if 'Топ 100' in response:
            message_list = response.split('\n')
            if len(message_list) < 6:
                j1(app, 'неверные данные в >>> Топ 100')
        if 'Статистика рынка' in response:
            if 'Цена BTC' not in response or 'Цена ETH' not in response:
                j1(app, 'неверные данные в >>> Статистика рынка')
        if 'Сравнение Топ 15' in response:
            if len(response.split('\n')) < 21:
                j1(app, 'неверные данные в >>> Сравнение Топ 15')
        if 'Категории' in response:
            if '№   Интерес/Капитал.    Название' not in response or len(response.split('\n')) < 15:
                j1(app, 'неверные данные в >>> Категории')
        if 'События' in response:
            if len(response.split('\n')) < 10:
                j1(app, 'неверные данные в >>> События')
        if 'Топ 10 новых токенов' in response:
            if len(response.split('\n')) < 5:
                j1(app, 'неверные данные в >>> Новые токены')
        if 'Топ токенов с эмиссией' in response:
            message_list = response.split('\n')
            if len(message_list) < 6:
                j1(app, 'неверные данные в >>> Топ токенов с эмиссией')
        if 'Топ токенов с капитализацией' in response:
            message_list = response.split('\n')
            if len(message_list) < 7:
                j1(app, 'неверные данные в >>> Топ токенов с капитализацией')
        if 'Список фондов' in response:
            if len(response.split('\n')) < 17:
                j1(app, 'неверные данные в >>> Список фондов')
        if 'Фонды 7дн 30дн Баллы Тикер' in response:
            if len(response.split('\n')) < 5:
                j1(app, 'неверные данные в >>> Фонды 7дн 30дн Баллы Тикер')
        if 'Фонды сегодня' in response:
            if len(response.split('\n')) < 15:
                j1(app, 'неверные данные в >>> Фонды сегодня')
        if response == '':
            print('Empty')
            j1(app, 'неверные данные в >>> неизвестная категория')
    else:
        j1(app, f'пустой ответ в {app.seq}')


async def response_processing(app, response, client):
    global n
    if 'Уважаемый пользователь' in response:
        messages = await client.get_messages(app.bot_name)
        await messages[0].click()
        await asyncio.sleep(3)
        n = 0


def j1(app, msg):
    app.log_error.error(msg)
    app.sms(msg)
    app.work_status = False
