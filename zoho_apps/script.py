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
    try: app_data["name"] = soup.select_one("h1.extn-title.extensionTitle").text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = ", ".join([md["src"] for md in soup.select("#screenshots img")])
    except: app_data["images"] = None
    try: app_data["logo"] = soup.select_one("div.extn-cell.extension-icon img")["src"]
    except: app_data["logo"] = None
    try: app_data["category"] = [td.find_next_sibling("td").text.strip() for td in soup.select("table.vrs-cat-pric td.info-title") if "Category" in td.text][0]
    except: app_data["category"] = None
    try: app_data["details"] = soup.select_one("p.shortDescription.extn-content").text.strip()
    except: app_data["details"] = None
    try: app_data["features"] = ". ".join([li.text.strip() for li in soup.select("#keyfeature li")])
    except: app_data["features"] = None
    try: app_data["tagline"] = soup.select_one("p.extn-tagline.extn-content").text.strip()
    except: app_data["tagline"] = None
    try: app_data["priceline"] = [td.find_next_sibling("td").text.strip() for td in soup.select("table.vrs-cat-pric td.info-title") if "Pricing" in td.text][0]
    except: app_data["priceline"] = "Paid"
    try: app_data["developer"] = soup.select_one('div.extn-cell.extn-tagline-title .extn-tagline.extn-content.partnerTxt.inline-middle a.redirectVendor').text.strip()
    except: app_data["developer"] = None
    try: app_data["timeline"] = [td.find_next_sibling("td").text.strip() for td in soup.select("table.vrs-cat-pric td.info-title") if "Published date" in td.text][0]
    except: app_data["timeline"] = None
    try: app_data["ratings_count"] = soup.select_one("div.extn-sub-head.averageRatingCount").text.strip()
    except: app_data["ratings_count"] = None
    try: app_data["rating"] = re.search("[0-9]+", soup.select_one("div#avgrating-wrapper span").text.strip()).group()
    except: app_data["rating"] = None
    try: app_data["installs"] = re.search("[0-9]+", soup.select_one('div[style="margin-top:2px;"] span').text.strip()).group()
    except: app_data["installs"] = None
    try: app_data["help"] = ", ".join([a['href'] for a in soup.select(".extensionResources a")])
    except: app_data["help"] = None
    try: app_data["tags"] = ", ".join([a.text.strip() for a in soup.select("a.fextn-tit.firstOff.tags-span")])
    except: app_data["tags"] = None
    try: app_data["editions"] = ", ".join([li.text.strip() for li in soup.select("#supported-edition li")])
    except: app_data["editions"] = None
    try: app_data["platform"] = [td.find_next_sibling("td").text.strip() for td in soup.select("table.vrs-cat-pric td.info-title") if "Platform" in td.text][0]
    except: app_data["platform"] = None
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=20)
        # get category links
        url = "https://marketplace.zoho.com/home"
        driver.get(url)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn-viewAll")))
        driver.implicitly_wait(10)
        category_links = [
            f'{a.get_attribute("href")}' for a in driver.find_elements_by_css_selector("a.btn.btn-viewAll")
        ]
        # done with category links
        all_apps_links = []
        for category_link in category_links:
            driver.get(category_link)
            wait.until(presence_of_element_located((By.CSS_SELECTOR, "a.extn-redirection-block")))
            while True:
                try:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn-viewMore")))
                    more_button = driver.find_element_by_css_selector("a.btn.btn-viewMore")
                    more_button.click()
                except: break
            all_apps_links.extend([f'{a.get_attribute("href")}' for a in driver.find_elements_by_css_selector("a.extn-redirection-block")])
        all_apps_links = list(set(all_apps_links))
        all_apps_data = []
        wait = WebDriverWait(driver, timeout=10)
        for link in all_apps_links:
            try:
                driver.get(link)
                try:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "span.extn-content.inline-middle")))
                except: pass
                driver.implicitly_wait(2)
                data = scape_app_data(bs4.BeautifulSoup(driver.page_source, features="html.parser"))
                data["url"] = driver.current_url
                all_apps_data.append(data)
            except:
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

