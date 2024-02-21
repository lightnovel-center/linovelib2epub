# https://github.com/ultrafunkamsterdam/undetected-chromedriver

import undetected_chromedriver as uc

if __name__ == '__main__':
    driver = uc.Chrome(headless=True, use_subprocess=False)
    # driver.get('https://nowsecure.nl')
    # driver.save_screenshot('nowsecure.png')

    login_url = 'https://masiro.me/admin/auth/login'
    driver.get(login_url)
    driver.save_screenshot('masiro_login.png')
    # 2024/2/18 依旧无法跳过，寄
