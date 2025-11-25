import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time
from backend.utils.logger import get_logger

logger = get_logger('web')

def obeys_robots(url):
    # very minimal robots check
    try:
        parsed = urlparse(url)
        robots = urljoin(f'{parsed.scheme}://{parsed.netloc}', '/robots.txt')
        r = requests.get(robots, timeout=5)
        if r.status_code != 200:
            return True
        return 'Disallow' not in r.text
    except Exception:
        return False

def fetch_and_summarize(url, max_chars=3000):
    if not obeys_robots(url):
        raise PermissionError('robots.txt disallows scraping')
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    text = ' '.join([p.get_text() for p in soup.find_all('p')])
    summary = text[:max_chars]
    return {'url': url, 'summary': summary}
