from requests import Session
from bs4 import BeautifulSoup

sessao = Session()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
}


def get_html(url, params: dict = {}) -> tuple[str, int]:
    req = sessao.get(url, params=params, headers=headers)
    if "charset" not in req.headers.get("Content-Type", "").lower():
        req.encoding = req.apparent_encoding
    return (req.text, req.status_code)


def get_json(url, params: dict = {}) -> tuple[dict, int]:
    req = sessao.get(url, params=params, headers=headers)
    if "charset" not in req.headers.get("Content-Type", "").lower():
        req.encoding = req.apparent_encoding
    return req.json(), req.status_code


def get_soup(url, params: dict = {}) -> tuple[BeautifulSoup, int]:
    html, status = get_html(url, params)
    return (BeautifulSoup(html, "html.parser"), status)
