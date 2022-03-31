import asyncio
from telethon import errors
import time
import sys
import re

from telethon import TelegramClient, events
t = 0
n = 0
request_message = ''
status_next = False


QUERY_BRANCH_1 = ["Фонды", "Список фондов", "Инвестиции", "Категории", "Назад"]
QUERY_BRANCH_2 = ["Аналитика", "Статистика рынка", "🔝 ТОП 100", "Категории", "События", "Новые токены", "Эмиссия",
                  "Капитализация", "Назад"]
QUERY_BRANCH_3 = ["Техподдержка", "Инструкция", "Написать", "Политика", "Оферта", "Назад"]
QUERY_BRANCH_4 = ["Аккаунт", "Инфо", "Настройки", "Язык", "Аккаунт", "Избранное", "Портфель", "Оплата", "Сигналы",
                  "Сигналы(Инфо)", "Назад"]
QUERY_ARRAY = [QUERY_BRANCH_1, QUERY_BRANCH_2, QUERY_BRANCH_3]
QUERY_BRANCH_TEST = [["🔝 ТОП 100", "Категории", "События", "Новые токены"]]


async def run(app):
    global n, status_next
    '''Создание клиента'''
    client = TelegramClient('anon', app.app_id, app.app_hash)
    """Создание событий для постоянного мониторинга сообщений"""
    try:
        @client.on(events.NewMessage(chats=(app.bot_name)))
        async def normal_handler(event):
            global t, request_message, status_next
            """Получение ответа"""
            sender = await event.get_sender()
            response = await client.get_messages(sender.username)
            from_id = None
            """Получаем id сообщения"""
            if response[-1].to_dict().get('peer_id') is not None:
                from_id = response[-1].to_dict().get('peer_id').get('user_id')
            """Получаем ссылку из сообщения. если она есть"""
            url = ''
            if response[-1].to_dict().get('entities') is not None and response[-1].to_dict().get('entities') != []:
                try:
                    url = response[-1].to_dict().get('entities').get('url')
                except:
                    pass
            """Считаем время ответа"""
            t = (time.time()) - t
            """Забираем сообщения из ответа"""
            response_message = response[-1].to_dict()['message']
            # print(response_message.split('\n'), '\n', url)
            client_id = app.config['telegram_client']['id']
            """Проверяем, что сообщение пришло от бота web3space и время ответа """
            if from_id != client_id and t > 2:
                app.log_error.error(f'Request: {request_message}, From_id: {from_id}, time: {t}, Error: timeout error')
            else:
                app.log_debug.debug(f'Request: {request_message}, From_id: {from_id}, Execution time: {t}')
            status_next = False
            await response_processing(app=app, response=response_message, client=client)
            await data_processing(app=app, response=response_message)
            """Проверяем ответ на наличие нужного заголовка и запускаем циклы нажатия на кнопки"""
            if '🏆 🔝 Топ 100' in response_message:
                await asyncio.sleep(0.5)
                await click_loop(app=app, client=client, event=event, text='▶', count_check_string=4)
                await click_loop(app=app, client=client, event=event, text='◀', count_check_string=4)
                await click_one(app=app, client=client, event=event, text='Сравнить все')
                await click_loop(app=app, client=client, event=event, text='▶', count_check_string=6)
                await click_loop(app=app, client=client, event=event, text='◀', count_check_string=6)
                status_next = True
            elif 'Фонды 7дн 30дн Баллы Тикер' in response_message or 'Фонды сегодня' in response_message or\
                    '📶 Категории' in response_message or 'Топ токенов с эмиссией' in response_message:
                await asyncio.sleep(0.5)
                await click_loop(app=app, client=client, event=event, text='▶', count_check_string=4)
                await click_loop(app=app, client=client, event=event, text='◀', count_check_string=4)
                status_next = True
            elif 'Топ токенов с капитализацией' in response_message:
                await asyncio.sleep(0.5)
                await click_loop(app=app, client=client, event=event, text='▶', count_check_string=5)
                await click_loop(app=app, client=client, event=event, text='◀', count_check_string=5)
                status_next = True
            elif '🏆 🔝 События' in response_message or '🏆 🔝 Топ 10 новых токенов' in response_message:
                await asyncio.sleep(0.5)
                await click_loop(app=app, client=client, event=event, text='▶', count_check_string=4)
                await click_loop(app=app, client=client, event=event, text='◀', count_check_string=4)
                status_next = True
            else:
                status_next = True
    except Exception as e:
        app.log_error.error(e, exc_info=True)
        app.sms(f'Бот {app.config["my_bot_name"]} ERROR: Бот упал и требует вмешательства.')
    """Запускаем клиент"""
    try:
        await client.start()
    except Exception as e:
        app.log_error.error('Connection to Telegram failed 5 times \n', exc_info=True)
        app.sms(f'Бот {app.config["my_bot_name"]} ERROR: Не удалось подключиться к Telegram')
        sys.exit()
    # for query in QUERY_ARRAY:
    for query in QUERY_BRANCH_TEST:
        print(query)
        n = 0
        while n < len(query):
            global request_message, status_next
            request_message = query[n]
            print(n, request_message)
            await send_one_message(app=app, client=client, message=query[n])
            while status_next is False:
                await asyncio.sleep(0.5)
            await asyncio.sleep(1)
            status_next = False
    """Клиент продолжит работы. пока не будет остановлен вручную"""
    await client.run_until_disconnected()


async def click_loop(app, client, event, text, count_check_string):
    sender = await event.get_sender()
    username = sender.username
    messages = await client.get_messages(username)
    first_last_coin_of_message = ''
    index = 0
    while True:
        t_start = (time.time())
        print(text)
        try:
            await messages[0].click(text=text)
        except:
            print('ERROR click in method "click_loop"')
        await asyncio.sleep(0.5)
        messages = await client.get_messages(username)
        message = messages[-1].to_dict().get('message')
        await data_processing(app=app, response=message)
        t_finish = (time.time())
        if t_finish - t_start > 2:
            app.log_error.error(f'Click button: {text}, Execution time: {t_finish - t_start}, Error: timeout error')
        else:
            app.log_debug.debug(f'Click button: {text}, Execution time: {t_finish - t_start}')
        # print(message.split('\n'))
        last_coin_of_message = message.split('\n')[count_check_string]
        await asyncio.sleep(0.5)
        if last_coin_of_message == first_last_coin_of_message:
            print(f'finish click on button "{text}"')
            break
        if index == 0:
            first_last_coin_of_message = last_coin_of_message
            index = 1


async def click_one(app, client, event, text):
    sender = await event.get_sender()
    username = sender.username
    messages = await client.get_messages(username)
    t_start = (time.time())
    print(text)
    try:
        await messages[0].click(text=text)
    except:
        print('ERROR click in method "click_one"')
    await asyncio.sleep(0.5)
    await client.get_messages(username)
    t_finish = (time.time())
    if t_finish - t_start > 2:
        app.log_error.error(f'Click button: {text}, Execution time: {t_finish - t_start}, Error: timeout error')
    else:
        app.log_debug.debug(f'Click button: {text}, Execution time: {t_finish - t_start}')
    # message = messages[-1].to_dict().get('message')
    # print(message.split('\n'))
    await asyncio.sleep(0.5)


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
        except Exception as e:
            app.log_error.error(e, exc_info=True)


async def data_processing(app, response):
    response_status = True
    if 'Топ 100' in response:
        try:
            message_list = response.split('\n')
            if len(message_list) > 6:
                check_line = message_list[4].split() + [message_list[5].split(':')[-1].strip()]
                data = {'symbol': check_line[2].split('/')[-1].replace(']', ''),
                        'funds_count': int(check_line[3])}
                capitalization = check_line[4]
                category = check_line[5]
                if capitalization != 'N/A':
                    capitalization_0 = float(capitalization)
                    coef_str = check_line[5]
                    if coef_str == 'млрд.':
                        coef = 1_000_000_000
                    elif coef_str == 'млн.':
                        coef = 1_000_000
                    elif coef_str == 'тыс.':
                        coef = 1000
                    else:
                        coef = 1
                    capitalization = int(capitalization_0 * coef)
                    category = check_line[6]
                data['capitalization'] = capitalization
                p = re.compile(r'/\d+ (.*)')
                try:
                    category = p.findall(category)[0]
                except:
                    category = '-99'
                data['category'] = category
                coin = app.collection.find_one({'symbol': data['symbol']})
                try:
                    status = True
                    while status is True:
                        if data['capitalization'] != int(coin['capitalization']):
                            status = False
                        if data['category'] != coin['category']:
                            status = False
                        if data['funds_count'] != len(coin['fund']):
                            status = False
                        break
                    if status is False:
                        coin_log = {'symbol': coin['symbol'], 'funds_count': len(coin['fund']), 'capitalization':
                                    int(coin['capitalization']), 'category': coin['category']}
                        app.log_error.error(f'Incorrect data for the query "Топ 100". Symbol: {data["symbol"]}\n\n'
                                            f'data from telegram bot: {data}\ndata from db: {coin_log}\n{"*"*10}')
                        response_status = False
                except Exception as e:
                    app.log_error.error(f'{e}\n{coin}\n', exc_info=True)
            else:
                app.log_error.error(f'Incorrect data for the query "Топ 100"')
                response_status = False
        except Exception as e:
            app.log_error.error(f'{e}', exc_info=True)
            response_status = False
    if 'Статистика рынка' in response:
        if 'Цена BTC' not in response or 'Цена ETH' not in response:
            app.log_error.error('Incorrect data for the query "Статистика рынка".')
            response_status = False
    if 'Сравнение Топ 15' in response:
        if len(response.split('\n')) < 21:
            app.log_error.error('Incorrect data for the query "Сравнение Топ 15".')
            response_status = False
    if 'Категории' in response:
        if '№   Интерес/Капитал.    Название' not in response or len(response.split('\n')) < 15:
            app.log_error.error('Incorrect data for the query "Категории".')
            response_status = False
    if 'События' in response:
        if len(response.split('\n')) < 10:
            app.log_error.error('Incorrect data for the query "События".')
            response_status = False
    if 'Топ 10 новых токенов' in response:
        if len(response.split('\n')) < 5:
            app.log_error.error('Incorrect data for the query "Новые токены".')
            response_status = False
    if 'Топ токенов с эмиссией' in response:
        message_list = response.split('\n')
        status = True
        try:
            if len(message_list) > 6:
                check_line = message_list[4].split() + [message_list[5].split(':')[-1].strip()]
                data = {'symbol': check_line[3].split('/')[-1].replace(']', ''),
                        'funds_count': int(check_line[2]), 'coef_issue': float(check_line[1].replace('%', ''))}
                p = re.compile(r'/\d+ (.*)')
                category = check_line[4]
                try:
                    category = p.findall(category)[0]
                except:
                    category = '-99'
                data['category'] = category
                coin = app.collection.find_one({'symbol': data['symbol']})
                try:
                    while status is True:
                        if data['coef_issue'] != float(coin['coef issue']):
                            status = False
                        if data['category'] != coin['category']:
                            status = False
                        if data['funds_count'] != len(coin.get('fund')):
                            status = False
                        break
                    if status is False:
                        coin_log = {'symbol': coin['symbol'], 'funds_count': len(coin['fund']), 'coef_issue':
                                    float(coin['coef issue']), 'category': coin['category']}
                        app.log_error.error(f'Incorrect data for the query "Топ токенов с эмиссией 90-100 %". Symbol: '
                                            f'{data["symbol"]}\n\ndata from telegram bot: {data}\ndata from db: '
                                            f'{coin_log}\n{"*" * 10}')
                        response_status = False
                except Exception as e:
                    app.log_error.error(f'{e}\n{coin}\n', exc_info=True)
            else:
                app.log_error.error(f'Incorrect data for the query "Топ токенов с эмиссией 90-100 %"')
                response_status = False
        except Exception as e:
            app.log_error.error(f'{e}', exc_info=True)
            response_status = False
    if 'Топ токенов с капитализацией' in response:
        message_list = response.split('\n')
        try:
            if len(message_list) > 7:
                check_line = message_list[6].split() + [message_list[7].split(':')[-1].strip()]
                data = {'symbol': check_line[4].split('/')[-1].replace(']', ''),
                        'funds_count': int(check_line[3])}
                capitalization_0 = float(check_line[2])
                coef_str = check_line[3]
                if coef_str == 'млрд.':
                    coef = 1_000_000_000
                elif coef_str == 'млн.':
                    coef = 1_000_000
                else:
                    coef = 1
                capitalization = int(capitalization_0 * coef)
                data['capitalization'] = capitalization
                p = re.compile(r'/\d+ (.*)')
                category = check_line[4]
                try:
                    category = p.findall(category)[0]
                except:
                    category = '-99'
                data['category'] = category
                coin = app.collection.find_one({'symbol': data['symbol']})
                try:
                    status = True
                    while status is True:
                        if data['capitalization'] != float(coin['capitalization']):
                            status = False
                        if data['category'] != coin['category']:
                            status = False
                        if data['funds_count'] != len(coin['fund']):
                            status = False
                        break
                    if status is False:
                        coin_log = {'symbol': coin['symbol'], 'funds_count': len(coin['fund']), 'capitalization':
                                    int(coin['capitalization']), 'category': coin['category']}
                        app.log_error.error(f'Incorrect data for the query "Топ токенов с капитализацией".'
                                            f' Symbol: {data["symbol"]}\n\ndata from telegram bot: {data}\ndata from db: '
                                            f'{coin_log}\n{"*" * 10}')
                        response_status = False
                except Exception as e:
                    app.log_error.error(f'{e}\n{coin}\n', exc_info=True)
            else:
                app.log_error.error(f'Incorrect data for the query "ТТоп токенов с капитализацией"')
                response_status = False
        except Exception as e:
            app.log_error.error(f'{e}', exc_info=True)
            response_status = False
    if 'Список фондов' in response:
        if len(response.split('\n')) < 17:
            app.log_error.error('Incorrect data for the query "Список фондов".')
            response_status = False
    if 'Фонды 7дн 30дн Баллы Тикер' in response:
        if len(response.split('\n')) < 5:
            app.log_error.error('Incorrect data for the query "Инвестиции".')
            response_status = False
    if 'Фонды сегодня' in response:
        if len(response.split('\n')) < 15:
            app.log_error.error('Incorrect data for the query "Категории".')
            response_status = False
    if response == '':
        print('Empty')
        app.log_error.error('Incorrect data for the query "Категории".')
        response_status = False
    if response_status is False:
        app.sms(f'Бот {app.config["my_bot_name"]} WARNING: Telegram отдает не правильную информацию')


async def response_processing(app, response, client):
    global n
    if 'Уважаемый пользователь' in response:
        messages = await client.get_messages(app.bot_name)
        await messages[0].click()
        await asyncio.sleep(3)
    else:
        n += 1
