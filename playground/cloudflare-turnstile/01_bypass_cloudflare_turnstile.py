import cloudscraper

login_url = 'https://masiro.me/admin/auth/login'

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
# scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
print(scraper.get(login_url).text)  # => "<!DOCTYPE html><html><head>..."

# https://github.com/VeNoMouS/cloudscraper
# 结论：skip无效，寄。
