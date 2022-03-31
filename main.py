import libb.app as app_
import sys
import asyncio
import time
import libb.messager as messanger
# import libb.messager_2 as messanger


async def main():
    app = app_.App()
    if app.status != 0:
        app.sms(f"{app.config['bot_name']}. База не подключена")
        sys.exit()
    await messanger.run(app=app)
    # messanger.run(app=app)


if __name__ == '__main__':
    asyncio.run(main())
