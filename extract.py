from bs4 import BeautifulSoup
import requests


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
            name = shelter_html_data.select("a")[0].get_text()
            shelter_dict['name'] = name
            url = shelter_html_data.select("a")[0].get("href")
            shelter_dict['url'] = url
            shelter_text = shelter_html_data.get_text(separator=" ").strip()
            if "Email" in shelter_text:
                shelter_text, email = shelter_text.split(" Email:")
                shelter_dict['email'] = email.strip()
            if "Phone" in shelter_text:
                shelter_text, phone = shelter_text.split(" Phone:")
                shelter_dict['phone'] = phone.strip()
            if shelter_text != name:
                address = shelter_text[len(name):].strip()
                shelter_dict['address'] = address
            shelters_details.append(shelter_dict)
            shelter_dict = {}
    return shelters_details


urls = extract_shelter_links()
details = extract_shelter_details(urls)
print(len(details))


# Insertion of shelter info to Google Sheet
