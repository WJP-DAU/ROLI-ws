import re
import time
import requests
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup

def get_individual_data(id):
    full_href = f'https://web.barreauduniger.ne/{id}'
    
    r = requests.get(full_href)
    s =  BeautifulSoup(r.content, 'lxml')

    full_name = s.find('h5', class_ = 'card-title fw-bold text-center').text.strip()
    print(f'Retrieving information for {full_name}')

    country       = 'Niger'
    title         = 'NA'
    generic_title = 'NA'
    given_name    = 'NA'
    family_name   = 'NA'
    gender        = 'NA'
    organization  = 'NA'
    mobile        = 'NA'
    languages     = 'NA'
    practice      = 'NA'
    position      = 'NA'

    contact_card = s.find('p', class_ = 'card-text')
    try:
        phone = contact_card.find('i', class_ = 'fa fa-phone-square').next_sibling.strip()
        phone = re.search(
            r'Téléphone: (.*?)(?:$)', phone
        ).group(1).strip()
    except AttributeError:
        phone = 'Not Found'

    try: 
        email = contact_card.find('i', class_ = 'fa fa-envelope').next_sibling.strip()
    except AttributeError:
        email = 'Not Found'
    
    try:
        address = s.find('h5', class_ = 'card-text').find('small').text.strip()
    except AttributeError:
        address = 'Not Found'


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
        "position"        : position,
        "organization"    : organization,
        "phone"           : phone,
        "mobile"          : mobile,
        "practice"        : practice,
        "full_href"       : full_href,
        "address"         : address
    }

    time.sleep(1)

    return lawyer_entry


def run_stage_1():

    results = []
    for i in range(1, 130):
        try:
            data = get_individual_data(i)
            results.append(data)
        except Exception as e:
            print(f"Error processing ID {i}: {e}")
            continue  # Skip to the next iteration if an error occurs
    
    master_data = pd.DataFrame(results)
    master_data.to_csv("data/niger_barreauduniger.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage not in [1]:
        print("Invalid stage")
        return None
    

if __name__ == "__main__":
    run(1)