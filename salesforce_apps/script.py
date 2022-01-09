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
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')


def scape_app_data(soup: bs4.BeautifulSoup, url=None, logo=None):
    app_data = {"url": url, "date": datetime.date.today(), "time": datetime.datetime.utcnow().strftime("%r"), "logo": logo}
    try: app_data["name"] = soup.find("h1", class_="appx-page-header-2_title").text.strip()
    except: app_data["name"] = None
    try: app_data["images"] = [img["src"] for img in soup.find("div", class_="appx-carousel-media").find_all("img", class_="appx-carousel-media-file")]
    except: app_data["images"] = None
    try: app_data["release_date"] = soup.find("span", attrs={"id": "appxListingDetailPageId:AppxLayout:j_id857"}).find("p", class_="").text.strip()
    except: app_data["release_date"] = None
    try: app_data["listed_on"] = soup.find("div", attrs={"id": "AppxListingDetailOverviewTab:listingDetailOverviewTab:appxListingDetailOverviewTabComp:j_id152"}).find("div", class_="appx-extended-detail-subsection-description").text.strip()
    except: app_data["listed_on"] = None
    try: app_data["version"] = soup.find("div", attrs={"id": "AppxListingDetailOverviewTab:listingDetailOverviewTab:appxListingDetailOverviewTabComp:j_id149"}).text.strip()
    except: app_data["version"] = None
    try: app_data["package_name"] = soup.find("div", attrs={"id": "AppxListingDetailOverviewTab:listingDetailOverviewTab:appxListingDetailOverviewTabComp:j_id146"}).text.strip()
    except: app_data["package_name"] = None
    try: app_data["category"] = ",".join([a.text.strip() for a in soup.find("div", class_="appx-detail-section-categories").find_all("a")])
    except: app_data["category"] = None
    try: app_data["highlights"] = [span.text.strip() for span in soup.find_all("span", class_="appx-highlights-text")]
    except: app_data["highlights"] = None
    try: app_data["tagline"] = soup.find("div", class_="appx-headline-details-tagline").text.strip()
    except: app_data["tagline"] = None
    try: app_data["headline"] = soup.find("div", class_="appx-detail-section-description").find("p").text.strip()
    except: app_data["headline"] = None
    try: app_data["rating"] = re.search("[0-9]+", f'{soup.find("span", class_="appx-rating-stars")["class"]}').group()
    except: app_data["rating"] = None
    try: app_data["reviews_count"] = re.search("[0-9]+", soup.find("span", class_="appx-rating-amount").text.strip()).group()
    except: app_data["reviews_count"] = None
    try: app_data["developer"] = soup.find("div", class_="appx-company-name").text.strip()
    except: app_data["developer"] = None
    try: app_data["website"] = soup.find("a", attrs={"data-event": "listing-publisher-website"})["href"]
    except: app_data["website"] = None
    try: app_data["datasheets"] = ",".join([a["href"] for a  in soup.find_all("a", attrs={"data-event": "listing-datasheet"})])
    except: app_data["datasheets"] = None
    try: app_data["features"] = [li.text.strip() for li in soup.find("div", class_="appx-feature-menu").find_all("li")]
    except: app_data["features"]  = []
    try: app_data["package_contents"] = [li.text.strip() for li in soup.find("div", class_="appx-extended-detail-subsection-details").find_all("li")]
    except: app_data["package_contents"]  = []
    try: app_data["lighting_components"] = [li.text.strip() for li in soup.find_all("div", class_="appx-extended-detail-subsection-details")[-1].find_all("li")]
    except: app_data["lighting_components"]  = []
    try:
        try:
            app_data["terms_and_conditions"] = soup.find("div", attrs={"id": "AppxListingDetailOverviewTab:listingDetailOverviewTab:appxListingDetailOverviewTabComp:j_id140"}).find("a")['href'] # latest date
        except:
            app_data["terms_and_conditions"] = soup.find("div", attrs={"id": "AppxListingDetailOverviewTab:listingDetailOverviewTab:appxListingDetailOverviewTabComp:j_id137"}).find("a")['href'] # latest date
    except: app_data["terms_and_conditions"] = None
    try: app_data["description"] = soup.find("div", class_="appx-extended-detail-description").text.strip()
    except: app_data["description"] = None
    try: app_data["requirements"] = soup.find("span", class_="appx-extended-detail-subsection-segment-req").text.strip()
    except: app_data["requirements"] = None
    try: app_data["pricing_text"] = soup.find("p", class_="appx-pricing-detail-header").text.strip()
    except: app_data["pricing_text"] = None
    try: app_data["languages"] = ",".join([a.text.strip() for a in soup.find_all("a", attrs={"data-event": "listing-languages"})])
    except: app_data["languages"] = ""
    try: app_data["similar"] = [
        {
            "name": li.find("a").find("span", class_="appx-tile-title").text.strip(),
            "link": li.find("a")['href'],
        } for li in soup.find("ul", class_="appx-tiles-grid-ul").find_all("li")
    ]
    except: app_data["similar"] = []
    print(app_data)
    return app_data


def main():
    try:
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=20)
        # get category links
        url = "https://appexchange.salesforce.com/appxStore"
        driver.get(url)
        wait.until(presence_of_element_located((By.ID, "appx-load-more-button-id")))
        categories_nav_link = driver.find_element_by_id("appx-menu-header-text")
        categories_nav_link.click()
        wait.until(presence_of_element_located((By.CLASS_NAME, "appx-menu-items-container")))
        menu_container = driver.find_element_by_css_selector(".appx-menu-items-container.appx-subcategory-level0")
        categories_link = menu_container.find_element_by_partial_link_text("Categories")
        categories_link.click()
        wait.until(presence_of_element_located((By.ID, "subcategory-Categories")))
        categories_submenu = driver.find_element_by_id("subcategory-Categories")
        category_links = []
        for category_link in categories_submenu.find_elements_by_css_selector("a.appx-menu-option"):
            try:
                if category_link.get_attribute("href") == "javascript:void(0);":
                    category_link.click()
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "div.appx-menu-items-container.appx-subcategory-menu.appx-subcategory-level2.appx-subcategory-visible")))
                    tmp_links = driver.find_element_by_css_selector("div.appx-menu-items-container.appx-subcategory-menu.appx-subcategory-level2.appx-subcategory-visible")
                    for link in tmp_links.find_elements_by_css_selector("a.appx-menu-option"):
                        category_links.append(link.get_attribute("href"))
                else:
                    category_links.append(category_link.get_attribute("href"))
            except Exception as e:
                print("Exception:\t", str(e))
        # done with category links
        all_app_links = []
        for link in category_links:
            # iterate over all app cards and load app links
            try:
                driver.get(link)
                wait.until(presence_of_element_located((By.CSS_SELECTOR, "a.appx-tile.appx-tile-app.tile-link-click")))
                while True:
                    try:
                        wait.until(presence_of_element_located((By.ID, "appx-load-more-button-id")))
                        more_button = driver.find_element_by_id("appx-load-more-button-id")
                        more_button.click()
                    except:
                        break
                for link in driver.find_elements_by_css_selector("li a.appx-tile.appx-tile-app.tile-link-click"):
                    all_app_links.append(link.get_attribute("href"))
            except Exception as e:
                print("Exception:\t", str(e))
        all_app_links = list(set(all))
        all_apps_data = []
        for i, link in enumerate(all_app_links):
            try:
                driver.get(link)
                try:
                    wait.until(presence_of_element_located((By.CSS_SELECTOR, "span.appx-price")))
                except: pass
                page_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
                all_apps_data.append(scape_app_data(page_soup, link))
                print(f"now at {i}!")
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
            exit()
        raise e


if __name__ == "__main__":
    main()
    exit()

