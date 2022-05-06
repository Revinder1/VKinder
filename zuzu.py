import json
import time
from pprint import pprint

import requests
import vk_api
import config


# vk = vk_api.VkApi(token=config.vk_api_user_token)
# api = vk.get_api()
def search_user_pair_info(city, age_from, age_to):
    params = {
        'access_token': config.vk_api_user_token,
        'v': config.version,
        'count': 1000,
        'sort': 1,
        'has_photo': 1,
        'city': city,
        'age_from': age_from,
        'age_to': age_to,
        'sex': 1,
        'birth_month': 1,
        'status': 6,
        'fields': 'city,sex,relation,bdate'
        }


    for i in range(1, 13):
        if i == 1:
            res = requests.get('https://api.vk.com/method/' + 'users.search', params=params).json()
            user_list = [j for j in res['response']['items']]
        else:
            res = requests.get('https://api.vk.com/method/' + 'users.search', params=params).json()
            for user in res['response']['items']:
                user_list.append(user)
        params['birth_month'] += 1


    for i in user_list:
        if (i.get('city') is None) or i['city']['id'] != 49 or i.get('relation') is None:
            user_list.remove(i)
        else:
            yield i




for user in search_user_pair_info(49, 23, 24):
    print(user)

# with open('pump.json', 'a', encoding='utf-8') as f:
#     json.dump(user_list, f, indent=2, ensure_ascii=False)