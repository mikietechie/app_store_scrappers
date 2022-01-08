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
    try: app_data["name"] = soup.select_one('h1[data-testid="product_name"]').text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = ", ".join([md["src"] for md in soup.select('aside[class="f1otqxop"] img')])
    except: app_data["images"] = None
    try: app_data["logo"] = soup.select_one('img[data-testid="product_icon"]')["src"]
    except: app_data["logo"] = None
    try: app_data["details"] = soup.select_one('div[data-testid="detail_description"]').text.strip()
    except: app_data["details"] = None
    try: app_data["sandboxed"] = soup.select_one('div[data-test-id="is-sandboxed-hover"]').text.strip()
    except: app_data["sandboxed"] = None
    try: app_data["priceline"] = soup.select_one(".f3llvvk:last-child").text.strip()
    except: app_data["priceline"] = "Paid"
    try: app_data["developer"] = soup.select_one('span[data-testid="author-name"]').text.strip()
    except: app_data["developer"] = None
    try: app_data["hosted_at"] = soup.select_one(".f1jofppb").text.strip()
    except: app_data["hosted_at"] = None
    try: app_data["works_with"] = [div.select_one("section") for div in soup.select(".f1o8vn7j .f1hiwvjl") if "Works with" in div.text][0].text.strip()
    except: app_data["works_with"] = None
    try: app_data["examples"] = ", ".join([a['href'] for a in [section.select("a") for section in soup.select(".f1o8vn7j section") if "Example Dashboards" in section.text][0]])
    except: app_data["examples"] = None
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=300)
        # get category links
        url = "https://extensiongallery.tableau.com/extensions?version=2021.1"
        driver.get(url)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, '.f8znxdr[data-testid="product-list"] a.f58v78i')))
        driver.implicitly_wait(10)
        all_apps_links = [
            f'https://extensiongallery.tableau.com{a.get_attribute("href")}' for a in driver.find_elements_by_css_selector('.f8znxdr[data-testid="product-list"] a.f58v78i')
        ]
        all_apps_links = list(set(all_apps_links))
        all_apps_data = []
        for link in all_apps_links:
            try:
                driver.get(link)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="detail_description"]')))
                app_data_el = driver.find_element_by_css_selector(".f1ed5j13")
                data = scape_app_data(bs4.BeautifulSoup(app_data_el.get_attribute("innerHTML"), features="html.parser"))
                try: data["developer_website"] = modal.find_element_by_partial_link_text("Developer Website").get_attribute("href")
                except: data["developer_website"] = None
                try: data["privacy_policy"] = modal.find_element_by_partial_link_text("Privacy Policy").get_attribute("href")
                except: data["privacy_policy"] = None
                try: data["terms_of_service"] = modal.find_element_by_partial_link_text("Terms of Service").get_attribute("href")
                except: data["terms_of_service"] = None
                data["url"] = driver.current_url
            except Exception as e:
                raise e
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

