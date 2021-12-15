from dotenv import load_dotenv
import os

COMMANDS = {  # command description used in the "help" command
    'start': 'Запуск бота',
    'help': 'Дает информацию о командах бота',
    'reg': 'Используй ее для регистрации',
}

load_dotenv()
TOKEN = str(os.getenv(key="TOKEN"))

FILE_NAME_STUDENTS = "../json/data.json"
FILE_NAME_USERS = "../json/users.json"
