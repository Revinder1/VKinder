import random
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

    def handle_message(self, msg):
        if msg.startswith("Мое имя"):
            return self.send_msg(self.peer_id, self.user.get_user_name())
        elif msg.startswith("Мой город"):
            return self.send_msg(self.peer_id, self.user.get_user_city())
        elif msg == "Мой пол":
            return self.send_msg(self.peer_id, self.user.get_user_gender())
        elif msg == "Дай фото":
            return self.send_msg(self.peer_id, attachment=self.user.get_img_attachment(self.user.get_best_three_photo(self.user_id)))
        # elif msg == "VKinder":
        #     generator_reader(self.user.search_user_pair_info(49, 23, 24))
        #     self.send_msg(self.peer_id, message=f'{generator_reader(self.user.search_user_pair_info(49, 23, 24))}')
        #     if msg == "Еще":
        #         self.send_msg(self.peer_id, message=f'{generator_reader(self.user.search_user_pair_info(49, 23, 24))}')
        #
        #     else:
        #         return "Сброс"



        # elif msg == 'Покажи клавиатуру':
        #     return self.send_msg(self.peer_id, message='Включаю',
        #                          keyboard=open('keyboards/keyboard.json', "r", encoding="UTF-8").read())
        # elif msg == 'Убери клавиатуру':
        #     return self.send_msg(self.peer_id, message='Отключаю',
        #                          keyboard=open('keyboards/turn_off_keyboard.json', "r", encoding="UTF-8").read())
        #
        # return self.send_msg(self.peer_id, 'Не распознал команду')




def generator_reader(generator):
    return next(generator)

