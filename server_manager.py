from server import Server
from config import vk_api_token

server1 = Server(vk_api_token, 212988687, "server1")
# vk_api_token - API токен, который мы ранее создали
# 212988687 - id сообщества-бота
# "server1" - имя сервера

server1.start()
