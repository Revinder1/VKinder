import vk_api.vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import requests
import commander
import user_initialiser


class Server:

    def __init__(self, api_token, group_id, server_name: str = "Empty"):
        self.server_name = server_name
        self.api_token = api_token
        self.group_id = group_id
        self.vk = vk_api.VkApi(token=api_token)
        # Для использования Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        # Для вызова методов vk_api
        self.vk_api = self.vk.get_api()
        self.upload = VkUpload(self.vk)
        self.session = requests.Session()
        self.users = dict()

    def send_msg(self, send_id, message=None, attachment=None, keyboard=None):
        self.vk_api.messages.send(peer_id=send_id, attachment=attachment,
                                  message=message, keyboard=keyboard, random_id=random.randrange(10 ** 7))

    def test(self):
        # Посылаем сообщение пользователю с указанным ID
        self.send_msg(77616340, "Привет-привет!")

    def start(self):
        for event in self.long_poll.listen():  # Слушаем сервер
            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                peer_id = event.object["message"]["peer_id"]
                from_id = event.object["message"]["from_id"]
                msg_text = event.object["message"]["text"]
                if from_id not in self.users:
                    self.users[from_id] = commander.Commander(self.api_token, self.group_id, from_id)

                # В ИТОГЕ НУЖНО ОТПРАВИТЬ СООБЩЕНИЕ ЮЗЕРУ ЧЕРЕЗ КОММАНДЕР, ПРИЛОЖИВ КЛАВИАТУРУ ВКиндера
                    self.send_msg(peer_id, self.users[from_id].handle_message(msg_text))
                # ПОЛЕ relation МОЖЕТ ВООБЩЕ НЕ ВЕРНУТЬ НИЧЕГО(ДАЖЕ 0), НУЖНО ОБРАБОТАТЬ
                print(self.vk_api.users.get(user_id=from_id, fields="age,sex,city,relation"))






                # if msg_text == 'покажи клавиатуру':
                #     self.send_msg(peer_id, message='test keyboard',
                #                   keyboard=open('keyboards/keyboard.json', "r", encoding="UTF-8").read())
                # elif msg_text == 'убери кнопки':
                #     self.send_msg(peer_id, message='Отключаю клавиатуру', keyboard=open(
                #         'keyboards/turn_off_keyboard.json', 'r', encoding='utf-8').read())
                # self.get_message_info(event)
                # self.send_msg(peer_id, f'{self.get_user_name(from_id)}, я получил Ваше сообщение!')
                # img = self.get_img_attachment(image_url='https://clck.ru/gi6GE', peer_id=peer_id)
                # self.send_msg(peer_id, attachment=img)


