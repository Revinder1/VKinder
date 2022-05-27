from commander import Commander
from server import Server
import config


if __name__ == '__main__':
  server1 = Server(config.vk_api_token, config.group_id, "server1")
# vk_api_token - API токен, который мы ранее создали
# group_id - id сообщества-бота
# "server1" - имя сервера
  server1.start()
