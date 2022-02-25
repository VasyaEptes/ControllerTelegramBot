import libb.app as app_
import sys
import time


def main():
    app = app_.App()
    if app.status != 0:
        app.sms(f"{app.config['bot_name']}. База не подключена")
        sys.exit()


if __name__ == '__main__':
    main()
