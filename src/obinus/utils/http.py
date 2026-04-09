from requests import Response, Session, request
from bs4 import BeautifulSoup, Tag
from obinus.utils.texto import normalizar

sessao = Session()

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
}


def _req(
    metodo: str,
    url: str,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    data: str | dict[str, str] | None = None,
) -> Response:
    res: Response = request(
        method=metodo,
        url=url,
        params=params,
        headers=HEADERS_BASE | (headers if headers else {}),
        data=data,
    )

    if res.status_code != 200:
        print(f"{url}: {res.status_code}")

    if "charset" not in res.headers.get("Content-Type", "").lower():
        res.encoding = res.apparent_encoding

    return res


def get_html(
    url,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    metodo: str = "GET",
    data: str | dict[str, str] | None = None,
) -> tuple[str, int]:
    res = _req(metodo, url, params, headers, data)
    return (res.text, res.status_code)


def get_json(
    url: str,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    metodo: str = "GET",
    data: str | dict[str, str] | None = None,
) -> object:
    res = _req(metodo, url, params, headers, data)
    return res.json()


def get_json_s(
    url: str,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    metodo: str = "GET",
    data: str | dict[str, str] | None = None,
) -> tuple[object, int]:
    res = _req(metodo, url, params, headers, data)
    return res.json(), res.status_code


def get_soup(
    url: str,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    metodo: str = "GET",
    data: str | dict[str, str] | None = None,
) -> BeautifulSoup:
    html, _ = get_html(url, params, headers, metodo, data)
    return BeautifulSoup(html, "html.parser")


def get_soup_s(
    url: str,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    metodo: str = "GET",
    data: str | dict[str, str] | None = None,
) -> tuple[BeautifulSoup, int]:
    html, status = get_html(url, params, headers, metodo, data)
    return BeautifulSoup(html, "html.parser"), status


def extrair_texto(tag: Tag | None) -> str | None:
    if not tag or tag is None:
        return None

    return normalizar("".join(tag.find_all(string=True, recursive=False)))
