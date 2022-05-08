import requests
import vk_api
from vk_api import VkUpload

import config
from vk_api.vk_api import VkApi


class UserInfo:

    def __init__(self, user_id):
        self.vk_token = config.vk_api_token
        self.vk_user_token = config.vk_api_user_token
        self.vk_api = vk_api.VkApi(token=self.vk_token).get_api()
        self.user_id = user_id


    def get_user_gender(self):
        response = self.vk_api.users.get(user_id=self.user_id, fields='sex')
        print(response)
        switcher = {
            1: 'Женский',
            2: 'Мужской',
            0: 'Не указан'
        }
        return switcher[response[0]["sex"]]

    def get_user_name(self):
        """ Получаем имя пользователя"""
        response = self.vk_api.users.get(user_id=self.user_id)
        return f'{response[0]["first_name"]}'


    def get_user_city(self):
        """ Получаем город пользователя"""
        return self.vk_api.users.get(user_id=self.user_id, fields="city")[0]["city"]['id']


    def search_user_pair_info(self, city, age_from, age_to):
        # Добавить идентификацию - если написала девушка, изменить sex на 2
        params = {
            'access_token': self.vk_user_token,
            'v': config.version,
            'count': 1000,
            'has_photo': 1,
            'city': city,
            'age_from': age_from,
            'age_to': age_to,
            'sex': 1,
            'birth_month': 1,
            'status': 6,
            'fields': 'city,sex,relation,bdate'
        }
        if self.get_user_gender() == 'Женский':
            params['sex'] = 2
        # Сбор данных по поиску, обходя лимит в 1000 пользователей
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
            if (i.get('city') is None) or i['city']['id'] != city or i.get('relation') is None:
                user_list.remove(i)
            else:
                link = f'https://vk.com/id{i["id"]} '
                i = {'id': i["id"], 'link': link, 'first_name': i['first_name'], 'last_name': i['last_name'], 'city': i['city']['title']}
                yield i

    @staticmethod
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
            most_popular[popularity] = max_size_url

        new_sorted_dict = dict(sorted(most_popular.items(), key=lambda x: x[0], reverse=True))
        result = []
        for key, value in new_sorted_dict.items():
            if len(result) != 3:
                result.append(value)
        return result


def get_largest(size_dict):
    # Выясняю, горизонтально или вертикально-ориентирована фотография,
    # чтобы далее мог отсортировать по нужному параметру словари в функции get_best_three_photo()

    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    return size_dict['height']