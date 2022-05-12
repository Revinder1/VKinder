from commander import Commander
from server import Server
import config
import sys

server1 = Server(config.vk_api_token, 212988687, "server1")
# vk_api_token - API токен, который мы ранее создали
# 212988687 - id сообщества-бота
# "server1" - имя сервера

server1.start()

