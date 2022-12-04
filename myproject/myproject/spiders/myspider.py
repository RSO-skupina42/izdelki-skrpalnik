from myproject.itemLoaders import ProgramLoader
from myproject.items import MyprojectItem

import scrapy
from scrapy import Request
import re


url_link_elem = "https://www.spar.si/online{elem}"
url_sadje = "https://search-spar.spar-ics.com/fact-finder/rest/v4/" \
            "search/products_lmos_si" \
            "?query=*" \
            "&q=*" \
            "&page={pagenum}" \
            "&hitsPerPage={hits_per_page}" \
            "&filter=category-path:{category_id}" \
            "&substringFilter=pos-visible:81701"

# "https://search-spar.spar-ics.com/fact-finder/rest/v4/search/products_lmos_si" \
# "?query=*" \
# "&q=*" \
# "&hitsPerPage=72" \
# "&page=2" \
# "&filter=category-path:S1" \
# "&substringFilter=pos-visible:81701"


# curl 'https://search-spar.spar-ics.com/fact-finder/rest/v4/search/products_lmos_si?' \
#      'query=*' \
#      '&q=*' \
#      '&page=1' \
#      '&hitsPerPage=72' \
#      '&filter=category-path:S1' \
#      '&substringFilter=pos-visible:81701'
# -H 'Accept: application/json, text/javascript, */*; q=0.01'
# -H 'Accept-Language: en-GB,en;q=0.5'
# -H 'Accept-Encoding: gzip, deflate, br'
# -H 'Origin: https://www.spar.si'
# -H 'Connection: keep-alive'
# -H 'Referer: https://www.spar.si/'
# -H 'Sec-Fetch-Dest: empty'
# -H 'Sec-Fetch-Mode: cors'
# -H 'Sec-Fetch-Site: cross-site'
# -H 'DNT: 1' -H 'Sec-GPC: 1'

def extract_size(text):
    rez_size, rez_unit = None, None

    regex = r"(\d+\s*[\.,]?\d*)(G|KG|DG|L|ML)"
    size = re.search(regex, text, re.IGNORECASE)

    if size and size.group(1) and size.group(2):
        rez_size, rez_unit = size.group(1), size.group(2)



    return rez_size, rez_unit


class MyspiderSpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = ['spar-ics.com']

    def start_requests(self):
        for cid in range(1, 16, 1):
            cid = f"S{cid}"
            yield Request(url_sadje.format(pagenum=1, hits_per_page=72, category_id=cid), cb_kwargs={"cid": cid})

    def parse(self, response, cid=None):
        # print(response.text)
        data_json = response.json()

        for hit in data_json["hits"]:
            yield self.parse_details(hit)

        paging = data_json["paging"]
        if paging.get("nextLink"):
            page_num_next = paging["nextLink"]["number"]
            hits_per_page = paging["hitsPerPage"]
            # filters = paging["nextLink"]["filters"]

            next_url = url_sadje.format(pagenum=page_num_next,
                                        hits_per_page=hits_per_page,
                                        category_id=cid)
            # print(next_url)
            yield Request(next_url, cb_kwargs={"cid": cid})

    def parse_details(self, data):
        loader = ProgramLoader(item=MyprojectItem())

        elem_id = data["id"]
        title = data["masterValues"].get("title", "").strip()
        price = data["masterValues"].get("best-price", "").strip()
        sales_unit = data["masterValues"].get("sales-unit", "").strip()

        short_description = data["masterValues"].get("short-description")
        short_description = short_description if short_description else data["masterValues"].get("short-description-2", "").strip()
        description = data["masterValues"].get("description", "").strip()
        desc = short_description.strip() + " " + description.strip()

        categories = data["masterValues"].get("category-name", "").strip()
        url_elem = url_link_elem.format(elem=data["masterValues"].get("url", "").strip())

        rez_size, rez_unit = extract_size(title)
        size = f"{rez_size} {rez_unit}"

        loader.add_value("elem_id", elem_id)
        loader.add_value("title", title)
        loader.add_value("price", price)
        loader.add_value("sales_unit", sales_unit)
        # loader.add_value("short_description", short_description)
        loader.add_value("description", desc)
        loader.add_value("category", categories)
        loader.add_value("url", url_elem)
        loader.add_value("size", size)

        return loader.load_item()
