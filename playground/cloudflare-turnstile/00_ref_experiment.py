login_url = 'https://masiro.me/admin/auth/login'

import  requests

resp = requests.get(login_url)
print(resp.status_code)

# 403