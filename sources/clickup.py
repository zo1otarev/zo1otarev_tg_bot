from clickupython import client
from config import CLICKUP_TOKEN, FILE_NAME_STUDENTS
import json


class clickup(object):

    def __init__(self, list_id):
        self.client_ = client.ClickUpClient(CLICKUP_TOKEN)
        self.list_ = list_id
        with open(FILE_NAME_STUDENTS, 'r', encoding='utf-8') as jfile:
            self.profiles_ = json.load(jfile)

    def create_profiles(self):

        if self.profiles_["__meta__"]["count"] == 0:
            return "No profiles has been added"

        pr = []
        pr_text = str()
        for profile in self.profiles_["students"]:
            pr.append(profile)
            text = str()
            text = 'Имя: ' + profile['name'] + '\nФамилия: ' + profile['surname'] + '\nГруппа: ' + profile[
                'group'] + '\nОценка по АЯ: ' + str(profile['grade']) + '\nТема: ' + profile[
                       'theme'] + '\nНик в телеграме: ' + profile['username']

            self.client_.create_task(list_id=self.list_, name="Profile", description=text)
            pr_text += text + '\n\n'

        data = dict()
        data["students"] = []
        count = dict()
        count["count"] = 0
        data["__meta__"] = count

        with open(FILE_NAME_STUDENTS, 'w', encoding='utf-8') as jfile:
            json.dump(data, jfile)
            print("Saved")

        return pr_text
