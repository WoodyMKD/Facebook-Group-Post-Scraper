from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import sys
import argparse
import time
import psycopg2

# ================ ( CONFIG ) ================
geckodriver_path = "XXX"
geckodriver_log_path = "XXX"
fb_username = "XXX"
fb_pass = "XXX"
headlessMode = True
# ============================================

# ================ ( Argument Config ) ================
# Example args: -g 125093080970970 -d 1

parser = argparse.ArgumentParser(description='FB Scraper')
parser.add_argument("-g", '--groups', nargs='+',
                    dest="groups")

parser.add_argument("-d", "--dlabocina", action="store",
                    dest="depth", default=3, type=int)
args = parser.parse_args()
# ============================================

PROFILE = webdriver.FirefoxProfile()
PROFILE.set_preference("app.update.enabled", False)
PROFILE.update_preferences()
options = Options()
options.headless = headlessMode


def remove_new_line(string):
    words = string.split("\n")
    string = " ".join(words)
    return string


def fix_href(string):
    head, sep, tail = string.partition('fref=')
    return head[:-1]


class CollectPosts(object):
    def __init__(self, ids=None, depth=3, delay=1.5):
        self.ids = ids
        self.depth = depth + 1
        self.delay = delay
        self.browser = webdriver.Firefox(options=options,
                                         firefox_profile=PROFILE,
                                         executable_path=geckodriver_path,
                                         service_log_path=geckodriver_log_path)
        self.conn = None
        self.curr = None

    def start_scraping(self):
        for iden in self.ids:
            self.collect_group_posts(iden)
        self.browser.quit()

    def collect_group_posts(self, group):
        self.browser.get('https://www.facebook.com/groups/' + group + '?sorting_setting=CHRONOLOGICAL')

        for scroll in range(self.depth):
            self.browser.execute_script(
                "window.scrollTo({"
                "left: 0,"
                "top: document.body.scrollHeight,"
                "behavior: 'auto'"
                "});")
            time.sleep(self.delay)

        self.connect_db()

        links = self.browser.find_elements_by_link_text("See more")
        for link in links:
            link.click()
        posts = self.browser.find_elements_by_class_name(
            "userContentWrapper")
        for count, post in enumerate(posts):
            self.extract_post_and_update_db(post)

        self.curr.close()

    def connect_db(self):
        try:
            print('Connecting to the PostgreSQL database...')
            self.conn = conn = psycopg2.connect("host=localhost dbname=NajdiPrevoz user=postgres password=tomato")
            self.curr = conn.cursor()
            self.curr.execute("DELETE FROM sk_kp")
            self.conn.commit()
            print('Connection successful!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return

    def extract_post_and_update_db(self, post):
        profile_name_url_element = post.find_element_by_css_selector("a[ajaxify]")
        profile_name = profile_name_url_element.get_attribute("title")
        time_element = post.find_element_by_css_selector("abbr")
        utime = time_element.get_attribute("data-utime")
        profile_url = fix_href(profile_name_url_element.get_attribute("href"))
        text = post.find_element_by_class_name("userContent").text

        if text:
            text = remove_new_line(text)
        else:
            return

        sql = """INSERT INTO SK_KP(driver_name, post_date, driver_facebook_url, post_content) VALUES(%s, %s, %s, %s);"""
        self.curr.execute(sql, (profile_name, utime, profile_url, text))
        self.conn.commit()

    def safe_find_element_by_id(self, elem_id):
        try:
            return self.browser.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def login(self, email, password):
        try:
            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()
            self.browser.find_element_by_name('email').send_keys(email)
            self.browser.find_element_by_name('pass').send_keys(password)
            self.browser.find_element_by_id('loginbutton').click()

        except Exception as e:
            print("ERROR!")
            print(sys.exc_info()[0])
            self.browser.quit()
            exit()


if __name__ == "__main__":
    if args.groups:
        C = CollectPosts(ids=args.groups, depth=args.depth)
        C.login(fb_username, fb_pass)
        C.start_scraping()
        print("Finished scraping.")
        exit()
