import requests
import os
import re

CATEGORY = "Populus tremula"

SPARQL_URL = "https://query.wikidata.org/sparql"

COMMONS_API = "https://commons.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": "star-carr-image-search/1.0 (roman.rous@atlas.cz)"
}


DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def safe_filename(name, max_length=120):
    # Remove "File:" prefix
    name = name.replace("File:", "")

    # Replace invalid Windows characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)

    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Truncate to avoid MAX_PATH issues
    if len(name) > max_length:
        base, ext = name.rsplit('.', 1)
        name = base[:max_length - len(ext) - 1] + '.' + ext

    return name

def get_category_pages(category, limit=5):
    # params = {
    #     "action": "query",
    #     "list": "categorymembers",
    #     "cmtitle": f"Category:{category}",
    #     "cmtype": "file",
    #     "cmlimit": limit,
    #     "format": "json",
    # }
    params = {
        "action": "query",
        "generator": "categorymembers",
        "gcmtitle": f"Category:{category}",
        "gcmtype": "file",
        "gcmlimit": limit,

        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": 512,
        "iiurlheight": 400,

        "format": "json"
    }

    r = requests.get(COMMONS_API, params=params, headers=HEADERS)
    r.raise_for_status()
    
    # for page in pages.values():
    #     info = page["imageinfo"][0]

    #     print({
    #         "title": page["title"],
    #         "thumb_url": info["thumburl"],
    #         "thumb_width": info["thumbwidth"],
    #         "thumb_height": info["thumbheight"],
    #         "original_width": info["width"],
    #         "original_height": info["height"],
    #         "mime": info["mime"],
    #     })
    
    return r.json()["query"]["pages"]


def get_file_url(page):
    # params = {
    #     "action": "query",
    #     "titles": filename,
    #     "prop": "imageinfo",
    #     "iiprop": "url",
    #     "format": "json",
    # }
    # r = requests.get(COMMONS_API, params=params, headers=HEADERS)
    # r.raise_for_status()

    # pages = r.json()["query"]["pages"]
    # page = next(iter(pages.values()))
    # print(page["imageinfo"][0])
    #print(page)
    return page["imageinfo"][0]["thumburl"]


def download_file(url, filename):
    filename = safe_filename(filename)
    r = requests.get(url, headers=HEADERS, stream=True)
    r.raise_for_status()

    path = os.path.join(DOWNLOAD_DIR, filename)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded: {filename}")

query = """
SELECT ?category WHERE {
  ?item wdt:P225 "Betula pendula".
  ?item wdt:P373 ?category.
}
"""

# r = requests.get(
#     SPARQL_URL,
#     params={"format": "json", "query": query},
#     headers={"User-Agent": "MyBot/1.0"}
# )

# category = r.json()["results"]["bindings"][0]["category"]["value"]
# print("Commons category:", category)

pages = get_category_pages(CATEGORY,20)

for page in pages:
    
    #print(pages[page])    
    title = pages[page]["title"]              # e.g. "File:Quercus robur leaf.jpg"
    filename = title.replace("File:", "")

    url = get_file_url(pages[page])
    print("File URL:", url)
    download_file(url, filename)
