import random
import re
from datetime import datetime
from random import randrange
import vk_api
from db.db_model import DbWorker
import db.db_model
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
        self.db = DbWorker(self.user_id)
        self.age_interval = ''
        self.link = ''
        self.age_from = 0
        self.age_to = 0
        self.age_pattern = r"(\d{2})-(\d{2,3})"
        self.generator = 0
        self.bl_generator = 0
        self.fav_generator = 0
        self.city = self.user.get_user_city()
        self.previous_id = 0
        self.previous_link = ''


    def handle_message(self, msg):
        if msg.startswith("/"):
            if msg[1::].lower() == 'начать':
                if not self.db.check_if_registered():
                    self.db.register_user()
                self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                              keyboard=self.create_keyboard())
            if msg[1::].lower() == 'меню':
                self.menu_bot(self.user_id, self.peer_id)

            if msg[1::].lower() == 'старт':
                if self.age_from == 0:
                    self.send_msg(self.peer_id, message='Введите возрастной диапазон X-X (Прим.: 18-20)')
                self.generator = self.user.search_user_pair_info(self.city, self.age_from, self.age_to)
                while True:
                    post = generator_reader(self.generator)['id']
                    post_link = f'https://vk.com/id{post} '
                    if not self.db.check_if_in_favorites(post) and not self.db.check_if_in_blacklist(post):
                        self.send_msg(self.peer_id, message=f'{post_link}',
                                      attachment=self.get_img_attachment(self.user.get_best_three_photo(post)))
                        self.previous_id = post
                        self.previous_link = post_link
                        break
                    continue

            if msg[1::].lower() == 'нравится':
                self.db.add_pair_in_favorite(self.previous_id, self.city, self.age_interval, self.previous_link,
                                             self.get_img_attachment(self.user.get_best_three_photo(self.previous_id)))
                while True:
                    post = generator_reader(self.generator)['id']
                    post_link = f'https://vk.com/id{post} '
                    if not self.db.check_if_in_favorites(post) and not self.db.check_if_in_blacklist(post):
                        self.send_msg(self.peer_id, message=f'{post_link}',
                                      attachment=self.get_img_attachment(self.user.get_best_three_photo(post)))
                        self.previous_id = post
                        self.previous_link = post_link
                        break
                    continue


            if msg[1::].lower() == 'не нравится':
                self.db.add_pair_in_blacklist(self.previous_id, self.city, self.age_interval, self.previous_link,
                                              self.get_img_attachment(self.user.get_best_three_photo(self.previous_id)))
                while True:
                    post = generator_reader(self.generator)['id']
                    post_link = f'https://vk.com/id{post} '
                    if not self.db.check_if_in_favorites(post) and not self.db.check_if_in_blacklist(post):
                        self.send_msg(self.peer_id, message=f'{post_link}',
                                      attachment=self.get_img_attachment(self.user.get_best_three_photo(post)))
                        self.previous_id = post
                        self.previous_link = post_link
                        break
                    continue

            if msg[1::].lower() == 'черный список':
                try:
                    self.bl_generator = self.db.show_blacklist()
                    bl_link = generator_reader(self.bl_generator)
                    self.previous_id = bl_link.vk_id
                    link = bl_link.link
                    photos = bl_link.link_photo_list
                    self.send_msg(self.peer_id, message=f'{link}', attachment=photos)
                    self.send_msg(self.peer_id, message='Ваш черный список',
                                  keyboard=self.create_bl_keyboard())
                except StopIteration:
                    self.send_msg(self.peer_id, message='Черный список пуст, возвращаю к поиску партнера')
                    self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                                  keyboard=self.create_keyboard())

            if msg[1::].lower() == 'избранные':
                try:
                    self.fav_generator = self.db.show_favorites()
                    fav_link = generator_reader(self.fav_generator)
                    self.previous_id = fav_link.vk_id
                    link = fav_link.link
                    photos = fav_link.link_photo_list
                    self.send_msg(self.peer_id, message=f'{link}', attachment=photos)
                    self.send_msg(self.peer_id, message='Ваш черный список',
                                  keyboard=self.create_fav_keyboard())
                except StopIteration:
                    self.send_msg(self.peer_id, message='Список избранных пуст, возвращаю к поиску партнера')
                    self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                                  keyboard=self.create_keyboard())


            if msg[1::].lower() == 'дальше чс':
                try:
                    bl_link = generator_reader(self.bl_generator)
                    self.previous_id = bl_link.vk_id
                    link = bl_link.link
                    photos = bl_link.link_photo_list
                    self.send_msg(self.peer_id, message=f'{link}', attachment=photos)
                except StopIteration:
                    self.send_msg(self.peer_id, message='Черный список пуст, возвращаю к поиску партнера')
                    self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                                  keyboard=self.create_keyboard())

            if msg[1::].lower() == 'удалить из чс':
                try:
                    self.db.delete_from_blacklist(self.previous_id)
                    bl_link = generator_reader(self.bl_generator)
                    self.previous_id = bl_link.vk_id
                    link = bl_link.link
                    photos = bl_link.link_photo_list
                    self.send_msg(self.peer_id, message=f'{link}', attachment=photos)
                except StopIteration:
                    self.send_msg(self.peer_id, message='Черный список пуст, возвращаю к поиску партнера')
                    self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                                  keyboard=self.create_keyboard())

            if msg[1::].lower() == 'удалить из избранных':
                try:
                    self.db.delete_from_favorite(self.previous_id)
                    fav_link = generator_reader(self.fav_generator)
                    self.previous_id = fav_link.vk_id
                    link = fav_link.link
                    photos = fav_link.link_photo_list
                    self.send_msg(self.peer_id, message=f'{link}', attachment=photos)
                except StopIteration:
                    self.send_msg(self.peer_id, message='Черный список пуст, возвращаю к поиску партнера')
                    self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                                  keyboard=self.create_keyboard())


            if msg[1::].lower() == 'вернуться':
                self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                              keyboard=self.create_keyboard())



            if msg[1::].lower() == 'дальше избранные':
                try:
                    fav_link = generator_reader(self.fav_generator)
                    link = fav_link.link
                    photos = fav_link.link_photo_list
                    self.send_msg(self.peer_id, message=f'{link}', attachment=photos)
                except StopIteration:
                    self.send_msg(self.peer_id, message='Список избранных пуст, возвращаю к поиску партнера')
                    self.send_msg(self.peer_id, message='Нажмите "Старт", чтобы начать знакомиться',
                                  keyboard=self.create_keyboard())



        if re.fullmatch(self.age_pattern, msg):
            # добавить /возраст сброс
            if int(msg[0:2]) < 18 or int(msg[3:]) > 99:
                return self.send_msg(self.peer_id, message='Возрастные ограничения от 18 до 99 лет')

            self.send_msg(self.peer_id, message=f'Возрастной диапазон поиска {msg} установлен, чтобы изменить '
                                                f'диапазон поиска введите /возраст')
            self.age_interval = msg
            self.age_from = int(msg[0:2])
            self.age_to = int(msg[3:])
            self.send_msg(self.peer_id, message='Чтобы перейти далее введите /начать')


# Попробовать использовать
#     def send_next_pair(self, generator, peer_id):




def generator_reader(generator):
    return next(generator)
