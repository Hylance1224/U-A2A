import os
import pickle
import config

path = ''

class Dictionary():
    def __init__(self):
        f = open('dictionary.txt', 'rb')
        self.dictionary = pickle.load(f)
        f.close()

    def __len__(self):
        return len(self.dictionary)

    def get_dictionary(self):
        return self.dictionary

    def transfer_api_num(self, api):
        num = self.dictionary.index(api)
        return num + len(config.ns)

    def transfer_num_api(self, num):
        api = self.dictionary[num-len(config.ns)]
        return api

    def translating_num(self, num_list):
        api_list = []
        for num in num_list:
            api_list.append(self.transfer_num_api(num))
        return api_list

    def numbering_api(self, api_list):
        num_list = []
        for api in api_list:
            num_list.append(self.transfer_api_num(api))
        return num_list


def create_dictionary():
    all_animation_api = []
    dirs = os.listdir(path)
    for dir in dirs:
        path_animation = path + '/' + dir
        files = os.listdir(path_animation)
        for file in files:
            if 'animationApi' in file:
                f = open(file)
                api_list = f.readlines()
                for api in api_list:
                    if api not in all_animation_api:
                        all_animation_api.append(api)
    all_animation_api.sort()
    f = open('dictionary.txt', 'wb')
    pickle.dump(all_animation_api, f)


if __name__ == '__main__':
    dictionary = Dictionary()
    dict = dictionary.get_dictionary()
    print(len(dict))




