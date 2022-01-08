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
    try: app_data["name"] = soup.select_one("div.header").text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = ", ".join([md["src"] for md in soup.select(".screenshots .silentbox-item")])
    except: app_data["images"] = None
    try: app_data["logo"] = soup.select_one(".app-cover img")["src"]
    except: app_data["logo"] = None
    try: app_data["category"] = ", ".join([a.text.strip() for a in [spacer for spacer in soup.select(".sidebar .details .spacer") if "ago in" in spacer.text][0].find_next_siblings("a")])
    except: app_data["category"] = None
    try: app_data["details"] = soup.select_one(".el-tab-pane .keep-whitespaces.website").text.strip()
    except: app_data["details"] = None
    try: app_data["instructions"] = soup.select_one("#pane-1 .keep-whitespaces.website").text.strip()
    except: app_data["instructions"] = None
    try: app_data["tagline"] = soup.select_one(".overview").text.strip()
    except: app_data["tagline"] = None
    try: app_data["priceline"] = soup.select_one(".app-cover").find_previous_sibling("span", class_="badge").text.strip()
    except: app_data["priceline"] = "Paid"
    try: app_data["developer"] = [spacer.text.strip() for spacer in soup.select(".sidebar .details .spacer") if "Published by" in spacer.text][0]
    except: app_data["developer"] = None
    try: app_data["timeline"] = [spacer.text.strip() for spacer in soup.select(".sidebar .details .spacer") if "ago in" in spacer.text][0]
    except: app_data["timeline"] = None
    try: app_data["info"] = soup.select_one(".sidebar .details .product-info").parent.text.strip()
    except: app_data["info"] = None
    try: app_data["verification"] = soup.select_one(".freshworks-verified").text.strip()
    except: app_data["verification"] = None
    try: app_data["help"] = ", ".join([a["href"] for a in soup.select(".help a")])
    except: app_data["help"] = None
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=300)
        # get category links
        url = "https://www.freshworks.com/apps/"
        driver.get(url)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, ".sidebar .category .menu .link")))
        driver.implicitly_wait(10)
        category_links = [
            f'https://www.freshworks.com{a.get_attribute("href")}' for a in driver.find_elements_by_css_selector(".sidebar .category .menu a.link")
        ]
        # done with category links
        all_apps_links = []
        for category_link in category_links:
            driver.get(category_link)
            wait.until(presence_of_element_located((By.CSS_SELECTOR, "button.mp-btn.seeAllBtn")))
            # TODO: add logic to click load more
            # .mp-btn.seeAllBtn
            wait.until(presence_of_element_located((By.CSS_SELECTOR, "button.mp-btn.seeAllBtn")))
            while True:
                try:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "button.mp-btn.seeAllBtn")))
                    more_button = driver.find_element_by_css_selector("button.mp-btn.seeAllBtn")
                    more_button.click()
                except: break
            all_apps_links.extend([f'https://www.freshworks.com{a.get_attribute("href")}' for a in driver.find_elements_by_css_selector(".app-grid a.app-card")])
        all_apps_links = list(set(all_apps_links))
        all_apps_data = []
        for app_link in all_apps_links:
            try:
                driver.get(link)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, "div.freshworks-verified")))
                app_data_el = driver.find_element_by_css_selector(".layout .content.body")
                data = scape_app_data(bs4.BeautifulSoup(app_data_el.get_attribute("innerHTML"), features="html.parser"))
                try: data["privacy_policy"] = modal.find_element_by_partial_link_text("App Privacy Policy").get_attribute("href")
                except: data["privacy_policy"] = None
                data["url"] = driver.current_url
                all_apps_data.append(data)
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

