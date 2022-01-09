"""
Work done by Mike Zinyoni
Python JavaScript engineer

!actively looking for a job!
"""

import bs4, os, csv, datetime, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

driver_path = os.environ['CHROME_WEB_DRIVER']
local = True
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')


def scape_app_data(soup: bs4.BeautifulSoup, url=None):
    app_data = {"url": url, "date": datetime.date.today(), "time": datetime.datetime.utcnow().strftime("%r")}
    try: app_data["name"] = soup.select_one(".c-details-hero h3").text.strip() # name
    except: app_data["name"] = None
    try: app_data["media"] = ",".join([item.get("src") for item in soup.select_one("u-carousel-swipe").select("img, iframe, video")])
    except: app_data["media"] = None
    try: app_data["release_date"] = soup.select_one("#release-notes-version").find_next_sibling("div").text.strip()
    except: app_data["release_date"] = None
    try: app_data["details"] = (soup.select_one("#details") or soup.select_one("#overview")).text.strip()
    except: app_data["details"] = None
    try: app_data["version"] = soup.select_one("#release-notes-version").text.strip()
    except: app_data["version"] = None
    try: app_data["logo"] = soup.select_one(".c-details-hero img")["src"]
    except: app_data["logo"] = None
    try: app_data["category"] = ", ".join([a.text.strip() for a in [h5 for h5 in soup.select("h5") if h5.text.lower() == "CATEGORY & CONTENTS".lower()][0].find_next_sibling("div").select("a")])
    except: app_data["category"] = None
    try: app_data["licensing"] = [h5 for h5 in soup.select("h5") if h5.text.lower() == "licensing".lower()][0].find_next_sibling("a")["href"]
    except: app_data["licensing"] = None
    try: app_data["downloads"] = soup.select_one("#login-to-download").find_previous_siblings("div")[0].select_one(".u\.txt\:lg").text.strip()
    except: app_data["downloads"] = 0
    try: app_data["installs"] = soup.select_one("#login-to-download").find_previous_siblings("div")[1].select_one(".u\.txt\:lg").text.strip()
    except: app_data["installs"] = 0
    try: app_data["headline"] = soup.select_one(".c-details-hero div.no-hover.splunk.details-page").text.strip() 
    except: app_data["headline"] = None
    try: app_data["rating"] = len(soup.select_one("sb-details-star-buttons").select("svg.highlighted"))
    except: app_data["rating"] = None
    try: app_data["reviews_count"] = re.search("[0-9]+", soup.select_one("sb-details-star-review-count").text.strip()).group()
    except: app_data["reviews_count"] = None
    try: app_data["developer"] = [h5 for h5 in soup.select("h5") if h5.text.lower() == "Built by".lower()][0].find_next_sibling("a").text.strip()
    except: app_data["developer"] = None
    try: app_data["website"] = "https://splunkbase.splunk.com"+[h5 for h5 in soup.select("h5") if h5.text.lower() == "Built by".lower()][0].find_next_sibling("a")["href"]
    except: app_data["website"] = None
    try:
        compatibility = [h5 for h5 in soup.select("h5") if h5.text.lower() == "compatibility".lower()][0]
        app_data["compatibility"] = re.compile("[\s]{2,}").sub(" ", "\n".join([el.text.strip() for el in compatibility.find_next_siblings("div") + compatibility.find_next_siblings("sb-release-select")]))
    except: app_data["compatibility"] = None
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=30)
        # get category links
        all_app_links = []
        for url in ["https://splunkbase.splunk.com/archive/apps/#/order/popular/product/all", "https://splunkbase.splunk.com/apps/#/product/all"]:
            driver.get(url)
            wait.until(presence_of_element_located((By.ID, "loadmore")))
            i = 0
            while i < 2000:
                i += 1
                try:
                    wait.until(presence_of_element_located((By.ID, "loadmore")))
                    # more_button = driver.find_element_by_id("loadmore")
                    # more_button.click()
                    driver.execute_script("document.querySelector('#loadmore').click()")
                except:
                    break
            all_app_links.extend([f"https://splunkbase.splunk.com{link['href']}" for link in bs4.BeautifulSoup(driver.page_source, features="html.parser").select("sb-app-card-v2-1 a")])
        all_apps_data = []
        wait = WebDriverWait(driver, timeout=10)
        all_app_links = list(set(all_app_links))
        for link in all_app_links:
            try:
                driver.get(link)
                try:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "#release-notes-version")))
                except:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "#overview")))
                page_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
                all_apps_data.append(scape_app_data(page_soup, link))
                #break # to be removed
            except Exception as e:
                print("Exception:\t", str(e))
        driver.close()
        with open("apps.csv", "w", encoding="utf-8") as file:
            csv_writer = csv.DictWriter(file, list(all_apps_data[0].keys()))
            csv_writer.writeheader()
            for app in all_apps_data:
                csv_writer.writerow(app)
        print("!!! Done With The Job !!!")
    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            driver.close()
            exit()
        raise e


if __name__ == "__main__":
    main()
    exit()

