import os
import telebot
import re
import logging
from flask import Flask, request
from students_bd import Studetns_DB, Known_Users, Student
from clickup import clickup
from config import TOKEN, COMMANDS
from telebot import types

students = Studetns_DB()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id
    known_users = Known_Users()
    known_users.load()

    if cid not in known_users['users']:
        known_users.save_to_file(cid)
        command_help(message)
        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        item_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        markup_inline.add(item_yes, item_no)
        bot.send_message(message.chat.id, "Хочешь зарегестрироватся?", reply_markup=markup_inline)
    else:
        bot.send_message(cid, "Я тебя знаю чел. Зачем ты жмешь кнопку старт? \nНажми /help для инфы.")


@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "Существующие команды бота: \n"
    for key in COMMANDS:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += COMMANDS[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.data == "yes":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Тогда проходи регистрацию")
        msg = bot.send_message(chat_id=call.message.chat.id, text='Как тебя зовут?')
        bot.register_next_step_handler(msg, get_name)
    elif call.data == "no":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Жаль, но ты это...")
        bot.send_message(chat_id=call.message.chat.id,
                         text='Просто напиши /reg , когда захочешь зарегистрироваться')
    elif call.data == "approve":  # call.data это callback_data, которую мы указали при объявлении кнопки
        parse(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Запомню : )')
    elif call.data == "not_approve":
        delete_anket(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Тогда ты можешь пройти регистрацию заново /reg')


@bot.message_handler(commands=['reg'])
def reg(message):
    bot.send_message(message.from_user.id, "Как тебя зовут?")
    global students
    chat_id = message.chat.id
    students[chat_id] = Student('', '', '', '', '', 0, 0)
    bot.register_next_step_handler(message, get_name)  # следующий шаг – функция get_name


def get_name(message):  # получаем фамилию
    global students
    students[message.chat.id] = Student(message.text, '', '', '', '', 0, 0)
    bot.send_message(message.chat.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global students
    students[message.chat.id].surname = message.text
    bot.send_message(message.chat.id, 'Напиши свою группу в формате ИУ8-**, где ** твои цифры. Пример: ИУ8-33')
    bot.register_next_step_handler(message, get_group)


def get_group(message):
    if len(message.text) == 6 and re.match(r'ИУ8-[0-9]{2}', message.text):
        global students
        students[message.chat.id].group = message.text
        bot.send_message(message.chat.id, 'Какая оценочка по АЯ?')
        bot.register_next_step_handler(message, get_grade)
    else:
        bot.send_message(message.from_user.id,
                         'Я бот, поэтому могу повторить.\nНапиши свою группу в формате ИУ8-**, где ** твои цифры. Пример: ИУ8-33')
        bot.register_next_step_handler(message, get_group)
        return


def get_grade(message):
    try:
        global students
        students[message.chat.id].grade = int(message.text)
        if students[message.chat.id].grade > 5 or students[message.chat.id].grade < 1:
            bot.send_message(message.from_user.id,
                             'Вряд ли такая оценка может быть по пятибальной шкале. Введи еще раз')
            bot.register_next_step_handler(message, get_grade)
            return
    except Exception:
        bot.send_message(message.from_user.id, 'Введите еще раз, но цифрами, пожалуйста')
        bot.register_next_step_handler(message, get_grade)
        return
    bot.send_message(message.from_user.id, 'Введите свою тему')
    bot.register_next_step_handler(message, get_theme)


def get_theme(message):
    global students
    students[message.chat.id].theme = message.text
    students[message.chat.id].chat_id = message.chat.id
    students[message.chat.id].username = message.from_user.username

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='approve')  # кнопка «Да»
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='not_approve')
    keyboard.add(key_yes, key_no)
    question = 'Проверь заполненные данные.\nТебя зовут: ' + students[message.chat.id].name + ' ' + students[
        message.chat.id].surname + '.\nТвоя группа: ' + students[
                   message.chat.id].group + '.\nТвоя оценка по АЯ: ' + str(
        students[message.chat.id].grade) + '.\nТвоя тема: ' + students[message.chat.id].theme + '.'
    bot.send_message(message.chat.id, text=question, reply_markup=keyboard)


def parse(chat_id):
    global students
    students.save_to_file(chat_id)


def delete_anket(chat_id):
    global students
    del students[chat_id]


def extract_arg(arg):
    return arg.split()[1:]


@bot.message_handler(commands=['create_current_profiles'])
def create_current_profiles(message):
    status = extract_arg(message.text)
    list_id = ''
    if not status:
        bot.send_message(message.chat.id, text="Введи скопированнаю (url-ссылку) твоего листа после комманды")
        return
    if len(status) > 1:
        bot.send_message(message.chat.id,
                         text="Ну ты индеец, я балдею. Написал аргументов с горой после команды. Я взял первый из них как ссылку на твой лист")
    if re.match(r'https://app.clickup.com/24402514/v/li/[0,9]*', status[0]):
        list_id = re.sub(r'https://app.clickup.com/24402514/v/li/', '', status[0])
    else:
        bot.send_message(message.chat.id,
                         text="Ты ошибся. Введи скопированнаю (url-ссылку) твоего листа после комманды")
        return

    global students
    students.clear()
    cl = clickup(list_id)
    try:
        text = cl.create_profiles()
        bot.send_message(message.chat.id, text=text)
    except Exception:
        bot.send_message(message.chat.id, 'Ты ошибся, введи верную url-ccылку на лист, к которой у бота есть доступ')
        return


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)


    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(
            url="https://min-gallows.herokuapp.com/bot")  # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200


    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.
    # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
    bot.remove_webhook()
    bot.infinity_polling()
