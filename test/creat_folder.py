import os

book_id = 3211

basic_info_pickle_path = f'../pickle/'
path_exists = os.path.exists(basic_info_pickle_path)
if not path_exists:
    os.makedirs(basic_info_pickle_path)