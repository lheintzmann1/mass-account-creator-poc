from randomuser import RandomUser
from account_generator_helper import InboxKitten
from unidecode import unidecode
import random
import string
import re
from seleniumwire import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

options = Options()


def generate_username(first_name, last_name):
    nb = random.randint(1000, 9999)
    template = f"{first_name.lower()}_{last_name.lower()}_{nb}"
    formats = ["_", "-", ".", ""]
    chosen_format = random.choice(formats)
    username = re.sub(r'\W+', chosen_format, template)
    username = username.replace("_", chosen_format)
    return username


def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def generate_user():
    user = RandomUser()
    first_name = unidecode(user.get_first_name())
    last_name = unidecode(user.get_last_name())
    gender = user.get_gender()
    password = generate_password()
    username = generate_username(first_name, last_name)
    mail = InboxKitten()
    email = mail.set_email(username)

    return {
        "firstName": first_name,
        "lastName": last_name,
        "fullName": f"{first_name} {last_name}",
        "gender": gender,
        "password": password,
        "username": username,
        "email": email
    }


def getCode(mail):
    pattern = r'(\d{6}) is your Instagram code'
    inbox = mail.get_inbox()
    for letter in inbox:
        match = re.search(pattern, letter.subject)
        if match:
            verification_code = match.group(1)
            return verification_code
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


def main():
    acc_no = int(input("Number of Accounts: "))
    use_proxy = input("Use proxy? (y/n): ")

    seleniumwire_options = {}
    if use_proxy == "y":
        pu = input("Proxy username: ")
        pp = input("Proxy password: ")
        proxy = input("Proxy (IP:PORT): ")
        seleniumwire_options = {
            'proxy': {
                'http': f'http://{pu}:{pp}@{proxy}',
                'https': f'https://{pu}:{pp}@{proxy}',
                'verify_ssl': False,
            }
        }

    for _ in range(acc_no):
        user = generate_user()
        print(user)

        browser = webdriver.Chrome(service=Service(ChromeDriverManager(
        ).install()), options=options, seleniumwire_options=seleniumwire_options)

        try:
            browser.set_page_load_timeout(30)
            browser.get('https://www.instagram.com/accounts/emailsignup/')
        except TimeoutException:
            browser.close()
            continue

        print("Instagram Webpage Opened")
        sleep(3)

        try:
            browser.find_element("xpath",
                                 "/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]").click()
        except NoSuchElementException as ex:
            pass

        sleep(3)

        email_in = browser.find_element(
            "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div[4]/div/label/input")
        email_in.send_keys(user["email"])
        sleep(1)

        full_name_in = browser.find_element(
            "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div[5]/div/label/input")
        full_name_in.send_keys(user["fullName"])
        sleep(1)

        username_in = browser.find_element(
            "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div[6]/div/label/input")
        username_in.send_keys(user["username"])
        sleep(1)

        password_in = browser.find_element(
            "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div[7]/div/label/input")
        password_in.send_keys(user["password"])
        sleep(3)

        browser.find_element(
            "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div[8]/div/button").click()
        sleep(5)

        year_index = random.randint(20, 45)
        month_index = random.randint(1, 11)
        day_index = random.randint(1, 26)

        year_in = Select(browser.find_element("xpath",
                                              "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div/div[4]/div/div/span/span[3]/select"))
        month_in = Select(browser.find_element("xpath",
                                               "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div/div[4]/div/div/span/span[1]/select"))
        day_in = Select(browser.find_element("xpath",
                                             "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div/div[4]/div/div/span/span[2]/select"))
        year_in.select_by_index(year_index)
        sleep(1)
        month_in.select_by_index(month_index)
        sleep(1)
        day_in.select_by_index(day_index)
        sleep(5)

        try:
            browser.find_element(
                "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div/div[6]/button").click()
        except NoSuchElementException:
            pass

        sleep(5)

        code = init_mail(user["username"])

        code_in = browser.find_element(
            "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/input")
        code_in.send_keys(code)
        sleep(2)
        browser.find_element(
            "xpath", "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div").click()

        sleep(10)

        with open("accounts.txt", "a") as f:
            f.write(f"{user['username']}:{user['password']}\n")
        browser.close()


if __name__ == "__main__":
    main()
