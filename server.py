import json
import db.db_model
import vk_api.vk_api
from vk_api import VkUpload
from vk_api import keyboard
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
        self.keyboard = vk_api.keyboard.VkKeyboard()
        # Для использования Long Poll API
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        # Для вызова методов vk_api
        self.vk_api = self.vk.get_api()
        self.upload = VkUpload(self.vk)
        self.session = requests.Session()
        self.users = dict()

    def send_msg(self, send_id, message=None, attachment=None, keyboard=None, template=None):
        return self.vk_api.messages.send(peer_id=send_id, attachment=attachment,
                                         message=message, keyboard=keyboard, template=template,
                                         random_id=random.randrange(10 ** 7))

    def get_img_attachment(self, _list):
        attachments = []
        for url in _list:
            image = self.session.get(url, stream=True)
            photo = self.upload.photo_messages(photos=image.raw)[0]
            attachments.append(f'photo{photo["owner_id"]}_{photo["id"]}')
        return ','.join(attachments)

    def menu_bot(self, from_id, peer_id):
        self.send_msg(peer_id,
                      message=f'Добро пожаловать, {user_initialiser.UserInfo(from_id).get_user_name()}! Я - бот для '
                              f'знакомств! '
                              'Прежде чем мы начнем знакомства, укажите возраст в формате Х-Х (Прим.: 18-20)')

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
                #
                # if '/старт' in msg_text.lower():
                #     user_init = user_initialiser.UserInfo(from_id)
                #     generator = user_init.search_user_pair_info(49, 23, 24)
                #     post = commander.generator_reader(generator)['id']
                #     post_link = f'https://vk.com/id{post} '
                #     self.send_msg(peer_id, message=f'{post_link}',
                #                   attachment=self.get_img_attachment(user_init.get_best_three_photo(post)))
                # elif '/дальше' in msg_text.lower():
                #     post = commander.generator_reader(generator)['id']
                #     post_link = f'https://vk.com/id{post} '
                #     self.send_msg(peer_id, message=f'{post_link}',
                #                   attachment=self.get_img_attachment(user_init.get_best_three_photo(post)))

                # ПРОВЕРКА НА НАЛИЧИЕ СВЯЗАННОГО ЮЗЕРА-КЛАССА В СЛОВАРЕ
                if from_id not in self.users:
                    new_dict[peer_id] = commander.Commander(self.api_token, self.group_id, from_id, peer_id, msg_type)
                    self.users[from_id] = new_dict
                    # Отправляем меню новому пользователю
                    self.menu_bot(from_id, peer_id)
                    self.users[from_id][peer_id].handle_message(msg_text)

                # ЕСЛИ ОДИН И ТОТ ЖЕ ЮЗЕР ОТПРАВЛЯЕТ СООБЩЕНИЯ С ЛС И ГРУППЫ, ДОБАВИТЬ В СЛОВАРЬ peer_id ГРУППЫ
                # И СВЯЗАТЬ С КЛАССОМ
                elif peer_id not in self.users[from_id]:
                    # ПРИХОДИТСЯ ОБНОВЛЯТЬ ЗНАЧЕНИЕ В СЛОВАРЕ, ИНАЧЕ ПРИ ОТПРАВКЕ С ЛС/ГРУППЫ АТРИБУТЫ КЛАССА Commander
                    # НЕ ОБНОВЛЯЮТСЯ И ОТПРАВЛЯЕТСЯ ТОЛЬКО В ОДНО МЕСТО
                    self.users[from_id][peer_id] = commander.Commander(self.api_token, self.group_id, from_id, peer_id,
                                                                       msg_type)
                    self.users[from_id][peer_id].handle_message(msg_text)

                else:
                    self.users[from_id][peer_id].handle_message(msg_text)

            elif event.type == VkBotEventType.MESSAGE_EVENT:
                if event.object['payload'].get('text') == "Клавиатура отключена":
                    r = self.vk_api.messages.sendMessageEventAnswer(
                        event_id=event.object['event_id'],
                        user_id=from_id,
                        peer_id=peer_id,
                        event_data=json.dumps(event.object['payload']))
                    self.send_msg(peer_id, message='клавиатура отключена',
                                  keyboard=open('keyboards/turn_off_keyboard.json', "r", encoding="UTF-8").read())
                elif event.object['payload'].get('text') == "Подбираю пару...":
                    r = self.vk_api.messages.sendMessageEventAnswer(
                        event_id=event.object['event_id'],
                        user_id=from_id,
                        peer_id=peer_id,
                        event_data=json.dumps(event.object['payload']))
                    self.users[from_id][peer_id].handle_message('/старт')
                elif event.object['payload'].get('text') == "Добавляем в избранное...":
                    r = self.vk_api.messages.sendMessageEventAnswer(
                        event_id=event.object['event_id'],
                        user_id=from_id,
                        peer_id=peer_id,
                        event_data=json.dumps(event.object['payload']))
                    self.users[from_id][peer_id].handle_message('/нравится')

                elif event.object['payload'].get('text') == "Больше этот человек не попадется...":
                    r = self.vk_api.messages.sendMessageEventAnswer(
                        event_id=event.object['event_id'],
                        user_id=from_id,
                        peer_id=peer_id,
                        event_data=json.dumps(event.object['payload']))
                    self.users[from_id][peer_id].handle_message('/не нравится')

                elif event.object['payload'].get('text') == "Загружаем избранных...":
                    r = self.vk_api.messages.sendMessageEventAnswer(
                        event_id=event.object['event_id'],
                        user_id=from_id,
                        peer_id=peer_id,
                        event_data=json.dumps(event.object['payload']))
                    self.users[from_id][peer_id].handle_message('/избранные')

                elif event.object['payload'].get('text') == "Загружаем черный список...":
                    r = self.vk_api.messages.sendMessageEventAnswer(
                        event_id=event.object['event_id'],
                        user_id=from_id,
                        peer_id=peer_id,
                        event_data=json.dumps(event.object['payload']))
                    self.users[from_id][peer_id].handle_message('/не нравится')






    @staticmethod
    def create_keyboard():
        kbrd = keyboard.VkKeyboard(one_time=False)
        kbrd.add_callback_button("Старт", keyboard.VkKeyboardColor.PRIMARY, payload={"type": "show_snackbar", "text": "Подбираю пару..."})
        kbrd.add_line()
        kbrd.add_button("Не нравится", keyboard.VkKeyboardColor.NEGATIVE, payload={"type": "show_snackbar", "text": "Больше этот человек не попадется..."})
        kbrd.add_callback_button("Нравится", keyboard.VkKeyboardColor.POSITIVE, payload={"type": "show_snackbar", "text": "Добавляем в избранное..."})
        kbrd.add_line()
        kbrd.add_callback_button("Показать избранное", keyboard.VkKeyboardColor.PRIMARY,
                                 payload={"type": "show_snackbar", "text": "Загружаем избранных..."})
        kbrd.add_callback_button("Показать черный список", keyboard.VkKeyboardColor.PRIMARY,
                                 payload={"type": "show_snackbar", "text": "Загружаем черный список..."})
        kbrd.add_callback_button("Отключить клавиатуру", keyboard.VkKeyboardColor.NEGATIVE, payload={"type": "show_snackbar", "text": "Клавиатура отключена"})
        return kbrd.get_keyboard()
