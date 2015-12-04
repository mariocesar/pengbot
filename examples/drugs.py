import requests
import urllib
from bs4 import BeautifulSoup
from pengbot.api import command, listener, env


def search_drug(term):
    searchparms = lambda term: urllib.parse.urlencode({
        'searchterm': term,
        'phrase': 'all',
        'language': 'english',
        'results_per_page': 10,
        'sources': ['consumer']
    })

    response = requests.get('http://www.drugs.com/search.php?%s' % searchparms(term))

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        search_result = soup.select('#content .search-result', limit=1)

        if search_result:
            search_result = search_result.pop()
            drug_url = search_result.find('h3').find('a').attrs['href']
            response = requests.get(drug_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            desc = soup.select('[itemprop=description]')
            if desc:
                return desc.pop().text
            else:
                jump = soup.select('#content h3 a')
                if jump:
                    newterm = jump.pop().text
                    return search_drug(newterm)


@command(alias=['hi'])
def hello():
    return 'Hello'


@command(alias=['buscar'])
def search(search_term):
    result = search_drug(search_term)
    if result:
        return result
    else:
        return "No encontre un medicamento o ingrediente con el nombre %s" % search_term
