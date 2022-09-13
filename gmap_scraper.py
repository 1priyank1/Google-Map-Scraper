import time
import urllib.parse

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

text = input("Enter search text: ")
text = urllib.parse.quote_plus(text)

# Create google map url from entered text
url = "https://www.google.com/maps/search/" + text
print("url: ", url)

# add your chrome driver path here
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
browser.maximize_window()

# Load google map url
browser.get(url)
# browser.execute_script("document.body.style.zoom='25%';")
# browser.maximize_window()

google_places = []
places_data = []
actions = ActionChains(browser)
out_file = "google_places.csv"


def get_location_data(places):
    # columns = ['Name', 'Contact No.', 'Website', 'Address', "Rating", "Reviews", "Google Map link"]
    # with open(out_file, 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(columns)
    for place in places:
        # print(place['url'])
        # Load page into browser
        browser.get(place['url'])

        try:
            location = browser.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
            address = location.text
        except:
            address = ""
            pass
        try:
            phone_number = browser.find_element(By.CSS_SELECTOR, "[data-tooltip='Copy phone number']")
            number = phone_number.text
        except:
            number = ""
            pass
        try:
            web = browser.find_element(By.CSS_SELECTOR, "[data-item-id='authority']")
            website = web.text
        except:
            website = ""
            pass
        try:
            avg_rating = browser.find_element(By.XPATH,
                                              "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/div[2]/span[1]/span/span[1]")
            rating = avg_rating.text
        except:
            rating = ""
            pass
        try:
            total_reviews = browser.find_element(By.XPATH,
                                                 "//*[@id='QA0Szd']/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/div[2]/span[2]/span[1]/button")
            reviews = total_reviews.text
        except:
            reviews = ""
            pass

        try:
            row = [place['name'], number, website, address, rating, reviews, place["url"]]
            google_places.append(row)
            # print(row)
            # with open(out_file, 'a', newline='') as csvfile:
            #     writer = csv.writer(csvfile)
            #     writer.writerow(row)
        except Exception as er:
            print(er)
            pass
        time.sleep(1)
    df = pd.DataFrame(google_places,
                      columns=['Name', 'Number', 'Website', 'Address', "Rating", "Reviews", "Google Map link"])
    df.drop_duplicates(keep='first', inplace=True)
    df.to_csv(out_file, encoding='utf-8', index=False)


def get_list():
    try:
        scrollable_div = browser.find_element(By.CLASS_NAME, "m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd")
        while True:
            ActionChains(browser).scroll(0, 0, 0, 2000, origin=scrollable_div).perform()
            time.sleep(0.5)
            try:
                end_of_list = browser.find_element(By.CSS_SELECTOR,
                                                   "#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd.QjC7t > div.m6QErb.tLjsW.eKbjU")
                end_of_list_text = end_of_list.text
                if end_of_list_text.find("end of the list") != -1:
                    print("end of the list")
                    break
            except Exception as ex:
                # print(ex)
                pass
    except Exception as e:
        print(e)

    soup = BeautifulSoup(browser.page_source, "html.parser")
    div_places = soup.select('div[jsaction] > a[href]')
    print("places size: ", len(div_places))
    get_place_info(div_places)


def get_place_info(div_places):
    for div_place in div_places:
        place_info = {
            'url': div_place['href'],
            'name': div_place['aria-label'],
        }
        places_data.append(place_info)
        # print(place_info)
    time.sleep(1)
    get_location_data(places_data)


# Get place list
get_list()
