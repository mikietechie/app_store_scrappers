"""
Work done by Mike Zinyoni
Python JavaScript engineer

!actively looking for a job!
Working Done!!!
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
    try: app_data["name"] = soup.select_one("h1").text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = ", ".join([img["src"] for img in soup.select("section.screenshots .image-gallery-slide-wrapper img")])
    except: app_data["images"] = None
    try: app_data["logo"] = soup.select_one("img").get("srcset") or soup.select_one("img").get("src")
    except: app_data["logo"] = None
    try: app_data["rating"] = len(soup.select('div[data-testid="Header-Stats"] svg.cui4-icon.cui4-icon--yellow'))
    except: app_data["rating"] = None
    try: app_data["reviews_count"] = re.search("[0-9]+", soup.select_one("span.ReviewCount-dnn620-0").text.strip()).group()
    except: app_data["reviews_count"] = None
    try: app_data["category"] = ", ".join([span.text.strip() for span in soup.select("a.styles__CategoryLink-sc-9px7lz-3")])
    except: app_data["category"] = None
    try: app_data["details"] = soup.select_one("section.Container-x87hbt-0.styles__AppDetailsContainer-xor6ij-0.styles__ContentWrapper-xor6ij-1").text.strip()
    except: app_data["details"] = None
    try: app_data["tagline"] = soup.select_one("p.Caption-uyiun5-0").text.strip()
    except: app_data["tagline"] = None
    try: app_data["developer"] = soup.select_one("p.styles__Author-sc-9px7lz-0").text.strip()
    except: app_data["developer"] = None
    try: app_data["similar"] = ", ".join([h2.text.strip() for h2 in soup.select("h2.Name-sc-8ygaid-0")])
    except: app_data["similar"] = None
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)
        # get category links
        url = "https://www.pipedrive.com/en/marketplace/apps"
        driver.get(url)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="AppCard"] a')))
        paginator_el = driver.find_element_by_css_selector(".styles__Pages-v7p2mr-3.fLLJAP")
        paginator_sp = bs4.BeautifulSoup(paginator_el.get_attribute("innerHTML"), features="html.parser")
        last_page = int(paginator_sp.select("a")[-1].text.strip())
        # soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
        page_links = [
            f"https://www.pipedrive.com/en/marketplace/apps?page={page}&sort=trending" for page in range(1, last_page)
        ]
        print("page links:\t:", page_links)
        all_app_links, urls = [], []
        for page_link in page_links:
            driver.get(page_link)
            wait.until(presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="AppCard"] a')))
            app_links = driver.find_elements_by_css_selector('article[data-testid="AppCard"] a')
            all_app_links.extend([app_link.get_attribute("href") for app_link in app_links])
            # break
        all_app_links = list(set(all_app_links))
        print("all app links:\t:", all_app_links)
        all_apps_data = []
        for app_link in all_app_links:
            try:
                driver.get(app_link)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="AppCard"] a')))
                app_data_html = driver.find_element_by_css_selector(".Details .App")
                data = scape_app_data(bs4.BeautifulSoup(app_data_html.get_attribute("innerHTML"), features="html.parser"))
                try: data["website"] = app_data_html.find_element_by_link_text("Website").get_attribute("href")
                except: data["website"] = None
                try: data["support_website"] = app_data_html.find_element_by_link_text("Support website").get_attribute("href")
                except: data["support_website"] = None
                try: data["support_email"] = app_data_html.find_element_by_link_text("Support email").get_attribute("href")
                except: data["support_email"] = None
                try: data["privacy_policy"] = app_data_html.find_element_by_link_text("Privacy Policy").get_attribute("href")
                except: data["privacy_policy"] = None
                try: data["terms_of_service"] = app_data_html.find_element_by_link_text("Terms of Service").get_attribute("href")
                except: data["terms_of_service"] = None
                data["url"] = app_link
                all_apps_data.append(data)
            except Exception as e:
                print("Exception:\t", str(e))
        driver.close()
        print("all apps data:\t:", all_apps_data)
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

