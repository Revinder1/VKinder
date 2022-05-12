from commander import Commander
from server import Server
import config
import sys

server1 = Server(config.vk_api_token, ********, "server1")
# vk_api_token - API токен, который мы ранее создали
# ******* - id сообщества-бота
# "server1" - имя сервера

server1.start()
