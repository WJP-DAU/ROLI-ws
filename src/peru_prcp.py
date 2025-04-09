import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_lawyer_info(url):
    r = requests.get(url)
    p = BeautifulSoup(r.content, 'lxml')

    full_name = p.find('h1').text.strip()
    email = p.find('li', class_ = 'details__email').find('a').text.strip()
    phone = p.find('li', class_ = 'details__phone').find('a').text.strip()
    position = p.find('h3').text.strip()
    try:
        practice_areas = p.find('ul', class_ = 'area-de-abagado').find_all('li')
        practice = ', '.join([a.text.strip() for a in practice_areas])
    except AttributeError:
        practice = 'Not Found'

    lawyer_entry = {
        "country"         : "Peru",
        "title"           : "NA",
        "given_name"      : "NA",
        "family_name"     : "NA",
        "full_name"       : full_name,
        "gender"          : "NA",
        "email"           : email,
        "languages"       : "NA",
        "position"        : position,
        "organization"    : "Payet, Rey, Cauvi, Pérez Abogados",
        "phone"           : phone,
        "mobile"          : "NA",
        "practice"        : practice,
        "full_href"       : url
    }

    return lawyer_entry


def run_stage_1():
    listing_url = 'https://prcp.com.pe/en/people/?post_types=senior-expert%2Ccounsel%2Casociado-principal%2Csocio%2Casociado&sf_paged='

    results = []

    for page in range(1,41):
        
        print(f'Getting results for page no. {page}')

        master_url = f'{listing_url}{page}'
        master_response = requests.get(master_url)
        parsed_master_response = BeautifulSoup(master_response.content, 'lxml')

        lawyers_list = parsed_master_response.find('div', class_ = 'posts-row-grid').find_all('article')
        lawyers_references = [x.find('h2').find('a').get('href') for x in lawyers_list]

        page_results = [get_lawyer_info(x) for x in lawyers_references]

        results.extend(page_results)

        time.sleep(1)
    
    master_data = pd.DataFrame.from_dict(results)
    master_data.to_csv("data/peru_prcp.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage not in [1]:
        print("Invalid stage")
        return None


if __name__ == "__main__":
    run(1)