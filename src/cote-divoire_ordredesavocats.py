import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

def run_stage_1():

    results = [] 

    for n_page in range(1, 48):

        print(f"Retrieving information from page no: {n_page}")

        url = f"https://app.ordredesavocats-ci.net/annuaire?page={n_page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        lawyers_html = soup.find_all("div", class_ = "col-xxl-3 col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs-6")

        for lawyer in lawyers_html:

            # Extracting data from entry
            country       = "Côte d'Ivoire"
            title         = "Maître"
            generic_title = True
            
            try:
                full_name = lawyer.find("div", class_ = "p-1 text-center").find("p", class_ = "mb-0 text-truncate f-w-600 pe-3 px-3").text.strip()
                full_name = re.search(r"Maître (.*?)(?:$)", full_name).group(1).strip()
            except AttributeError:
                full_name = "Not Found"
            
            gender = "NA"

            try:
                email = lawyer.find("a", class_ = "px-3 pb-0").get("href")
                email = re.search(
                    r"mailto:(.*?)(?:$)", email
                ).group(1).strip()
            except AttributeError:
                email = "Not Found"
            
            languages = "NA"
            position  = "NA"

            try:
                organization = lawyer.find("p", class_ = "text-truncate f-w-500 mb-0 px-4").text.strip().title()
            except AttributeError:
                organization = "Not Found"
            
            try:
                phone = lawyer.find("a", class_ = "btn btn-outline-primary btn-sm btn-pill border-0").text.strip()
            except AttributeError:
                phone = "Not Found"
            
            practice = "NA"

            try:
                full_href = lawyer.find("a", {"id": "info"}).get("href")
            except AttributeError:
                full_href = "Not Found"

            responsita = requests.get(full_href)
            soupita    = BeautifulSoup(responsita.text, "lxml")

            try:
                family_name = soupita.find("a", class_ = "text-perso-primary").text.strip().title()
            except AttributeError:
                family_name = "Not Found"

            try:
                given_name = soupita.find("div", class_ = "desc text-capitalize").text.strip().title()
            except AttributeError:
                given_name = "Not Found"
            
            try:
                href_cabinet = lawyer.find("a", {"id": "cabinet"}).get("href")
            except AttributeError:
                href_cabinet = "Not Found"
            
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
                "practice"        : practice,
                "full_href"       : full_href,
                "href_cabinet"    : href_cabinet
            } 

            results.append(lawyer_entry)

            time.sleep(1)
        print(f"===============================================")

    master_data = pd.DataFrame(results)
    master_data.to_csv("data/cote-divoire_ordredesavocats/cote-divoire_ordredesavocats.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage not in [1]:
        print("Invalid stage")
        return None


if __name__ == "__main__":
    run(1)
    # run(2)
