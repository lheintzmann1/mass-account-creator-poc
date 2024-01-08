import asyncio
import random
import re
import string
import sqlite3
from unidecode import unidecode
import concurrent.futures
from randomuser import RandomUser
from account_generator_helper import InboxKitten
from seleniumwire import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

options = Options()


def process(user, swire_opt):
    try:
        browser = webdriver.Chrome(service=Service(ChromeDriverManager(
        ).install()), options=options, seleniumwire_options=swire_opt)

        try:
            browser.set_page_load_timeout(30)
            browser.get(
                'https://www.tiktok.com/signup/phone-or-email/email?lang=en')
        except TimeoutException:
            browser.close()
            return

        print("Tiktok Webpage Opened")
        sleep(3)

        try:
            browser.find_element("xpath", "//*[text()='Accept all']").click()
        except NoSuchElementException:
            pass

        sleep(3)

        email_in = browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[5]/div/input")
        email_in.send_keys(user["email"])
        sleep(1)

        pass_in = browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[6]/div/input")
        pass_in.send_keys(user["password"])
        sleep(3)

        month_in = random.randint(1, 12)
        day_in = 16
        year_in = random.randint(23, 63)

        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[1]").click()
        sleep(1)
        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[1]/div[2]/div[{month}]".format(month=month_in)).click()
        sleep(1)

        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[2]").click()
        sleep(1)
        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[2]/div[2]/div[{day}]".format(day=day_in)).click()
        sleep(1)

        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[3]").click()
        sleep(1)
        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[3]/div[2]/div[{year}]".format(year=year_in)).click()
        sleep(5)

        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[7]/div/button").click()

        sleep(5)

        code = init_mail(user["username"])

        code_in = browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[7]/div/div/input")
        code_in.send_keys(code)
        sleep(2)
        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/button").click()

        sleep(5)

        uname_in = browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[1]/input")
        uname_in.send_keys(user["username"])

        sleep(1)

        browser.find_element(
            "xpath", "/html/body/div[1]/div/div[2]/div[1]/form/button").click()

        sleep(10)

        try:
            conn = sqlite3.connect("accounts.db")
            c = conn.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS tiktok (username TEXT, password TEXT)")
            c.execute("INSERT INTO accounts VALUES (?, ?)",
                      (user["username"], user["password"]))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)
#        with open("accounts.txt", "a") as f:
#            f.write(f"{user['username']}:{user['password']}\n")
        browser.close()

    except (NoSuchElementException, TimeoutException, WebDriverException):
        pass
    finally:
        if browser:
            browser.close()
        else:
            pass


def gen_uname(fname, name):
    nb = random.randint(1000, 9999)
    template = f"{fname.lower()}_{name.lower()}_{nb}"
    formats = ["_", ".", ""]
    chosen_format = random.choice(formats)
    uname = re.sub(r'\W+', chosen_format, template)
    uname = uname.replace("_", chosen_format)
    return uname


def gen_pass(length=8):
    chars = string.ascii_letters + string.digits + '$€!.?&'
    password = ''.join(random.choice(chars) for i in range(length))
    if not any(c.islower() for c in password):
        password = password[:1] + \
            random.choice(string.ascii_lowercase) + password[1:]
    if not any(c.isupper() for c in password):
        password = password[:2] + \
            random.choice(string.ascii_uppercase) + password[2:]
    if not any(c.isdigit() for c in password):
        password = password[:3] + random.choice(string.digits) + password[3:]
    if not any(c in '$€!.?&' for c in password):
        password = password[:4] + random.choice('$€!.?&') + password[4:]
    return password


def rand_emoji():
    return chr(random.randint(0x1F600, 0x1F64F))


def generate_user():
    user = RandomUser()
    fname = unidecode(user.get_first_name())
    lname = unidecode(user.get_last_name())
    gender = user.get_gender()
    password = gen_pass()
    uname = gen_uname(fname, lname)
    mail = InboxKitten()
    email = mail.set_email(uname)
    bio = rand_emoji()

    return {
        "firstName": fname,
        "lastName": lname,
        "fullName": f"{fname} {lname}",
        "gender": gender,
        "password": password,
        "username": uname,
        "email": email,
        "bio": bio
    }


def getCode(mail):
    pattern = r'(\d{6}) is your verification code'
    inbox = mail.get_inbox()
    for letter in inbox:
        match = re.search(pattern, letter.subject)
        if match:
            code = match.group(1)
            return code
    return None


def init_mail(username):
    mail = InboxKitten()
    email = mail.set_email(username)
    code = getCode(mail)

    while code is None:
        sleep(10)
        code = getCode(mail)
        print("Waiting for code...")
    print(f"Code: {code}")
    return code


async def main():
    acc_no = int(input("Number of Accounts (0 for endless): "))
    max_threads = int(input("Maximum number of threads: "))
    # proxy = input("Proxy (Leave blank for none): ")
    swire_opt = {}
    if acc_no == 0:
        acc_no = float("inf")

    loop = asyncio.get_event_loop()

    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        futures = []

        for _ in range(acc_no if acc_no != float("inf") else max_threads):
            user = generate_user()
            future = loop.run_in_executor(
                executor, process, user, swire_opt)
            futures.append(future)

        await asyncio.gather(*futures)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
