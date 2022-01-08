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


def scape_app_data(soup: bs4.BeautifulSoup):
    app_data = {"date": datetime.date.today(), "time": datetime.datetime.utcnow().strftime("%r")}
    try: app_data["name"] = soup.select_one(".description-wrapper .title-container h3").text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = ", ".join([md["src"] for md in soup.select("div.product-description img")])
    except: app_data["images"] = None
    try: app_data["logo"] = soup.select_one('img[alt="Logo"]')["src"]
    except: app_data["logo"] = None
    try: app_data["category"] = soup.select_one(".product-title").text.strip()
    except: app_data["category"] = None
    try: app_data["details"] = soup.select_one("div.product-description").text.strip()
    except: app_data["details"] = None
    try: app_data["rating_count"] = re.search("[0-9]+", soup.select_one("span.rating-count").text.strip()).group()
    except: app_data["rating_count"] = None
    try: app_data["rating"] = re.search("[0-9]+", soup.select_one(".rating-number").text.strip()).group()
    except: app_data["rating"] = None
    try: app_data["tagline"] = soup.select_one(".description-wrapper p").text.strip()
    except: app_data["tagline"] = None
    try: app_data["priceline"] = [div.select_one("div:last-child").text.strip() for div in soup.select(".details-panel .detail-item") if "PRICE" in div.text.upper()][0]
    except: app_data["priceline"] = "Paid"
    try: app_data["developer"] = [spacer.text.strip() for spacer in soup.select(".sidebar .details .spacer") if "Published by" in spacer.text][0]
    except: app_data["developer"] = None
    try: app_data["timeline"] = soup.select_one(".description-wrapper p").text.strip()
    except: app_data["timeline"] = None
    try: app_data["info"] = soup.select_one(".product-desc").text.strip()
    except: app_data["info"] = None
    try: app_data["developer"] = [div.select_one("div:last-child").text.strip() for div in soup.select(".details-panel .detail-item") if "AUTHOR" in div.text.upper()][0]
    except: app_data["developer"] = None
    try: app_data["version"] = [div.select_one("div:last-child").text.strip() for div in soup.select(".details-panel .detail-item") if "VERSION" in div.text.upper()][0]
    except: app_data["version"] = None
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=300)
        url = "https://www.zendesk.com/apps/directory/"
        driver.get(url)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, "div.load-more-wrapper button")))
        while True:
            try:
                wait.until(presence_of_element_located((By.CSS_SELECTOR, "div.load-more-wrapper button")))
                more_button = driver.find_element_by_css_selector("div.load-more-wrapper button")
                more_button.click()
            except: break
        all_app_links = [f'https://www.zendesk.com{a_el.get_attribute("href")}' for a_el in driver.find_elements_by_css_selector("#results .grid .icon-hit-component a.no-text-decoration")]
        all_apps_data = []
        all_app_links = list(set(all_app_links))
        for link in all_apps_links:
            try:
                driver.get(link)
                try:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, ".detail-item")))
                except:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "a.review-scroll-trigger")))
                app_data_html = driver.find_element_by_css_selector(".marketplace-banner").parent
                app_data = scape_app_data(bs4.BeautifulSoup(app_data_html.get_attribute("innerHTML"), features="html.parser"))
                try: app_data["contact"] = modal.find_element_by_partial_link_text("Contact Us").get_attribute("href")
                except: app_data["contact"] = None
                try: app_data["website"] = modal.find_element_by_partial_link_text("Website").get_attribute("href")
                except: app_data["website"] = None
                app_data["url"] = link
                all_apps_data.append(app_data)
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

