import requests
import vk_api
import config
from vk_api.vk_api import VkApi


class UserInfo:

    def __init__(self, user_id):
        self.vk_token = config.vk_api_token
        self.vk_api = vk_api.VkApi(token=self.vk_token).get_api()
        self.user_id = user_id


    def get_user_name(self):
        """ Получаем имя пользователя"""
        fields = "age,sex,city,relation"
        response = self.vk_api.users.get(user_id=self.user_id, fields=fields)

        return response

    def get_user_city(self, user_id):
        """ Получаем город пользователя"""

        return self.vk_api.users.get(user_id=user_id, fields="city")[0]["city"]['title']








    # def get_message_info(self, event):
    #     """
    #     Информация о полученном сообщении
    #     От кого/Из какого города/Текст сообщения/Куда получено сообщение(группа/личное сообщение)
    #     """
    #     user = self.get_user_name(event.object['message']['from_id'])
    #     print("Username: " + user)
    #     print("From: " + self.get_user_city(event.object['message']['from_id']))
    #     print("Text: " + event.object['message']['text'])
    #     print("Type: ", end="")
    #     if event.object['message']['id'] > 0:
    #         print("private message")
    #     else:
    #         print("group message")
    #     print(" --- ")
