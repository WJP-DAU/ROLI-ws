import re
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_lawyer_info(href):

    full_href = f'https://www.uianet.org{href}'
    r = requests.get(full_href)
    s = BeautifulSoup(r.text, 'lxml')

    full_name = s.find('h1').text.strip().replace('\t', '').title()
    full_name = re.sub(r'\s+', ' ', full_name)

    try:
        organization = s.find('p', class_ = 'cabinet').text.strip().title()
    except AttributeError:
        organization = 'Not Found'

    try:
        address = s.find('p', class_ = 'adresse').text.strip().replace('\t', '').replace('\n| \n', ', ')
        address = re.sub(r'\s+', ' ', address)
    except AttributeError:
        address = 'Not Found'

    try:
        country = s.find('span', class_ = 'pays').text.strip().title()
    except AttributeError:
        country = 'Not Found'

    try:
        email = s.find('a', class_='email').get('href').replace('mailto:', '').strip()
    except AttributeError:
        email = 'Not Found'

    try:
        phone = s.find('li', class_='phone').find('a').text.strip()
    except AttributeError:
        phone = 'Not Found'

    try:
        website = s.find('li', class_='web').find('a').get('href').strip()
    except AttributeError:
        website = 'Not Found'

    try:
        linkedin = s.find('a', class_='linkedin').get('href').strip()
    except AttributeError:
        linkedin = 'Not Found'

    lawyer_entry = {
        "country"         : country,
        "title"           : "NA",
        "given_name"      : "NA",
        "family_name"     : "NA",
        "full_name"       : full_name,
        "gender"          : "NA",
        "email"           : email,
        "languages"       : "NA",
        "position"        : "NA",
        "organization"    : organization,
        "phone"           : phone,
        "mobile"          : "NA",
        "practice"        : "NA",
        "full_href"       : full_href,
        "address"         : address,
        "website"         : website,
        "linkedin"       : linkedin
    }

    time.sleep(1)

    return lawyer_entry

def run_stage_1():

    results = []

    for page in range(1, 196):

        print(f'Getting information listed on page {page}')
        listing_url = f'https://www.uianet.org/en/directory?page={page}'

        r = requests.get(listing_url)
        s = BeautifulSoup(r.content, 'lxml')

        lawyer_cards = s.find('ul', class_ = 'list-annuaire-page').find_all('li')

        for card in lawyer_cards:
            href = card.find('h3').find('a').get('href').strip()
            lawyer_entry = get_lawyer_info(href)
            results.append(lawyer_entry)
        
        time.sleep(1)

    master_data = pd.DataFrame.from_dict(results)
    master_data.to_csv("data/global_uianet.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage not in [1]:
        print("Invalid stage")
        return None


if __name__ == "__main__":
    run(1)