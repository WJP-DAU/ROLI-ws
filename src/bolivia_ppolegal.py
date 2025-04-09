import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_lawyer_info(p):

    full_name = p.find('h3').text.strip().title()

    print(f'Getting information for {full_name }')

    contact_box = p.find('div', class_ = 'contacto-profesional').find_all('p')
    try:
        email = contact_box[0].find('a').text.strip()
    except AttributeError:
        email = 'Not Found'
    try:  
        phone = contact_box[1].text.strip()
    except IndexError:
        phone = contact_box[0].text.strip()
    position = p.find('div', class_ = 'links-socios').text.strip()
    try:
        practice = p.find('h5').find_next_sibling('p').text.strip()
    except AttributeError:
        practice = 'Not Found'
    url = p.find('div', class_ = 'img-plus').find('a').get('href')

    lawyer_entry = {
        "country"         : "Bolivia",
        "title"           : "NA",
        "given_name"      : "NA",
        "family_name"     : "NA",
        "full_name"       : full_name,
        "gender"          : "NA",
        "email"           : email,
        "languages"       : "NA",
        "position"        : position,
        "organization"    : "PPO Legal & Tax",
        "phone"           : phone,
        "mobile"          : "NA",
        "practice"        : practice,
        "full_href"       : url
    }

    return lawyer_entry

def run_stage_1():
    listing_url = 'https://www.ppolegal.com/en/professionals/'
    response = requests.get(listing_url)
    parsed_response = BeautifulSoup(response.content, 'lxml')

    lawyer_list = parsed_response.find_all('div', class_ = 'col-md-12 col-profesionales')
    results = [get_lawyer_info(x) for x in lawyer_list]

    master_data = pd.DataFrame.from_dict(results)
    master_data.to_csv("data/bolivia_ppolegal.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage not in [1]:
        print("Invalid stage")
        return None


if __name__ == "__main__":
    run(1)