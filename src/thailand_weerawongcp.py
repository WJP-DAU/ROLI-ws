import re
import time
import requests
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup

def get_individual_data(object):
    href_attr = object.find('a').get('href')
    full_href = f'https://www.weerawongcp.com/{href_attr}'
    
    r = requests.get(full_href)
    r.encoding = r.apparent_encoding
    s =  BeautifulSoup(r.text, 'lxml')

    full_name = s.find('h1').text.strip()
    print(f'Retrieving information for {full_name}')

    country = 'Thailand'
    title   = 'NA'
    generic_title = 'NA'
    given_name  = 'NA'
    family_name = 'NA'
    gender      = 'NA'
    organization = 'Weerawong, Chinnavat & Partners Ltd.'
    mobile = 'NA'

    contact_object = s.find('h3', string = re.compile('Contact')).find_next_siblings()
    try:
        phone = contact_object[0].text
        phone = re.search(
            r'T: (.*?)(?:$)', phone
        ).group(1).strip()
        phone
    except AttributeError:
        phone = 'Not Found'

    try: 
        email = contact_object[2].find('a').get('href').strip()
        email = re.search(
            r'mailto:(.*)$', email
        ).group(1).strip()
    except AttributeError:
        email = 'Not Found'

    try:
        languages = s.find('h3', string = re.compile('Languages')).find_next_siblings('p')[0].text.strip()
    except AttributeError:
        languages = 'Not Found'

    bio = s.find_all('table')[2].find('tr').find_all('td')[1].text.strip()

    lawyer_entry = {
        "country"         : country,
        "title"           : title,
        "generic_title"   : generic_title,
        "given_name"      : given_name,
        "family_name"     : family_name,
        "full_name"       : full_name,
        "gender"          : gender,
        "email"           : email,
        "languages"       : languages,
        # "position"        : position,
        "organization"    : organization,
        "phone"           : phone,
        "mobile"          : mobile,
        # "practice"        : practice,
        "full_href"       : full_href,
        "bio"             : bio
    }

    time.sleep(1)
    
    return lawyer_entry


def get_page_data(object):
    table_html = object.find('table', class_ = 'sptb1')
    page_data  = pd.read_html(StringIO(str(table_html)))[0]
    page_data.columns = ['full_name', 'practice', 'position']

    lawyer_data_list = [
        get_individual_data(person) 
        for person in table_html.find_all('td', class_ = 'xname')
    ]
    lawyer_data = pd.DataFrame(lawyer_data_list)

    return [page_data, lawyer_data]


def run_stage_1():

    results = []

    for n_page in range(0, 7):

        print(f'Retrieving information for page {n_page}')
        url = f'https://www.weerawongcp.com/people-list.php?type=practice&key=&order=name_asc&page={n_page}'

        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'lxml')

        page_data_cb = get_page_data(soup)
        page_data = pd.merge(
            page_data_cb[0], 
            page_data_cb[1], 
            on = 'full_name', 
            how = 'inner'
        )
        results.append(page_data)

        print("=============================================================================")
    
    master_data = pd.concat(results)
    master_data.to_csv("data/thailand_weerawongcp/thailand_weerawongcp.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage not in [1]:
        print("Invalid stage")
        return None
    

if __name__ == "__main__":
    run(1)
