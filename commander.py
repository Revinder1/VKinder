import random
from random import randrange
import server
import user_initialiser


class Commander(server.Server):
    def __init__(self, api_token, group_id):
        super().__init__(api_token, group_id)
        self.user = user_initialiser.UserInfo

    def handle_message(self, msg):
        if msg.startswith("Моё имя"):
            return self.user.get_user_name()


        """
        Функция принимающая сообщения пользователя
        :param msg: Сообщение
        :return: Ответ пользователю, отправившему сообщение
        """
        pass


    def get_img_attachment(self, image_url, peer_id):
        attachments = []
        image = self.session.get(image_url, stream=True)
        photo = self.upload.photo_messages(photos=image.raw)[0]
        attachments.append(f'photo{photo["owner_id"]}_{photo["id"]}')
        return ','.join(attachments)

