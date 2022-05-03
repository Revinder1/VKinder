import requests

import server


class UserInfo():
    def __init__(self):
        pass


    def get_user_name(self, user_id):
        """ Получаем имя пользователя"""
        first_name = users.get(user_id=user_id)[0]['first_name']
        last_name = users.get(user_id=user_id)[0]['last_name']
        return f'{first_name} {last_name}'

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
