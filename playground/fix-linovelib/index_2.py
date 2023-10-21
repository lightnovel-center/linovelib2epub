from bs4 import BeautifulSoup
import cloudscraper
scraper = cloudscraper.create_scraper(delay=10,   browser={'custom': 'ScraperBot/1.0',})
url = 'https://w.linovelib.com/novel/3279.html'
req = scraper.get(url)
print(req)