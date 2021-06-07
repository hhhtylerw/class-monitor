from selenium import webdriver
from twilio.rest import Client
from datetime import datetime
import time, requests, json
import login

email = login.getEmail()
password = login.getPassword()
monitorList = [
    {
        "classNumber": "PHY2049",
        "classCredit": "3"
    },
    {
        "classNumber": "PHY2049L",
        "classCredit": "1"
    },
    {
        "classNumber": "MAS3114",
        "classCredit": "3"
    },
    {
        "classNumber": "CGS3065",
        "classCredit": "3"
    }
]
classBlacklist = [17059,15424,17080]
sidCookie, shibCookie = "", ""
client = Client("AC287aed74055f97dd0a0f6797d8f0ebf4", "81793dea0f6ab3d9d5b269428a64d19b")

def getCookies():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    driver = webdriver.Chrome("C:\\Users\\hhhtylerw\\chromedriver.exe", options=options)
    driver.get("https://one.uf.edu/")
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="root"]/main/div[1]/div/div/div/div[2]/button').click() # Click login
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="username"]').send_keys(email) # Type email
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password) # Type password
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="submit"]').click() # Click login
    time.sleep(5)
    driver.switch_to.frame(driver.find_element_by_id('duo_iframe'))
    driver.find_element_by_xpath('//*[@id="auth_methods"]/fieldset/div[1]/button').click() # Click DUO Push
    driver.switch_to.default_content()

    oldtime = int(time.time())
    while True: # Wait for DUO Push approval
        newtime = int(time.time())
        if newtime - oldtime >= 60:
            driver.quit()
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " | " + "Login not confirmed, sleeping")
            return "", ""

        if driver.current_url == "https://one.uf.edu/":
            break
        time.sleep(1)

    time.sleep(5)
    driver.get("https://one.uf.edu/myschedule/2218")
    time.sleep(10)
    driver.refresh()
    time.sleep(10)
    driver.find_element_by_xpath('//*[@id="scheduleBox"]/div/div[1]/a/span').click()

    time.sleep(10)

    sidCookie = driver.get_cookie("connect.sid")["value"]
    shibCookie = driver.get_cookie("_shibsession_68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f")["value"]

    driver.quit()

    return sidCookie, shibCookie

while True: # Loop monitor forever
    try: # Attempt to monitor and parse classes / Will try to get login cookies if fails
        if sidCookie == "" or shibCookie == "": # Check if cookies are blank
            print(1/0) # Will purposefully break try
        for monitor in monitorList:
            cookies = {
                'connect.sid': sidCookie,
                '_shibsession_68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f': shibCookie,
            }
            headers = {
                'Host': 'one.uf.edu',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
                'Accept': 'application/json, text/plain, */*',
                'sec-ch-ua-mobile': '?0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://one.uf.edu/soc/registration-search/2218',
                'Accept-Language': 'en-US,en;q=0.9',
                'dnt': '1',
            }
            params = (
                ('category', 'CWSP'),
                ('class-num', ''),
                ('course-code', monitor["classNumber"]),
                ('course-title', ''),
                ('cred-srch', 'EQ'),
                ('credits', monitor["classCredit"]),
                ('day-f', ''),
                ('day-m', ''),
                ('day-r', ''),
                ('day-s', ''),
                ('day-t', ''),
                ('day-w', ''),
                ('days', 'false'),
                ('dept', ' '),
                ('eep', ''),
                ('fitsSchedule', 'false'),
                ('ge', ''),
                ('ge-b', ''),
                ('ge-c', ''),
                ('ge-d', ''),
                ('ge-h', ''),
                ('ge-m', ''),
                ('ge-n', ''),
                ('ge-p', ''),
                ('ge-s', ''),
                ('instructor', ''),
                ('last-control-number', '0'),
                ('level-max', '--'),
                ('level-min', '--'),
                ('no-open-seats', 'false'),
                ('online-a', ''),
                ('online-c', ''),
                ('online-h', ''),
                ('online-p', ''),
                ('period-b', ''),
                ('period-e', ''),
                ('prog-level', ' '),
                ('qst-1', ''),
                ('qst-2', ''),
                ('qst-3', ''),
                ('quest', ''),
                ('term', '2218'),
                ('wr-2000', ''),
                ('wr-4000', ''),
                ('wr-6000', ''),
                ('writing', ''),
            )
            r = requests.get('https://one.uf.edu/api/myschedule/course-search/', headers=headers, params=params, cookies=cookies)
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " | " + str(r) + " | " + monitor["classNumber"])
            load = json.loads(r.text)[0]["COURSES"][0]["sections"]

            for i in load:
                if i["classNumber"] in classBlacklist:
                    continue

                #print(i["openSeats"])
                if i["openSeats"] != 0:
                    print("Open seat found!\nSending text...")
                    client.messages.create(body=f'Open {monitor["classNumber"]} seat found!',from_='+12392408716',to='+18505085707')
            time.sleep(15)

    except: # Get new login cookies
        try: # Attemp to login
            sidCookie, shibCookie = getCookies() 
        except: # Login failed, start over
            pass
    print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " | " + "Sleeping 120 minutes")
    time.sleep(60 * 120)



