import requests, json, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from twilio.rest import Client
import login

delay = 4
options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
service = Service(login.getchromedriverpath())
headers = {
    "Content-Type": "application/json"
}
cookies = {
    "ONEUF_SESSION": "R",
    "_shibsession_68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f": "ATIO"
}
client = Client(login.getsid(), login.gettoken())

def get_course_info():
    print("Getting course info")
    try:
        r = requests.get(f"https://one.uf.edu/api/myschedule/course-search?ai=false&auf=false&category=CWSP&class-num=&course-code={login.getcourseid()}&course-title=&cred-srch=&credits={login.getcoursecredits()}&day-f=&day-m=&day-r=&day-s=&day-t=&day-w=&dept=&eep=&fitsSchedule=false&ge=&ge-b=&ge-c=&ge-d=&ge-h=&ge-m=&ge-n=&ge-p=&ge-s=&instructor=&last-control-number=0&level-max=&level-min=&no-open-seats=false&online-a=&online-c=&online-h=&online-p=&period-b=&period-e=&prog-level=&qst-1=&qst-2=&qst-3=&quest=false&term=2228&wr-2000=&wr-4000=&wr-6000=&writing=false&var-cred=&hons=false", headers=headers, cookies=cookies)
        print(r.status_code)

        resp = json.loads(r.text)
        if len(resp) == 0:
            print("No courses found")
            return True
        for section in resp[0]["COURSES"][0]["sections"]:
            print(section["waitList"])
            if section["waitList"]["cap"] == section["waitList"]["total"]:
                #print("Course is full")
                pass
            else:
                #print("Course is not full")
                client.messages.create(to=login.getphone(), from_=login.gettwiliophone(), body=f"Seat open for {login.getcourseid()}")
                time.sleep(1)
        return True
    except:
        return False

def get_uf_session():
    print("Getting UF session")
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://one.uf.edu/")
        time.sleep(delay)
        driver.find_element(By.XPATH, '//*[@id="main-content"]/div[1]/div[1]/div/div/div/div[2]/button').click()
        time.sleep(delay)
        driver.find_element(By.XPATH, '//*[@id="username"]').send_keys(login.getemail())
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(login.getpassword())
        driver.find_element(By.XPATH, '//*[@id="submit"]').click()
        time.sleep(delay)
        driver.switch_to.frame(driver.find_element(By.ID, "duo_iframe"))
        driver.find_element(By.XPATH, '//*[@id="login-form"]/div[2]/div/label/input').click()
        driver.find_element(By.XPATH, '//*[@id="auth_methods"]/fieldset/div[1]/button').click()
        start = time.time()
        while True:
            if time.time() - start < 60 and driver.current_url == "https://one.uf.edu/":
                #print("SUCCESS")
                break
            elif time.time() - start > 60:
                #print("FAILURE")
                time.sleep(60 * 120)
                return False
            time.sleep(1)
        driver.get("https://one.uf.edu/myschedule/")
        time.sleep(delay)
        driver.find_element(By.XPATH, '//*[@id="main-content"]/div[1]/div/div[2]/div/div/button[3]').click()
        time.sleep(delay)
        driver.find_element(By.XPATH, '//*[@id="main-content"]/div[1]/div/div[1]/div/div[2]/div/a/span[1]').click()
        time.sleep(10)
        for cookie in driver.get_cookies():
            if cookie["name"] == "ONEUF_SESSION":
                cookies["ONEUF_SESSION"] = cookie["value"]
            elif cookie["name"] == "_shibsession_68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f":
                cookies["_shibsession_68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f68747470733a2f2f73702e6c6f67696e2e75666c2e6564752f75726e3a6564753a75666c3a70726f643a30303734312f"] = cookie["value"]
        #print("SUCCESS\n", cookies)
        return True
    except:
        #print("FAILURE")
        return False
    finally:
        driver.quit()

def monitor():
    get_uf_session()
    while True:
        if not get_course_info():
            get_uf_session()
        time.sleep(60 * 5)


#get_course_info()
#get_uf_session()
monitor()