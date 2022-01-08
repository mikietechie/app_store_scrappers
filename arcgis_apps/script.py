"""
Work done by Mike Zinyoni
Python JavaScript engineer

!actively looking for a job!!!!
Done
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


def scape_app_data(soup: bs4.BeautifulSoup):
    app_data = {"date": datetime.date.today(), "time": datetime.datetime.utcnow().strftime("%r")}
    try: app_data["name"] = soup.select_one("p.listingsGallery-header-heading.avenir-light").text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = ", ".join([(url[:-4] if url.endswith('");,') else url[:-3] ) for url in re.findall(r'(https?://[^\s]+)', ", ".join([div["style"] for div in soup.select(".listingsGallery-mainimage, .listingsGalleryThumbnail")]))])
    except: app_data["images"] = None
    try: app_data["logo"] = soup.select_one(".listingsGallery-header-logo img").get("src")
    except: app_data["logo"] = None
    try: app_data["details"] = soup.select_one(".tab-contents .column-14").text.strip()
    except: app_data["details"] = None
    try: app_data["tagline"] =soup.select_one("p.listingsGallery-header-subheader.avenir-light").text.strip()
    except: app_data["tagline"] = None
    try: app_data["info"] = soup.select_one(".network-table .network-table-content").text.strip()
    except: app_data["info"] = None
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=300)
        # get category links
        url = "https://www.esri.com/en-us/arcgis-marketplace/products"
        driver.get(url)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, '.pagination .pagination-wrapper a.btn.btn-transparent.font-size-0')))
        last_page_link = driver.find_elements_by_css_selector(".pagination .pagination-wrapper a.btn.btn-transparent.font-size-0")[-1]
        page_links = [
            f"https://www.esri.com/en-us/arcgis-marketplace/products?p={page}" for page in range(1, int(last_page_link.text.strip()))
        ]
        print("page links:\t:", page_links)
        all_app_links, urls = [], []
        for page_link in page_links:
            driver.get(page_link)
            wait.until(presence_of_element_located((By.CSS_SELECTOR, '.marketplace-cards .card .cards-simple.lighttheme a')))
            app_links = driver.find_elements_by_css_selector('.marketplace-cards .card .cards-simple.lighttheme a')
            all_app_links.extend([app_link.get_attribute("href") for app_link in app_links])
        all_app_links = list(set(all_app_links))
        print("all app links:\t:", all_app_links)
        all_apps_data = []
        for app_link in all_app_links:
            try:
                driver.get(app_link)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, '#listing-gallery .listingsGallery .listingsGallery-wrapper')))
                driver.implicitly_wait(1)
                app_data_html = driver.find_element_by_css_selector("#main-content #root")
                data = scape_app_data(bs4.BeautifulSoup(app_data_html.get_attribute("innerHTML"), features="html.parser"))
                data["url"] = app_link
                all_apps_data.append(data)
            except Exception as e:
                #raise e
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
            exit()
        raise e


if __name__ == "__main__":
    main()
    exit()

