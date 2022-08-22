import pickle

# file = open("../pickle/3211_content_dict.pickle", 'rb')
# file = open("../pickle/3211_image_dict.pickle", 'rb')
file = open("../pickle/3211_basic_info.pickle", 'rb')
dict = pickle.load(file)
file.close()

print(dict)