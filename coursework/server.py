import json
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

    # Отправляем сообщение пользователю в лс/группу с возможностью прикреплений файлов и клавиатур
    def send_msg(self, send_id, message=None, attachment=None, keyboard=None):
        return self.vk_api.messages.send(peer_id=send_id, attachment=attachment,
                                         message=message, keyboard=keyboard,
                                         random_id=random.randrange(10 ** 7))

    # Функция для обработки url фотографий, чтобы в дальнейшем отправлять их пользователю
    def get_img_attachment(self, _list):
        attachments = []
        for url in _list:
            image = self.session.get(url, stream=True)
            photo = self.upload.photo_messages(photos=image.raw)[0]
            attachments.append(f'photo{photo["owner_id"]}_{photo["id"]}')
        return ','.join(attachments)

    # Меню-подсказка пользователю
    def menu_bot(self, from_id, peer_id):
        self.send_msg(peer_id,
                      message=f'Добро пожаловать, {user_initialiser.UserInfo(from_id).get_user_name()}! Я - бот для '
                              f'знакомств! '
                              'Прежде чем мы начнем знакомства, укажите возраст в формате Х-Х (Прим.: 18-20)')

    def start(self):
        try:
            for event in self.long_poll.listen():  # Слушаем сервер
                # Пришло новое сообщение
                if event.type == VkBotEventType.MESSAGE_NEW:
                    new_dict = dict()
                    peer_id = event.object["message"]["peer_id"]
                    from_id = event.object["message"]["from_id"]
                    msg_text = event.object["message"]["text"]

                    # Проверка на наличие связанных юзер-класс в словаре
                    if from_id not in self.users:
                        new_dict[peer_id] = commander.Commander(self.api_token, self.group_id, from_id, peer_id)
                        self.users[from_id] = new_dict
                        # Отправляем меню новому пользователю
                        self.menu_bot(from_id, peer_id)
                        # Отправляем сообщение на обработку
                        self.users[from_id][peer_id].handle_message(msg_text)

                    # Если один и тот же юзер отправляет сообщения с лс и группы, добавить в словарь peer_id группы
                    # и связать с классом
                    elif peer_id not in self.users[from_id]:
                        # Приходится обновлять значение в словаре, иначе при отправке с лс/группы атрибуты класса
                        # Commander не обновляются и отправляются только в одно место (если писать сразу с разных мест)
                        self.users[from_id][peer_id] = commander.Commander(self.api_token, self.group_id,
                                                                           from_id, peer_id)
                        self.users[from_id][peer_id].handle_message(msg_text)

                    else:
                        self.users[from_id][peer_id].handle_message(msg_text)

                # обрабатываем нажатие Callback-кнопок
                elif event.type == VkBotEventType.MESSAGE_EVENT:
                    if event.object['payload'].get('text') == "Клавиатура отключена":
                        self.vk_api.messages.sendMessageEventAnswer(
                            event_id=event.object['event_id'],
                            user_id=from_id,
                            peer_id=peer_id,
                            event_data=json.dumps(event.object['payload']))
                        self.send_msg(peer_id, message='клавиатура отключена',
                                      keyboard=open('keyboards/turn_off_keyboard.json', "r", encoding="UTF-8").read())
                    else:
                        self.switcher(event, from_id, peer_id)

        # При ручном отключении бота во время загрузок, отключить клавиатуру и завершить работу
        except KeyboardInterrupt:
            self.send_msg(peer_id, message='клавиатура отключена, До Свидания',
                          keyboard=open('keyboards/turn_off_keyboard.json', "r", encoding="UTF-8").read())

    # Свитчер для обработки Callback-кнопок, сопоставляет payload-инфу и отправляет нужные запросы в обработку сообщений
    def switcher(self, event, from_id, peer_id):
        texts = {
            "Подбираю пару...": '/старт',
            "Добавляем в избранное...": '/нравится',
            "Больше этот человек не попадется...": '/не нравится',
            "Загружаем избранных...": '/избранные',
            "Загружаем черный список...": '/черный список',
            "Загружаю следующего пользователя чс...": '/дальше чс',
            "Загружаю следующего избранного...": '/дальше избранные',
            "Удаляю из черного списка...": '/удалить из чс',
            "Удаляю из списка избранных...": '/удалить из избранных',
            "Возвращаемся к поиску партнера": '/вернуться'
        }
        if event.object['payload'].get('text') in texts:
            self.vk_api.messages.sendMessageEventAnswer(
                event_id=event.object['event_id'],
                user_id=from_id,
                peer_id=peer_id,
                event_data=json.dumps(event.object['payload']))
            self.users[from_id][peer_id].handle_message(texts[event.object['payload'].get('text')])

    # Создание главной клавиатуры с помощью vk_api
    @staticmethod
    def create_keyboard():
        kbrd = keyboard.VkKeyboard(one_time=False)
        kbrd.add_callback_button("Старт", keyboard.VkKeyboardColor.PRIMARY,
                                 payload={"type": "show_snackbar", "text": "Подбираю пару..."})
        kbrd.add_line()
        kbrd.add_callback_button("Не нравится", keyboard.VkKeyboardColor.NEGATIVE,
                                 payload={"type": "show_snackbar", "text": "Больше этот человек не попадется..."})
        kbrd.add_callback_button("Нравится", keyboard.VkKeyboardColor.POSITIVE,
                                 payload={"type": "show_snackbar", "text": "Добавляем в избранное..."})
        kbrd.add_line()
        kbrd.add_callback_button("Избранное", keyboard.VkKeyboardColor.PRIMARY,
                                 payload={"type": "show_snackbar", "text": "Загружаем избранных..."})
        kbrd.add_callback_button("Черный список", keyboard.VkKeyboardColor.PRIMARY,
                                 payload={"type": "show_snackbar", "text": "Загружаем черный список..."})
        kbrd.add_callback_button("Отключить клавиатуру", keyboard.VkKeyboardColor.NEGATIVE,
                                 payload={"type": "show_snackbar", "text": "Клавиатура отключена"})
        return kbrd.get_keyboard()

    # Создание клавиатуры для управления черным списком
    @staticmethod
    def create_bl_keyboard():
        kbrd = keyboard.VkKeyboard(one_time=False)
        kbrd.add_callback_button("Дальше", keyboard.VkKeyboardColor.PRIMARY,
                                 payload={"type": "show_snackbar", "text": "Загружаю следующего пользователя чс..."})
        kbrd.add_line()
        kbrd.add_callback_button("Вернуться к поиску", keyboard.VkKeyboardColor.SECONDARY,
                                 payload={"type": "show_snackbar", "text": "Возвращаемся к поиску партнера"})
        kbrd.add_line()
        kbrd.add_callback_button("Удалить из списка", keyboard.VkKeyboardColor.SECONDARY,
                                 payload={"type": "show_snackbar", "text": "Удаляю из черного списка..."})
        kbrd.add_line()
        kbrd.add_callback_button("Отключить клавиатуру", keyboard.VkKeyboardColor.NEGATIVE,
                                 payload={"type": "show_snackbar", "text": "Клавиатура отключена"})
        return kbrd.get_keyboard()

    # Создание клавиатуры для управления списком избранных
    @staticmethod
    def create_fav_keyboard():
        kbrd = keyboard.VkKeyboard(one_time=False)
        kbrd.add_callback_button("Дальше", keyboard.VkKeyboardColor.PRIMARY,
                                 payload={"type": "show_snackbar", "text": "Загружаю следующего избранного..."})
        kbrd.add_line()
        kbrd.add_callback_button("Вернуться к поиску", keyboard.VkKeyboardColor.SECONDARY,
                                 payload={"type": "show_snackbar", "text": "Возвращаемся к поиску партнера"})
        kbrd.add_line()
        kbrd.add_callback_button("Удалить из списка", keyboard.VkKeyboardColor.SECONDARY,
                                 payload={"type": "show_snackbar", "text": "Удаляю из списка избранных..."})
        kbrd.add_line()
        kbrd.add_callback_button("Отключить клавиатуру", keyboard.VkKeyboardColor.NEGATIVE,
                                 payload={"type": "show_snackbar", "text": "Клавиатура отключена"})
        return kbrd.get_keyboard()
