import random
import re
from datetime import datetime
from random import randrange
import vk_api
import server
import user_initialiser
import json


class Commander(server.Server):
    def __init__(self, api_token, group_id, user_id, peer_id, msg_type):
        super().__init__(api_token, group_id)
        # self.vk_api = vk_api.VkApi(token=api_token).get_api()
        self.msg_type = msg_type
        self.user_id = user_id
        self.peer_id = peer_id
        self.user = user_initialiser.UserInfo(user_id)
        self.age_from = 0
        self.age_to = 0
        self.age_pattern = r"(\d{2})-(\d{2,3})"
        self.generator = 0

    def handle_message(self, msg):
        if msg.startswith("/"):
            if msg[1::].lower() == 'начать':
                self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                              keyboard=self.create_keyboard())
            if msg[1::].lower() == 'меню':
                self.menu_bot(self.user_id, self.peer_id)

            if msg[1::].lower() == 'старт':
                if self.age_from == 0:
                    self.send_msg(self.peer_id, message='Введите возрастной диапазон X-X (Прим.: 18-20)')
                if self.user.get_user_city():
                    city = self.user.get_user_city()
                else:
                    self.send_msg(self.peer_id, message='Не могу распознать Ваш город, измените настройки профиля')
                    return "Ошибка"
                a = datetime.now()
                self.generator = self.user.search_user_pair_info(city, self.age_from, self.age_to)
                post = generator_reader(self.generator)['id']
                post_link = f'https://vk.com/id{post} '
                self.send_msg(self.peer_id, message=f'{post_link}',
                              attachment=self.get_img_attachment(self.user.get_best_three_photo(post)))
                b = datetime.now()
                print(b - a, 'eto start')

            if msg[1::].lower() == 'дальше':
                a = datetime.now()
                post = generator_reader(self.generator)['id']
                post_link = f'https://vk.com/id{post} '
                self.send_msg(self.peer_id, message=f'{post_link}',
                              attachment=self.get_img_attachment(self.user.get_best_three_photo(post)))
                b = datetime.now()
                print(b - a, 'eto dalshe')


        if re.fullmatch(self.age_pattern, msg):
            # добавить /возраст сброс
            if int(msg[0:2]) < 18 or int(msg[3:]) > 99:
                return self.send_msg(self.peer_id, message='Возрастные ограничения от 18 до 99 лет')

            self.send_msg(self.peer_id, message=f'Возрастной диапазон поиска {msg} установлен, чтобы изменить '
                                                f'диапазон поиска введите /возраст')
            self.age_from = int(msg[0:2])
            self.age_to = int(msg[3:])
            self.send_msg(self.peer_id, message='Чтобы перейти далее введите /начать')




def generator_reader(generator):
    return next(generator)
