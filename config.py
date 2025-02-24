import logging

# Токены и настройки
API_TOKEN = '7729139708:AAGdGrUGi-t2Xf_2QXo7Xv17vUgbopEEo-c'  # Ваш токен Telegram-бота
WB_API_KEY = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1NjA5MzY2OCwiaWQiOiIwMTk1MzM3ZS00NzNjLTczMDQtODczYy02OTA4YWQ4Njg3NjQiLCJpaWQiOjEyMDcyMzI5LCJvaWQiOjU2MzQ2OSwicyI6MTA3Mzc0MTg4Miwic2lkIjoiZGIwMzEzZGUtN2RlZi00ZGZiLWIxNmItZDEyMGVkYzViMTMwIiwidCI6ZmFsc2UsInVpZCI6MTIwNzIzMjl9.FjcSwyfT8yTwvOKjfuCExBVsT0ZrQcDDfSTGDZWkg2Hrbt5sEQB6lgU9CMIQIx3mxwmXJbAS-i0gWwr1BpkiSw'  # Замените на ваш ключ Wildberries
ZMO_API_KEY = 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIwZjlhMzUzNTY4ZGU0YmU1YTdkMmY1MTUyNWY0YzI4NCIsImF1dGhLZXkiOiJTVEFOREFSRF9VU0VSIiwiZ3JvdXBJZCI6IjRkMmU1OTQ2Yzc2YjQwOTRhOTdiNTI2ZDk4ZGQwMDcxIiwianRpIjoiOGEzMDQ1ZWQtZjg0NS00MmI0LWJjOTktMzFhMDlmMDJiZGY1In0.P_wWOSIpHKN5A2qNpF1UyNFvLNycH_CHCXmbIQElKtN5XUA5bJYz6r06ZY4yVKirMDsaGTW7Xd7JcFEq3ZCLfA '  # Ваш токен ZMO.ai
CENT_APP_API_KEY = ''  # Получить на cent.app/merchant/api
GROUP_ID = 2265036783# ID вашей группы в Telegram
DATABASE_URL = 'postgresql://botuser:password@localhost/botdb'  # PostgreSQL
REDIS_URL = 'redis://localhost:6379'

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)