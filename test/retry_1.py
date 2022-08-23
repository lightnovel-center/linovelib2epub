import time


def fetch_page(url, retry_max=3):
    current_num_of_request = 0

    # 0,1,2,3
    while current_num_of_request <= retry_max:
        try:
            print('request')
            2/0
        except Exception as e:
            time.sleep(3)

        current_num_of_request += 1
        print('current_num_of_request: ', current_num_of_request)

    return None

# fetch_page(url='',retry_max=0)
fetch_page(url='',retry_max=3)