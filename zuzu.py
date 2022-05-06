import json
import time
from pprint import pprint
import pandas as pd
import requests
import vk_api
import config


# vk = vk_api.VkApi(token=config.vk_api_user_token)
# api = vk.get_api()
def search_user_pair_info(city, age_from, age_to):
    # Добавить идентификацию - если написала девушка, изменить sex на 2
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


# table_info = pd.DataFrame(search_user_pair_info(49, 23, 24))
# for i in search_user_pair_info(49, 23, 24):
#     print(i)


def get_best_three_photo(owner_id):
    user_url = 'https://api.vk.com/method/' + 'photos.get'
    user_params = {
        'access_token': config.vk_api_user_token,
        'v': config.version,
        'owner_id': owner_id,
        'album_id': 'profile',
        'photo_sizes': '1',
        'extended': '1'
    }
    req = requests.get(user_url, params=user_params).json()
    most_popular = dict()
    for photo in req['response']['items']:
        sizes = photo['sizes']
        likes = photo['likes']['count']
        comments = photo['comments']['count']
        popularity = likes + comments
        max_size_url = max(sizes, key=get_largest)['url']
        max_size_photo = max(sizes, key=get_largest)['type']
        most_popular[popularity] = max_size_url

    new_sorted_dict = dict(sorted(most_popular.items(), key=lambda x: x[0], reverse=True))
    result = []
    for key, value in new_sorted_dict.items():
        if len(result) != 3:
            result.append(value)

    return result



def get_largest(size_dict):
    # Выясняю, горизонтально или вертикально-ориентирована фотография,
    # что бы далее мог отсортировать по нужному параметру словари

    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    return size_dict['height']


# for i in get_best_three_photo(20246948):
#     print(i)
print(get_best_three_photo(20246948))
