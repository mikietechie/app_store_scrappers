"""
Work done by Mike Zinyoni
Python JavaScript engineer

!actively looking for a job!
Working
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
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')


def scape_app_data(soup: bs4.BeautifulSoup):
    app_data = {"date": datetime.date.today(), "time": datetime.datetime.utcnow().strftime("%r")}
    try: app_data["name"] = soup.select_one("h1.t__h1").text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = ", ".join([img["src"] for img in soup.select(".appstore__app-details__main .u__padt__10 img")])
    except: app_data["images"] = None
    try: app_data["logo"] = soup.select_one("img.appstore__app-details__app-icon")["src"]
    except: app_data["logo"] = None
    try: app_data["video"] = soup.select_one("div.appstore__app-details__video-embed__container iframe")['src']
    except: app_data["video"] = None
    try: app_data["category"] = ", ".join([span.text.strip() for span in soup.select("span.appstore__app-details__category-pill")])
    except: app_data["category"] = None
    try: app_data["details"] = soup.select_one("div.intercom-interblocks").text.strip()
    except: app_data["details"] = None
    try: app_data["tagline"] = soup.select_one("p.u__mr_x2").text.strip()
    except: app_data["tagline"] = None
    try: app_data["developer"] = soup.select("span.appstore__app-details__header__badge-opener-text")[0].text.strip()
    except: app_data["developer"] = None
    try: app_data["pricing_text"] = soup.select("span.appstore__app-details__header__badge-opener-text")[1].text.strip()
    except: app_data["pricing_text"] = None
    try: app_data["similar"] = ", ".join([h3.text.strip() for h3 in soup.select(".appstore__modal__grid__item h3")])
    except: app_data["similar"] = []
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=300)
        # get category links
        url = "https://www.intercom.com/app-store/"
        driver.get(url)
        wait.until(presence_of_element_located((By.ID, "ember510")))
        driver.implicitly_wait(10)
        try:
            dismiss_chat_btn = driver.find_element_by_css_selector("div.intercom-lr0ri6.es6hgh14")
            dismiss_chat_btn.click()
            driver.implicitly_wait(10)
        except: pass
        soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
        category_links = [
            f'https://www.intercom.com{a["href"]}' for a in soup.select(".appstore__section-menu div div:nth-child(3) a.appstore__section-menu__category")
        ]
        # done with category links
        all_apps_data, urls = [], []
        print(category_links)
        for link in category_links:
            print(link)
            # iterate over all app cards and load app links
            try:
                driver.get(link)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, ".appstore__grid__item .card .appstore__app-card__container")))
                for app_card in driver.find_elements_by_css_selector(".appstore__grid__item .card .appstore__app-card__container"):
                    driver.implicitly_wait(0.5)
                    app_card.click()
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "body > div.application__embercom-root.ember-application > div.ds-new__modal__blanket > div > div > div.ds-new__modal__body.o__full-bleed > div.appstore__modal__header > div")))
                    modal = driver.find_element_by_css_selector("body > div.application__embercom-root.ember-application > div.ds-new__modal__blanket > div")
                    if driver.current_url not in urls:
                        data = scape_app_data(bs4.BeautifulSoup(modal.get_attribute("innerHTML"), features="html.parser"))
                        try: data["terms_of_service"] = modal.find_element_by_partial_link_text("Terms of service").get_attribute("href")
                        except: data["terms_of_service"] = None
                        try: data["privacy_policy"] = modal.find_element_by_partial_link_text("Privacy policy").get_attribute("href")
                        except: data["privacy_policy"] = None
                        data["url"] = driver.current_url
                        urls.append(driver.current_url)
                        all_apps_data.append(data)
                        close_modal_btn = driver.find_element_by_css_selector("body > div.application__embercom-root.ember-application > div.ds-new__modal__blanket > div > div > div.ds-new__modal__close__container > button > svg")
                        close_modal_btn.click()
                        if len(all_apps_data) >3: break
            except Exception as e:
                raise e
                print("Exception:\t", str(e))
            if len(all_apps_data) >5: break
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

