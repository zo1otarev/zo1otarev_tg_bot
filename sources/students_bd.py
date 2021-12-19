import json
from config import FILE_NAME_STUDENTS, FILE_NAME_USERS


class Student(object):

    def __init__(self, name, surname, group, theme, username, grade, chat_id):
        self.name = name
        self.surname = surname
        self.group = group
        self.theme = theme
        self.username = username
        self.grade = grade
        self.chat_id = chat_id


class Studetns_DB(dict):


    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def new_elem(self, chat_id):
        self.__dict__[chat_id] = Student('', '', '', '', '', 0, 0)


    def save_to_file(self, chat_id):
        new_student = vars(self[chat_id])
        del self[chat_id]

        with open(FILE_NAME_STUDENTS, 'r', encoding='utf-8') as jfile:
            data = json.load(jfile)
            data["students"].append(new_student)
            data["__meta__"]["count"] += 1

        with open(FILE_NAME_STUDENTS, 'w', encoding='utf-8') as jfile:
            json.dump(data, jfile)
            print("Saved")


class Known_Users(dict):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def save_to_file(self, chat_id):
        self['users'].append(chat_id)
        self['__meta__']['count'] += 1
        with open(FILE_NAME_USERS, 'w', encoding='utf-8') as jfile:
            json.dump(self.__dict__, jfile)

    def load(self):
        with open(FILE_NAME_USERS, 'r', encoding='utf-8') as jfile:
            self.__dict__ = json.load(jfile)


