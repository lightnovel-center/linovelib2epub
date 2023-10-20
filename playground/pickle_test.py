import pickle

pickle_path = '../pickle/masiro.me_1039.pickle'
with open(pickle_path, 'rb') as fp:
    novel = pickle.load(fp)

print(novel)
