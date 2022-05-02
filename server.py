import random

import requests
import vk_api.vk_api
from vk_api import VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from random import randrange

# Мб мне не нужно использовать BotLongPoll, а просто VkLongPoll как в задании


class Server:

    def __init__(self, api_token, group_id, server_name: str = "Empty"):
        self.server_name = server_name
        self.vk = vk_api.VkApi(token=api_token)
        # Для использования Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        # Для вызова методов vk_api
        self.vk_api = self.vk.get_api()
        self.upload = VkUpload(self.vk)
        self.session = requests.Session()

    def send_msg(self, send_id, message=None, attachment=None):
        self.vk_api.messages.send(peer_id=send_id, attachment=attachment,
                                  message=message, random_id=random.randrange(10 ** 7))

    def test(self):
        # Посылаем сообщение пользователю с указанным ID
        self.send_msg(77616340, "Привет-привет!")

    def start(self):
        for event in self.long_poll.listen():  # Слушаем сервер
            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                peer_id = event.object['message']['peer_id']
                from_id = event.object["message"]["from_id"]
                self.get_message_info(event)
                self.send_msg(peer_id, f'{self.get_user_name(from_id)}, я получил Ваше сообщение!')
                img = self.get_img_attachment(image_url='https://clck.ru/gi6GE', peer_id=peer_id)
                self.send_msg(peer_id, attachment=img)

    def get_message_info(self, event):
        """
        Информация о полученном сообщении
        От кого/Из какого города/Текст сообщения/Куда получено сообщение(группа/личное сообщение)
        """

        user = self.get_user_name(event.object['message']['from_id'])
        print("Username: " + user)
        print("From: " + self.get_user_city(event.object['message']['from_id']))
        print("Text: " + event.object['message']['text'])
        print("Type: ", end="")
        if event.object['message']['id'] > 0:
            print("private message")
        else:
            print("group message")
        print(" --- ")


    def get_user_name(self, user_id):
        """ Получаем имя пользователя"""

        first_name = self.vk_api.users.get(user_id=user_id)[0]['first_name']
        last_name = self.vk_api.users.get(user_id=user_id)[0]['last_name']
        return f'{first_name} {last_name}'

    def get_user_city(self, user_id):
        """ Получаем город пользователя"""

        return self.vk_api.users.get(user_id=user_id, fields="city")[0]["city"]['title']

    def get_img_attachment(self, image_url, peer_id):
        attachments = []
        image = self.session.get(image_url, stream=True)
        photo = self.upload.photo_messages(photos=image.raw)[0]
        attachments.append(f'photo{photo["owner_id"]}_{photo["id"]}')
        return ','.join(attachments)

