from bs4 import BeautifulSoup
import grequests
import requests
import time
import conf as CFG

def get_movies_url(url, headers):
    """parse top-250 page and return tuple of lists of movies name and its references (without domain)"""
    response = requests.get(url, headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    titlelist = soup.findAll(class_="titleColumn")

    top_ref_list = []
    top_name_list = []
    for items in titlelist:
        top_ref_list.append(items.find("a").get('href'))
        top_name_list.append(items.find("a").contents[0])
    return (top_name_list, top_ref_list)


def get_response_1(film_url, header):
    try:
        response = requests.get(film_url, header)
        return response
    except Exception:
        raise ConnectionError("Connection error during request directors of %s" % film_url)


def get_directors(response):
    """Parsing single page by film_url and return list of directors. Header is standart header of request"""
    soup = BeautifulSoup(response.content, 'html.parser')
    director_soup = soup.select_one('span:-soup-contains("Director")')
    if director_soup is None:  # for uniq case when Director is not in span
        director_soup = soup.find_all(class_="ipc-metadata-list-item__content-container")[0] # container with directors list
    else:
        director_soup = director_soup.next_sibling # in usual take next container with director list
    directors_list = []
    for ref in director_soup.findAll('a'):
        directors_list.append(ref.contents[0])
    return directors_list


def collect_directors_requests(SITE_URL, movies_list):
    """"""
    """RECON_ATTEMPTS_NUM = 10
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }"""
    directors_list = []
    counter = 0
    for film_url in movies_list[1]:
        for attempt in range(CFG.RECON_ATTEMPTS_NUM):
            try:
                response = get_response_1(SITE_URL + film_url, CFG.HEADERS)
                directors_list.append(get_directors(response))
                print(counter, end=" ")
                counter += 1
                break
            except ConnectionError:
                time.sleep(3)

            except RuntimeError:
                directors_list.append('')
                counter += 1
                break
                print("Check film ", SITE_URL + film_url)
    return directors_list


def collect_directors_grequests(SITE_URL, movies_list):
    directors_list = []
    counter = 0
    BATCH_SIZE = 10
    i = 0
    req_batch = []
    for film_url in movies_list[1]:
        req_batch.append(SITE_URL + film_url)
        i += 1
        if i < BATCH_SIZE:
            continue
        i = 0
        rs = (grequests.post(u) for u in req_batch)
        req_batch = []
        responses = grequests.map(rs)
        for response in responses:
            try:
                directors_list.append(get_directors(response))
                print(counter, end=" ")
                counter += 1
            except RuntimeError:
                directors_list.append('')
                counter += 1
                print("Check film ", SITE_URL + film_url)
    return directors_list


def print_movies_dir(movies_list, directors_list):
    """printint top-250 movies in format asked. In input lists ordered in same order by movie with same len"""
    for i in range(len(movies_list)):
        print(str(i + 1), "-", movies_list[i], "-", ', '.join(directors_list[i]))

def main():
    # Set request headers to be look like brauser
    HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    TOP_URL = 'https://www.imdb.com/chart/top?ref_=nv_mv_250'
    SITE_URL = 'https://www.imdb.com'

    movies_list = get_movies_url(TOP_URL, HEADERS)

    directors_list = collect_directors_requests(SITE_URL, movies_list)

    """directors_list = []

    counter = 0
    RECON_ATTEMPTS_NUM = 5
    BATCH_SIZE = 10
    i = 0
    req_batch = []
    for film_url in movies_list[1]:"""





    '''for attempt in range(RECON_ATTEMPTS_NUM):
        try:
            response = get_response_1(SITE_URL + film_url, HEADERS)
            directors_list.append(get_directors(response)) 
            print(counter, end=" ")
            counter += 1
            break
        except ConnectionError:
            time.sleep(3)

        except RuntimeError:
            directors_list.append('')
            counter += 1
            break
            print("Check film ", SITE_URL + film_url)'''

    print_movies_dir(movies_list[0], directors_list)


if __name__ == '__main__':
    main()