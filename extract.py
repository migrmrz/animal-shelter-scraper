from bs4 import BeautifulSoup
import requests
from googleapiclient.discovery import build
import pickle
import datetime
from pprint import pprint


# Extraction of shelter links from all states
def extract_shelter_links() -> list:
    url = "https://www.dogloversdigest.com/adoption/state-list-of-shelters-" \
        "and-rescue-organizations/"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    entry_content = soup.find(class_="entry-content")
    shelter_elements = entry_content.select("ul")[0].select("li a")
    shelter_urls = []
    for shelter_link in shelter_elements:
        shelter_urls.append(shelter_link.get("href"))
    return shelter_urls


# Extraction of shelter info from every shelter of the list
def extract_shelter_details(shelter_urls: list) -> list:
    # Main structure that will store every shelter detail in a dict structure
    shelters_details = []
    for url in shelter_urls:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        entry_content = soup.find(class_="entry-content")
        shelter_html_list = entry_content.select("p")[1:]
        # Structure that will contain details of each shelter: name, url,
        # address, phone and email
        shelter_dict = {}
        for shelter_html_data in shelter_html_list:
            if shelter_html_data.select("a")[0].get_text() == "here":
                continue
            name = shelter_html_data.select("a")[0].get_text()
            shelter_dict['name'] = name
            url = shelter_html_data.select("a")[0].get("href")
            shelter_dict['url'] = url
            shelter_text = shelter_html_data.get_text(separator=" ").strip()
            if "Email" in shelter_text:
                shelter_text, email = shelter_text.split(" Email:")
                shelter_dict['email'] = email.strip()
            else:
                shelter_dict['email'] = ""
            if "Phone" in shelter_text:
                shelter_text, phone = shelter_text.split(" Phone:")
                shelter_dict['phone'] = phone.strip()
            else:
                shelter_dict['phone'] = ""
            if shelter_text != name:
                address = shelter_text[len(name):].strip()
                shelter_dict['address'] = address
            else:
                shelter_dict['address'] = ""
            shelters_details.append(shelter_dict)
            shelter_dict = {}
    return shelters_details


# Insertion of individual shelter info to Google Sheets
def create_google_service():
    """
        Creates and returns a Google Sheets service from a pickle file
        previously generated.
    """
    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)
    service = build("sheets", "v4", credentials=credentials)
    return service


def insert_data(shelters_details: list) -> dict:
    """
        Creates a spreadsheet and then inserts the extracted information
    """
    # Creates google sheets service
    service = create_google_service()
    date_str = str(datetime.date.today())
    spreadsheet_name = "Animal-Shelters_{}".format(date_str)
    spreadsheet_body = {
        "properties": {
            "title": spreadsheet_name
        }
    }
    # Creates spreadsheet
    create_request = service.spreadsheets().create(body=spreadsheet_body)
    create_response = create_request.execute()
    spreadsheet_id = create_response['spreadsheetId']
    # Edits spreadsheet to insert data
    range_ = "Sheet1!A2:E2"
    insert_data_option = "INSERT_ROWS"
    value_input_option = "RAW"
    values = []
    temp_row = []
    for shelter in shelters_details:
        for row in shelter.values():
            temp_row.append(row)
        values.append(temp_row)
        temp_row = []
    value_range_body = {
        "values": values
    }
    edit_request = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption=value_input_option,
        insertDataOption=insert_data_option,
        body=value_range_body)
    edit_response = edit_request.execute()
    pprint(edit_response['updates'])
    return spreadsheet_name


urls = extract_shelter_links()
details = extract_shelter_details(urls)
print("Extracted a total of {} records".format(len(details)))
print("Initiating insertion to Google Sheets...")
print("Insertion results:\n")
insert_data(details)
print("Done!")
