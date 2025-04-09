import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_additional_info(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    practice  = soup.find('div', {'id': 'services'}).find_all('li')
    practice  = [x.text.strip() for x in practice]
    practice  = '; '.join(practice)

    try: 
        sectors   = soup.find('div', {'id': 'sectors'}).find_all('li')
        sectors   = [x.text.strip() for x in sectors]
        sectors   = '; '.join(sectors)
        practice.extend(sectors)
    except AttributeError:
        print('Only one tab for sectors/practice')
        
    phone     = soup.find('p', class_ = 'team-phone').text.strip()
    try:
        linkedin = soup.find('p', class_ = 'team-linkedin').find('a').get('href').strip()
    except AttributeError:
        linkedin = 'Not Found'
    try:
        languages = soup.find('div', {'id': 'profile'}).find('p', string = re.compile('Languages')).find_next_sibling('ul').find_all('span', class_ = 's1')
        languages = [x.text.strip() for x in languages]
        languages = ', '.join(languages)
    except AttributeError:
        languages = 'Not Found'

    results = {
        'practice'  : practice,
        'languages' : languages,
        'phone'     : phone,
        'linkedin'  : linkedin
    }

    return results


def run_stage_1():

    url = 'https://www.kap.co.th/our-team/'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    lawyer_cards = soup.find('div', class_ = 'portfolio-items').find_all('div', class_ = 'portfolio-item')

    results = []
    counter = 1
    for lawyer in lawyer_cards:

        print(f'Getting information from subject no {counter}')

        country      =  'Thailand'
        title        = 'NA'
        gender       = 'NA' 
        organization = 'Kudun & Partners'
        mobile       = 'NA'

        caption = lawyer.find('div', class_ = 'partners-box-caption')

        full_name = caption.find('div', class_ = 'team-name').find_all('h3')
        given_name = full_name[0].text.strip().title()
        family_name = full_name[1].text.strip().title()
        full_name_joint = ' '.join([x.text.strip() for x in full_name]).title()

        print(f'Name: {full_name_joint}')

        position = caption.find('span', class_ = 'designation').text.strip()

        links = caption.find_all('a')

        email = links[0].get('href')
        email = re.search(
            r'mailto:(.*)', email
        ).group(1).strip()

        full_href = links[1].get('href')

        additional_info = get_additional_info(full_href)
        time.sleep(1)

        lawyer_entry = {
            "country"         : country,
            "title"           : title,
            # "generic_title"   : generic_title,
            "given_name"      : given_name,
            "family_name"     : family_name,
            "full_name"       : full_name_joint,
            "gender"          : gender,
            "email"           : email,
            "languages"       : additional_info['languages'],
            "position"        : position,
            "organization"    : organization,
            "phone"           : additional_info['phone'],
            "mobile"          : mobile,
            "practice"        : additional_info['practice'],
            "full_href"       : full_href,
            "linkedin"        : additional_info['linkedin']
        } 

        results.append(lawyer_entry)

        counter += 1
        print('=============================')
    
    master_data = pd.DataFrame.from_dict(results)
    master_data.to_csv("data/thailand_kap.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage not in [1]:
        print("Invalid stage")
        return None


if __name__ == "__main__":
    run(1)
    # run(2)