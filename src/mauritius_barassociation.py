import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

def run_stage_1():

    url = "https://www.mauritiusbarassociation.com/bar-council-members-list/"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    table_html = soup.find("table", class_ = "tablepress tablepress-id-18")

    master_data = pd.read_html(StringIO(str(table_html)))[0]
    master_data["Surname"] = master_data["Surname"].str.title()
    master_data.to_csv("../data/mauritius_barassociation/mauritius_barassociation.csv", index = False, encoding = "utf-8")

def run(stage):
    if stage == 1:
        run_stage_1()
    if stage > 1:
        print("Invalid stage")
        return None

if __name__ == "__main__":
    run(1)