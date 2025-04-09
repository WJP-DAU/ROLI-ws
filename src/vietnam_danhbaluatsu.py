import re
import time
import json
import pickle
import requests
import pandas as pd
from openai import OpenAI
from bs4 import BeautifulSoup
from json.decoder import JSONDecodeError

def run_stage_1():

    results = []

    for n_page in range(1, 291):

        print(f"Retrieving information from page no: {n_page}")

        url = f"https://www.danhbaluatsu.com/luat-su/p{n_page}"
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "lxml")

        lawyers_list = soup.find("div", class_ = "mmid").find_all("div", class_ = "right")

        for lawyer in lawyers_list:

            # Extracting data from entry
            country       = "Vietnam"
            title         = "Luật sư"
            generic_title = True
            given_name    = "NA"
            family_name   = "NA"

            try:
                full_name = lawyer.find("h2").find("a").text.strip()
            except AttributeError:
                full_name = "Not Found"

            gender = "NA"
            
            try: 
                email = lawyer.find("span", string = re.compile("Email:")).find_parent().text
                email = re.search(
                    r"Email: (.*?)(?:$)", email
                ).group(1).strip()
            except AttributeError:
                email  = "Not Found"
            
            languages = "NA"
            position  = "NA"
            
            try: 
                organization = lawyer.find("span", string = re.compile("Tổ chức hành nghề:")).find_parent().find("a").text
            except AttributeError:
                organization  = "Not Found"

            try: 
                phone  = lawyer.find("span", string = re.compile("Điện thoại:")).find_parent().text
                phone  = re.search(
                    r"Điện thoại: (.*?)(?: - Hotline|$)", phone
                ).group(1).strip()
            except AttributeError:
                phone  = "Not Found"

            try: 
                mobile = lawyer.find("span", string = re.compile("Di động:")).find_parent().text
                mobile = re.search(
                    r"Di động: (.*?)(?: - Hotline|$)", mobile
                ).group(1).strip()
            except AttributeError:
                mobile  = "Not Found"

            practice = "NA"

            lawyer_href = lawyer.find("h2").find("a").get("href")
            full_href   = f"https://www.danhbaluatsu.com{lawyer_href}"
            
            # Extra info from the website
            try: 
                hotline = lawyer.find("span", class_ = "hotline").text.strip()
            except AttributeError:
                hotline  = "Not Found"
            try: 
                bar_association = lawyer.find("span", string = re.compile("Đoàn luật sư:")).find_next_sibling("a").text.strip()
            except AttributeError:
                bar_association  = "Not Found"

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
                "hotline"         : hotline,
                "bar_association" : bar_association
            } 

            results.append(lawyer_entry)

        time.sleep(1)
        print(f"===============================================")

    master_data = pd.DataFrame(results)
    master_data.to_csv("data/vietnam_danhbaluatsu/vietnam_danhbaluatsu.csv", index = False, encoding = "utf-8")


def get_system_prompt():
    system_prompt = """
    You are a very helpful assistant. I will be passing you some information in Vietnamese and I will need your help in performing two tasks. First,
    splitting a full name into given, middle, and last name. Second, identifying if the information I'm providing contains specific segments 
    I'm interested in and, if true, structuring those segments in a JSON format for me. I will be providing more information regarding the JSON
    schema after I pass you the information. Very important to note is that you will always have to perform the first task (name splitting), 
    but the second task will only be performed in specific cases that I will flag to you.
    """

    return system_prompt


def process_info(full_name, url):

    print(f"Processing information for individual: {full_name}")

    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, "lxml")

    try:
        bio_container = soup.find("div", class_ = "boxgen").find_all("p")
        bio_elements  = [p.text.strip() for p in bio_container]
        bio = "\n".join(bio_elements)
        status = "Profile processed"
    except AttributeError: # In some cases the provided URL is not available...
        print("Error... profile NOT found!!")
        bio = ""
        status = "Profile missing"

    if bio:
        context_prompt = get_context_prompt(
            only_name = False,
            full_name = full_name,
            bio = bio
        )
        print("Bio content found")

    else:
        context_prompt = get_context_prompt(
            only_name = True,
            full_name = full_name,
            bio = bio
        )
        print("Bio content NOT found")

    history = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user",   "content": context_prompt}
    ]

    client = OpenAI(
        base_url = "http://localhost:1910/v1",
        api_key  = "sk-1234"
    )

    chat_completion = client.chat.completions.create(
        messages = history,
        model    = "deepseek-r1-distill-qwen-32b"
        # model    = "deepseek-r1-distill-qwen-7b"
    )

    answer = chat_completion.choices[0].message.content
    answer_split = answer.split("</think>")

    think_content = answer_split[0].strip().replace("<think>\n", "")
    json_content  = answer_split[1].strip()
    json_content  = json_content.replace("json", "").replace("```", "").strip()

    results_json = json.loads(json_content)
    results_json["full_name"] = full_name
    results_json["url"] = url
    results_json["rsn"] = think_content
    results_json["status"] = status

    if not bio:
        results_json["expertise"]        = "No biography information"
        results_json["languages"]        = "No biography information"
        results_json["years_experience"] = "No biography information"
        results_json["public_servant"]   = "No biography information"
    
    print("=============================================================================")
    
    return results_json


def get_context_prompt(only_name, full_name, bio):

    if only_name:

        prompt = f"""
        I will provide you a Vietnamese full name and I need your help in splitting this name into given name, middle name, and family name. 
        Additionally, I will need you to guess the gender (male or female) based on the name that I'm giving you. You will have to base your 
        guess in your 
        knowledge of Vietnamese naming conventions. 

        The Vietnamese name is: {full_name}.

        Please structure your answer following this JSON schema:
        {{
            "given_name"  : given name of the person from the full_name,
            "middle_name" : middle name of the person from the full_name,
            "family_name" : family name of the person from the full_name.
            "gender"      : gender based on the full name given.
        }}

        Please take into account the following:

        - If you are not able to provide an answer for any of these keys, please fill that key with a "UNCERTAIN" string for me to know that 
        it is not possible for you to know the answer to that specific field.
        - Please process the given, middle, and family names in title case.
        - You can answer with "NONE" if you believe that the name has no middle name.
        - Some strings passed as "full name" could be corrupted with additional information such as professional and academic titles such as 
        "lawyer" or "master". Please feel free to drop them and not include them in your answer.
        - Your answer should include ONLY the resulting JSON with your answers. Exclude any additional comments from the answer please.

        Thank you and you can begin now.
        """
    
    else:

        prompt = f"""
        I will provide you a Vietnamese full name and I need your help in splitting this name into given name, middle name, and family name. 
        Additionally, I will need you to guess the gender (male or female) based on the name that I'm giving you. You will have to base your guess in 
        your  knowledge of Vietnamese naming conventions. 

        The Vietnamese name is: {full_name}.

        Additionally, I have some biographic information available for this person. I will need you to read it carefully and assess if the information
        provided mentions any of the following fields:

        1. Areas of legal expertise that this person has, if mentioned in the provided text. For example, criminal, litigation, commercial, 
        civil, human rights, and so on.
        2. Languages spoken by the person, if mentioned.
        3. If the person is CURRENTLY working for the government or not.
        4. Years of experience, if mentioned.

        The biographic information that we have from this person is the following: {bio}

        Please structure your answer following this JSON schema:
        {{
            "given_name"       : given name of the person from the full_name,
            "middle_name"      : middle name of the person from the full_name,
            "family_name"      : family name of the person from the full_name,
            "gender"           : gender based on the full name given,
            "expertise"        : areas of legal expertise mentioned in the biographic information,
            "languages"        : languages spoken by the person, if any,
            "years_experience" : years of experience that this person has as a lawyer if it is mentioned in the biographic information,
            "public_servant"   : if the person is a public servant, answer or fill this field as TRUE, if the person is working as a privatre 
            lawyer please answer or fill this field as FALSE.
        }}

        Please take into account the following:

        - If you are not able to provide an answer for any of these keys, please fill that key with a "UNCERTAIN" string for me to know that 
        it is not possible for you to know the answer to that specific field.
        - Please process the given, middle, and family names in title case.
        - You can answer with "NONE" if you believe that the name has no middle name.
        - Some strings passed as "full name" could be corrupted with additional information such as professional and academic titles such as 
        "lawyer" or "master". Please feel free to drop them and not include them in your answer.
        - If there is no information in the biographic information that I passed to you that helps you answer or infere the fields of 
        expertise, languages, years of experience, and public servant, please answer or fill those fields with "NOT MENTIONED".
        - Your answer should include ONLY the resulting JSON with your answers. Exclude any additional comments from the answer please.

        Thank you and you can begin now.
        """
    
    return prompt


def run_stage_2(start = 1):
    
    data = pd.read_csv("data/vietnam_danhbaluatsu/vietnam_danhbaluatsu.csv")
    data = data.iloc[896:]
    target_values = dict(zip(data["full_name"], data["full_href"]))

    processed_data_list = []
    current = start

    for name,href in target_values.items():
        try:
            r = process_info(name, href)
        except JSONDecodeError:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!! JSON DECODE ERROR !!!!!")
            print("!!!! Trying again...   !!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            try:
                r = process_info(name, href)
            except JSONDecodeError:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("!!!! JSON DECODE ERROR !!!!!")
                print("!!!! SKIPPING PERSON... !!!!")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                continue
        
        processed_data_list.append(r)
        current = current + 1
        if current % 10 == 0 :
            print("---- SAVING PARTIAL DATA ----")
            with open("data/vietnam_danhbaluatsu/vietnam_danhbaluatsu_partial.pkl", "wb") as f:
                pickle.dump(processed_data_list, f)
            print("---- PARTIAL DATA SAVED ----")
    
    master_data = pd.DataFrame.from_dict(processed_data_list)
    master_data.to_csv("data/vietnam_danhbaluatsu/vietnam_danhbaluatsu_processed.csv", index = False, encoding = "utf-8")


def run(stage):
    if stage == 1:
        run_stage_1()
    if stage == 2:
        run_stage_2()
    if stage not in [1,2]:
        print("Invalid stage")
        return None


if __name__ == "__main__":
    run(1)
    # run(2)