import asyncio


async def controler(app):
    while True:
        count = 0
        await asyncio.sleep(0.1)
        while app.status_next is False:
            await asyncio.sleep(0.01)
            while app.next_push:
                await asyncio.sleep(0.01)
            count += 1
            if count > 500:
                app.log_error.error(f'превышено время ожидания {app.seq}')
                app.sms(f'превышено время ожидания {app.seq}')
                app.status_next = True
                break
        await asyncio.sleep(0.1)
        while app.waiting is True:
            await asyncio.sleep(0.1)
            if app.waiting is False:
                break



