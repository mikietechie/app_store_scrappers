import bs4, os, csv, datetime
from urllib.parse import urlparse
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


def get_index_url(url):
    o = urlparse(url)
    return o.scheme + "://" + o.hostname


def scape_app_data(soup: bs4.BeautifulSoup, url):
    app_data = {"url": url, "date": datetime.date.today(), "time": datetime.datetime.utcnow().strftime("%r")}
    try: app_data["logo"] = soup.find("img", class_="logo").get("src")
    except: app_data["logo"] = None
    try: app_data["video"] = soup.find("iframe", class_="video-iframe").get("src")
    except: app_data["video"] = None
    try: app_data["name"] = soup.find("h1", class_="app-name").text.strip()
    except: app_data["name"] = None
    try: app_data["tag_line"] = soup.find("h2", class_="tag-line").text.strip()
    except: app_data["tag_line"] = None
    try: app_data["category"] = soup.find("span", class_="category").text.strip()
    except: app_data["category"] = None
    try: app_data["rating"] = soup.find("div", class_="overall").find("div", class_="parsed-rating").text.strip()
    except: app_data["rating"] = None
    try: app_data["reviews_count"] = soup.find("div", class_="overall").find("span", class_="review-count").text.strip().replace("(", "").replace(" ratings)", "")
    except: app_data["reviews_count"] = None
    try: app_data["developer"] = soup.find("a", attrs={"data-id": "developer"}).text.strip()
    except: app_data["developer"] = None
    try: app_data["website"] = get_index_url(soup.find("a", attrs={"data-id": "developer"}).get("href"))
    except: app_data["website"] = None
    try: app_data["contact"] = soup.find("span", class_="contact").text.strip()
    except: app_data["contact"] = None
    try: app_data["email"] = soup.find("a", class_="contact").text.strip()
    except: app_data["email"]  = None
    try: app_data["support"] = soup.find("a", attrs={"data-id": "support"}).text.strip()
    except: app_data["support"] = None
    try: app_data["details"] = soup.find("div", class_="overview-text").find_all("p")[-1].text.strip()
    except: app_data["details"] = None
    try: app_data["how_it_works_with_quick_books"] = soup.find("div", class_="overview-text").find_all("p")[0].text.strip()
    except: app_data["how_it_works_with_quick_books"] = None
    try: app_data["key_benefits"] = "\n".join([li.text.strip() for li in soup.find("div", class_="overview-text").find("ul", class_="key-benefits").find_all("li")])
    except: app_data["key_benefits"] = None
    try: app_data["pricing_text"] = soup.find("div", class_="pricing").find("p").text.strip()
    except: app_data["pricing_text"] = None
    try: app_data["plans"] = [{
        "plan-name": plan.find("div", class_="plan-name").text.strip(),
        "details": plan.find("div", class_="details").text.strip(),
        "users": plan.find("div", class_="users").find("div", class_="value").text.strip(),
        "price": plan.find("div", class_="price").find("div", class_="value").text.strip(),
    } for plan in soup.find_all("div", class_="plan")]
    except: app_data["plans"] = []
    try: app_data["similar"] = [{
        "name": app_card.find("div", class_="appcard-display-name").text.strip(),
        "tag-line": app_card.find("div", class_="appcard-tagline").text.strip(),
        "url": f"https://quickbooks.intuit.com{app_card['href']}"
    } for app_card in soup.find_all("a", class_="appcard-wrapper-default")]
    except: app_data["similar"] = []
    try: app_data["FAQs"] = [{
        "question": faq.find("h4", class_="faq-question").text.strip(),
        "answer": faq.find("div", class_="faq-answer").text.strip()
    } for faq in soup.find_all("div", class_="faqs-question-answers")]
    except: app_data["FAQs"] = []
    print(app_data)
    return app_data

def main():
    try:
        url = "https://quickbooks.intuit.com/app/apps/home/"
        driver=webdriver.Chrome(executable_path = driver_path, options=chrome_options)
        wait = WebDriverWait(driver, timeout=10)
        driver.get(url)
        wait.until(presence_of_element_located((By.CLASS_NAME, "appcard-wrapper-home-browse")))
        soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
        sidebar = soup.find("div", class_="split-layout-sidebar")
        categories = sidebar.find_all("div", class_="collection-container")[-1]
        category_links = [f"https://quickbooks.intuit.com{category_link['href']}" for category_link in categories.find_all("a", class_="item collection")]
        all_app_links = []
        for link in category_links:
            # iterate over all app cards and load app links
            driver.get(link)
            wait.until(presence_of_element_located((By.CLASS_NAME, "appcard-wrapper-home-browse")))
            button = driver.find_element_by_css_selector("button.view-all-link")
            try:
                wait.until(presence_of_element_located((By.CSS_SELECTOR, "button.view-all-link")))
                button = driver.find_element_by_css_selector("button.view-all-link")
                button.click()
            except: print("click error")
            page_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
            for url in [f"https://quickbooks.intuit.com{app_card['href']}" for app_card in page_soup.find_all("a", class_="appcard-wrapper-home-browse")]:
                all_app_links.append(url)
        all_app_links = list(set(all_app_links))
        all_apps_data = []
        for link in all_app_links:
            try:
                driver.get(link)
                wait.until(presence_of_element_located((By.CLASS_NAME, "overall")))
                page_soup = bs4.BeautifulSoup(driver.page_source, features="html.parser")
                all_apps_data.append(scape_app_data(page_soup, link))
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

