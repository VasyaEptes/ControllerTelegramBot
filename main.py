import libb.app as app_
import sys
import asyncio
import libb.message_handler as handler
from libb.pyrogram_messanger import messanger


async def main():
    app = app_.App()
    if app.status != 0:
        app.sms(f"{app.config['bot_name']}. База не подключена")
        sys.exit()
    await asyncio.gather(handler.run(app=app), messanger(app=app))

if __name__ == '__main__':
    asyncio.run(main())
