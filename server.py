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
        return self.vk_api.messages.send(peer_id=send_id, attachment=attachment,
                                         message=message, keyboard=keyboard, random_id=random.randrange(10 ** 7))

    def test(self):
        # Посылаем сообщение пользователю с указанным ID
        self.send_msg(77616340, "Привет-привет!")

    def start(self):

        for event in self.long_poll.listen():  # Слушаем сервер
            # Пришло новое сообщение
            if event.type == VkBotEventType.MESSAGE_NEW:
                new_dict = dict()
                peer_id = event.object["message"]["peer_id"]
                from_id = event.object["message"]["from_id"]
                msg_text = event.object["message"]["text"]
                msg_type = event.object["message"]["id"]
                print(event.object)
                # ПРОВЕРКА НА НАЛИЧИЕ СВЯЗАННОГО ЮЗЕРА-КЛАССА В СЛОВАРЕ
                if from_id not in self.users:
                    new_dict[peer_id] = commander.Commander(self.api_token, self.group_id, from_id, peer_id, msg_type)
                    self.users[from_id] = new_dict
                    self.users[from_id][peer_id].handle_message(msg_text)

                # ЕСЛИ ОДИН И ТОТ ЖЕ ЮЗЕР ОТПРАВЛЯЕТ СООБЩЕНИЯ С ЛС И ГРУППЫ, ДОБАВИТЬ В СЛОВАРЬ peer_id ГРУППЫ
                # И СВЯЗАТЬ С КЛАССОМ
                elif peer_id not in self.users[from_id]:
                    # ПРИХОДИТСЯ ОБНОВЛЯТЬ ЗНАЧЕНИЕ В СЛОВАРЕ, ИНАЧЕ ПРИ ОТПРАВКЕ С ЛС/ГРУППЫ АТРИБУТЫ КЛАССА Commander
                    # НЕ ОБНОВЛЯЮТСЯ И ОТПРАВЛЯЕТСЯ ТОЛЬКО В ОДНО МЕСТО
                    self.users[from_id][peer_id] = commander.Commander(self.api_token, self.group_id, from_id, peer_id, msg_type)
                    self.users[from_id][peer_id].handle_message(msg_text)

                else:
                    self.users[from_id][peer_id].handle_message(msg_text)



                # В ИТОГЕ НУЖНО ОТПРАВИТЬ СООБЩЕНИЕ ЮЗЕРУ ЧЕРЕЗ КОММАНДЕР, ПРИЛОЖИВ КЛАВИАТУРУ ВКиндера



                # self.send_msg(peer_id, self.users[from_id].handle_message(msg_text))

                # ПОЛЕ relation МОЖЕТ ВООБЩЕ НЕ ВЕРНУТЬ НИЧЕГО(ДАЖЕ 0), НУЖНО ОБРАБОТАТЬ

                # if msg_text == 'покажи клавиатуру':
                #     self.send_msg(peer_id, message='test keyboard',
                #                   keyboard=open('keyboards/keyboard.json', "r", encoding="UTF-8").read())
                # elif msg_text == 'убери кнопки':
                #     self.send_msg(peer_id, message='Отключаю клавиатуру', keyboard=open(
                #         'keyboards/turn_off_keyboard.json', 'r', encoding='utf-8').read())

