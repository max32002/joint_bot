#!/usr/bin/env python3
#encoding=utf-8
import os
import sys
import platform
import json
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# for close tab.
from selenium.common.exceptions import NoSuchWindowException
# for alert
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# for ["pageLoadStrategy"] = "eager"
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# for selenium 4
from selenium.webdriver.chrome.service import Service

# for wait #1
import time

import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# for error output
import logging
logging.basicConfig()
logger = logging.getLogger('logger')

#DR_NAME = u"尹文耀"
#DR_NAME = u"呂紹睿"
#DR_NAME = u"林志明"   # 整形外科

app_version = "MaxRegBot (2022.05.06)"

homepage_default = u"http://www.tzuchi.com.tw/home/index.php/2017-04-20-06-51-46/2017-04-20-06-52-41"

# initial webdriver
# 說明：初始化 webdriver
driver = None

homepage = ""
browser = "chrome"
user_id = ""
user_name = ""
user_tel = ""
user_birthday = ""
user_gender = ""
visit_time = ""
dr_name = ""

enable_captcha_ocr = False
#enable_captcha_ocr = True

debugMode = False

def get_app_root():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)
    return app_root

def get_config_dict():
    config_json_filename = 'settings.json'
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, config_json_filename)
    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    return config_dict

def load_config_from_local(driver):
    config_dict = get_config_dict()

    global homepage
    global homepage_default
    global browser

    global user_id
    global user_name
    global user_tel
    global user_birthday
    global user_gender
    global visit_time
    global dr_name

    global debugMode

    if not config_dict is None:
        # read config.
        if 'homepage' in config_dict:
            homepage = config_dict["homepage"]

        if 'user_id' in config_dict:
            user_id = config_dict["user_id"]

        if 'user_name' in config_dict:
            user_name = config_dict["user_name"]

        if 'user_tel' in config_dict:
            user_tel = config_dict["user_tel"]

        if 'user_birthday' in config_dict:
            user_birthday = config_dict["user_birthday"]

        if 'user_gender' in config_dict:
            user_gender = config_dict["user_gender"]

        if 'visit_time' in config_dict:
            visit_time = config_dict["visit_time"]

        if 'dr_name' in config_dict:
            dr_name = config_dict["dr_name"]

        # output config:
        print("version", app_version)
        print("homepage", homepage)
        print("user_id", user_id)
        print("user_name", user_name)
        print("user_tel", user_tel)
        print("user_birthday", user_birthday)
        print("user_gender", user_gender)
        print("visit_time", visit_time)
        print("dr_name", dr_name)
        
        print("debugMode", debugMode)

        # entry point
        # 說明：自動開啟第一個的網頁
        if homepage is None:
            homepage = ""
        if len(homepage) == 0:
            homepage = homepage_default

        Root_Dir = ""
        if browser == "chrome":
            # method 5: uc
            #import undetected_chromedriver as uc

            # method 6: Selenium Stealth
            #from selenium_stealth import stealth

            DEFAULT_ARGS = [
                '--disable-audio-output',
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-breakpad',
                '--disable-browser-side-navigation',
                '--disable-checker-imaging', 
                '--disable-client-side-phishing-detection',
                '--disable-default-apps',
                '--disable-demo-mode', 
                '--disable-dev-shm-usage',
                #'--disable-extensions',
                '--disable-features=site-per-process',
                '--disable-hang-monitor',
                '--disable-in-process-stack-traces', 
                '--disable-javascript-harmony-shipping', 
                '--disable-logging', 
                '--disable-notifications', 
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-perfetto',
                '--disable-permissions-api', 
                '--disable-plugins',
                '--disable-presentation-api',
                '--disable-reading-from-canvas', 
                '--disable-renderer-accessibility', 
                '--disable-renderer-backgrounding', 
                '--disable-shader-name-hashing', 
                '--disable-smooth-scrolling',
                '--disable-speech-api',
                '--disable-speech-synthesis-api',
                '--disable-sync',
                '--disable-translate',

                '--ignore-certificate-errors',

                '--metrics-recording-only',
                '--no-first-run',
                '--no-experiments',
                '--safebrowsing-disable-auto-update',
                #'--enable-automation',
                '--password-store=basic',
                '--use-mock-keychain',
                '--lang=zh-TW',
                '--stable-release-mode',
                '--use-mobile-user-agent', 
                '--webview-disable-safebrowsing-support',
                #'--no-sandbox',
                #'--incognito',
            ]

            chrome_options = webdriver.ChromeOptions()

            # for navigator.webdriver
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False,'profile.default_content_setting_values':{'notifications':2}})

            # default os is linux/mac
            chromedriver_path =Root_Dir+ "webdriver/chromedriver"
            if platform.system()=="windows":
                chromedriver_path =Root_Dir+ "webdriver/chromedriver.exe"

            #caps = DesiredCapabilities().CHROME
            caps = chrome_options.to_capabilities()

            #caps["pageLoadStrategy"] = u"normal"  #  complete
            caps["pageLoadStrategy"] = u"eager"  #  interactive
            #caps["pageLoadStrategy"] = u"none"
            
            #caps["unhandledPromptBehavior"] = u"dismiss and notify"  #  default
            caps["unhandledPromptBehavior"] = u"ignore"
            #caps["unhandledPromptBehavior"] = u"dismiss"

            # method 4:
            chrome_service = Service(chromedriver_path)

            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)


        if browser == "firefox":
            # default os is linux/mac
            chromedriver_path =Root_Dir+ "webdriver/geckodriver"
            if platform.system()=="windows":
                chromedriver_path =Root_Dir+ "webdriver/geckodriver.exe"

            firefox_service = Service(chromedriver_path)
            driver = webdriver.Firefox(service=firefox_service)

        time.sleep(1.0)

        # get url from dropdownlist.
        homepage_url = ""
        if len(homepage) > 0:
            target_str = u'http://'
            if target_str in homepage:
                target_index = homepage.find(target_str)
                homepage_url = homepage[target_index:]
            target_str = u'https://'
            if target_str in homepage:
                target_index = homepage.find(target_str)
                homepage_url = homepage[target_index:]

        if len(homepage_url) > 0:
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count >= 1:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except Exception as excSwithFail:
                pass

            driver.get(homepage_url)
            print("after homepage:", homepage_url)
    else:
        print("Config error!")

    return driver

# start to find dr name.
def tzuchi_OpdTimeShow(driver):
    ret = True

    is_dr_name_found = False

    el = None
    try:
        el = driver.find_element(By.ID, 'example')
    except Exception as exc:
        print("find #example fail, try to get all hyperlink")
        # try to find all.
        el = driver.find_element(By.TAG_NAME, 'body')

    el_reg_all = None
    if el is not None:
        #print("found example table")
        #example > tbody > tr:nth-child(24) > td:nth-child(2) > a:nth-child(4)
        try:
            el_reg_all = el.find_elements(By.TAG_NAME, 'a')
        except Exception as exc:
            print("find DR_NAME a hyperlink fail")

    if el_reg_all is not None:
        total_count = len(el_reg_all)
        for idx in range(total_count):
            # avoid over flow.
            target_index = (total_count-1)-idx
            if target_index < 0:
                target_index = 0
            if target_index > (total_count-1):
                target_index = (total_count-1)
            el_reg = el_reg_all[target_index]

            if not el_reg is None: 
                hyerlink_text = None
                try:
                    hyerlink_text = el_reg.text
                except Exception as exc:
                    #print(exc)
                    pass

                #print("idx:", idx, "text:", hyerlink_text)
                #print("I found hyerlink table:" + hyerlink_text)
                if not hyerlink_text is None:
                    try:
                        if dr_name in hyerlink_text:
                            is_dr_name_found = True
                    except Exception as exc:
                        print(exc)

                    if is_dr_name_found:
                        try:
                            el_reg.click()
                        except Exception as exc:
                            print(exc)
            
            if is_dr_name_found:
                break

    if not is_dr_name_found:
        # force reload!
        try:
            # this may cause fail!
            #print("refresh page")
            driver.refresh()
        except Exception as exc:
            #print("refresh fail")
            pass
        ret = False

    return ret

def tzuchi_RegNo(driver):
    is_fill_text_by_app = False

    print("check 初診.")
    # for "first time"
    # 初診/複診

    visit_time_html_id = 'MainContent_rblRegFM_1'
    if visit_time == '初診':
        visit_time_html_id = 'MainContent_rblRegFM_0'

    el_radio = None
    try:
        # direct user version 2:
        el_radio = driver.find_element(By.ID, visit_time_html_id)
    except Exception as exc:
        pass
        #print("find #visit_time_html_id fail")

    if el_radio is not None:
        try:
            if not el_radio.is_selected():
                el_radio.click()
        except Exception as exc:
            print("click MainContent_rblRegFM_0 radio fail")

    # for User Gender
    # 男/女 

    user_gender_html_id = 'MainContent_rtbSexType_0'
    if user_gender == '女':
        user_gender_html_id = 'MainContent_rtbSexType_1'

    el_radio = None
    try:
        # direct user version 2:
        el_radio = driver.find_element(By.ID, user_gender_html_id)
    except Exception as exc:
        pass
        #print("find #user_gender_html_id fail")

    if el_radio is not None:
        try:
            if not el_radio.is_selected():
                el_radio.click()
        except Exception as exc:
            print("click user_gender_html_id radio fail")

    # for "ID type"
    el_radio = None
    try:
        # version 1:
        el_radio = driver.find_element(By.ID, 'rblRegFM_0')
    except Exception as exc:
        print("find #rblRegFM_0 fail")
        # version 2:
        try:
            el_radio = driver.find_element(By.ID, 'MainContent_IdSelectType2_0')
        except Exception as exc:
            pass
            #print("find #MainContent_IdSelectType2_0 fail")

    if el_radio is not None:
        try:
            if not el_radio.is_selected():
                el_radio.click()
        except Exception as exc:
            print("click MainContent_IdSelectType2_0 radio fail")

    # for "ID type" case 2.
    # when 初診, id name is different.
    
    el_radio = None
    try:
        # version 2:
        el_radio = driver.find_element(By.ID, 'MainContent_IdSelectType1_0')
    except Exception as exc:
        pass
        #222print("find #MainContent_IdSelectType1_0 fail")

    if el_radio is not None:
        try:
            if not el_radio.is_selected():
                el_radio.click()
        except Exception as exc:
            print("click MainContent_IdSelectType1_0 radio fail")


    el_text_id = None
    try:
        el_text_id = driver.find_element(By.ID, 'txtMRNo')
    except Exception as exc:
        print("find #txtMRNo fail")
        
        # version 2:
        try:
            el_text_id = driver.find_element(By.ID, 'MainContent_tbxMRNo')
        except Exception as exc:
            print("find #MainContent_tbxMRNo fail")

    if el_text_id is not None:
        try:
            text_id_value = str(el_text_id.get_attribute('value'))
            if text_id_value == "":
                #el_text_id.click()
                print("try to send keys")
                el_text_id.send_keys(user_id)
                is_fill_text_by_app = True
        except Exception as exc:
            print("send user_id fail")

    # user name
    el_text_name = None
    try:
        # direct, version 2:
        el_text_name = driver.find_element(By.ID, 'MainContent_tbxName')
    except Exception as exc:
        pass
        #print("find #MainContent_tbxName fail")

    if el_text_name is not None:
        print("found MainContent_tbxName")
        try:
            text_name_value = str(el_text_name.get_attribute('value'))
            if text_name_value == "":
                print("try to send keys:", user_name)
                el_text_name.send_keys(user_name)
                is_fill_text_by_app = True
            else:
                pass
                print("text not empty, value:", text_name_value)
        except Exception as exc:
            print("sned MainContent_tbxName fail")


    # tel
    el_text_tel = None
    try:
        el_text_tel = driver.find_element(By.ID, 'txtTel')
    except Exception as exc:
        pass
        #print("find #txtTel fail")

        # version 2:
        try:
            el_text_tel = driver.find_element(By.ID, 'MainContent_tbxTel')
        except Exception as exc:
            pass
            #print("find #MainContent_tbxTel fail")

    if el_text_tel is not None:
        try:
            text_tel_value = str(el_text_tel.get_attribute('value'))
            if text_tel_value == "":
                #el_text_tel.click()
                print("try to send keys")
                el_text_tel.send_keys(user_tel)
                is_fill_text_by_app = True
        except Exception as exc:
            print("sned user_tel fail")


    # birthday
    el_text_birthday = None
    try:
        # direct, version 2:
        el_text_birthday = driver.find_element(By.ID, 'MainContent_tbxBirthday')
    except Exception as exc:
        pass
        #print("find #MainContent_tbxBirthday fail")

    if el_text_birthday is not None:
        try:
            text_birthday_value = str(el_text_birthday.get_attribute('value'))
            if text_birthday_value == "":
                #el_text_tel.click()
                print("try to send keys")
                el_text_birthday.send_keys(user_birthday)
                is_fill_text_by_app = True
        except Exception as exc:
            print("sned MainContent_tbxBirthday fail")


    #print("is_fill_text_by_app",is_fill_text_by_app)
    if is_fill_text_by_app:
        el_text_captcha = None
        try:
            # direct, version 1:
            el_text_captcha = driver.find_element(By.ID, 'txtVCode')
        except Exception as exc:
            print("find #txtVCode fail")
            # direct, version 2:
            try:
                el_text_captcha = driver.find_element(By.ID, 'MainContent_tbxVCode')
            except Exception as exc:
                print("find #MainContent_tbxVCode fail")

        if el_text_captcha is not None:
            try:
                el_text_captcha.click()
            except Exception as exc:
                print("focus el_text_captcha fail")

        if enable_captcha_ocr:
            img_captcha = None
            try:
                img_captcha = driver.find_element(By.ID, 'imgVI')
            except Exception as exc:
                print("find #imgVI fail")

            if img_captcha is not None:
                try:
                    img_captcha.screenshot('captcha.png')
                except Exception as exc:
                    print("focus el_text_captcha fail")

def tzuchi_reg(url, driver):
    #print("tzuchi_reg")
    ret = True

    # step 1: list all dept.
    if "/SecList_DL.aspx" in url:
        pass

    # step 2: get the first hyperlink.
    is_match_dr_page_url = False
    dr_page_list = ['/OpdTimeShow.aspx', '/OpdTimeShow?']
    for each_page in dr_page_list:
        #print("each_page:", each_page)
        if each_page in url:
            is_match_dr_page_url = True
            break
    if is_match_dr_page_url:
        #print("star to query dr name hyperlink")
        ret = tzuchi_OpdTimeShow(driver)

    # step 3: reg
    # app.tzuchi.com.tw/tchw/opdreg/RegNo.aspx
    reg_form_list = ['/RegNo.aspx', '/RegNo?']
    for each_page in reg_form_list:
        if each_page in url:
            tzuchi_RegNo(driver)
            break

    return ret

def main():
    global driver
    driver = load_config_from_local(driver)

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    global debugMode
    if debugMode:
        print("Start to looping, detect browser url...")

    while True:
        time.sleep(0.1)

        is_alert_popup = False

        # pass if driver not loaded.
        if driver is None:
            continue

        '''
        try:
            if not driver is None:
                WebDriverWait(driver, 0.1).until(EC.alert_is_present(),
                                               'Timed out waiting for PA creation confirmation popup to appear.')
            #print("alert popup")
            is_pass_alert = False
            if last_url == "":
                is_pass_alert = True

            if u'SecList_DL.aspx' in last_url:
                is_pass_alert = True

            if u'OpdTimeShow.aspx' in last_url:
                is_pass_alert = True
                pass

            print("is_pass_alert:", is_pass_alert)
            if is_pass_alert:
                alert = None
                if not driver is None:
                    alert = driver.switch_to.alert
                if not alert is None:
                    alert.accept()
                    #print("alert accepted")
            else:
                is_alert_popup = True
        except TimeoutException:
            #print("no alert")
            pass
        '''

        default_close_alert_text = [
        u'「南區醫院總額醫療服務審查分級作業原則」'
        , u'無開放現場掛號及人工電話掛號'
        , u'健康檢查不需掛號，請逕洽服務台'
        ]
        try:
            alert = None
            if not driver is None:
                alert = driver.switch_to.alert
            if not alert is None:
                if not alert.text is None:
                    is_match_auto_close_text = False
                    for txt in default_close_alert_text:
                        if len(txt) > 0:
                            if txt in alert.text:
                                is_match_auto_close_text = True
                    #print("alert3 text:", alert.text)

                    if is_match_auto_close_text:
                        alert.accept()
                        #print("alert3 accepted")

                    is_alert_popup = True
            else:
                print("alert3 not detected")
        except NoAlertPresentException as exc1:
            #logger.error('NoAlertPresentException for alert')
            pass
        except NoSuchWindowException:
            #print('NoSuchWindowException2 at this url:', url )
            #print("last_url:", last_url)
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count >= 1:
                    driver.switch_to.window(driver.window_handles[0])
            except Exception as excSwithFail:
                pass
        except Exception as exc:
            logger.error('Exception2 for alert')
            logger.error(exc, exc_info=True)

        #MUST "do nothing: if alert popup.
        #print("is_alert_popup:", is_alert_popup)
        if is_alert_popup:
            continue

        url = ""
        try:
            url = driver.current_url
        except NoSuchWindowException:
            #print('NoSuchWindowException at this url:', url )
            #print("last_url:", last_url)
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count >= 1:
                    driver.switch_to.window(driver.window_handles[0])
            except Exception as excSwithFail:
                pass

        except UnexpectedAlertPresentException as exc1:
            #print('UnexpectedAlertPresentException at this url:', url )
            #print("last_url:", last_url)

            is_pass_alert = False
            if last_url == "":
                is_pass_alert = True

            if u'SecList_DL.aspx' in last_url:
                is_pass_alert = True

            if u'OpdTimeShow.aspx' in last_url:
                pass
                #is_pass_alert = True

            print("is_pass_alert:", is_pass_alert)

            if is_pass_alert:
                try:
                    driver.switch_to.alert.accept()
                    #print('Alarm! ALARM!')
                except NoAlertPresentException:
                    pass
                    #print('*crickets*')
        
        except Exception as exc:
            logger.error('Exception')
            logger.error(exc, exc_info=True)

            #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
            str_exc = ""
            try:
                str_exc = str(exc)
            except Exception as exc2:
                pass

            if len(str_exc)==0:
                str_exc = repr(exc)
            
            exit_bot_error_strings = [u'Max retries exceeded with url', u'chrome not reachable', u'without establishing a connection']
            for str_chrome_not_reachable in exit_bot_error_strings:
                # for python2
                try:
                    basestring
                    if isinstance(str_chrome_not_reachable, unicode):
                        str_chrome_not_reachable = str(str_chrome_not_reachable)
                except NameError:  # Python 3.x
                    basestring = str

                if isinstance(str_exc, str):
                    if str_chrome_not_reachable in str_exc:
                        print(u'quit bot')
                        driver.quit()
                        import sys
                        sys.exit()

            print("exc", str_exc)
            pass
            
        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        # 說明：輸出目前網址，覺得吵的話，請註解掉這行。
        if debugMode:
            print("url:", url)

        if len(url) > 0 :
            if url != last_url:
                print(url)
            last_url = url

        # 
        tzuchi_domain_list = ['tzuchi-healthcare.org.tw','tzuchi.com.tw']
        for each_domain in tzuchi_domain_list:
            if each_domain in url:
                ret = tzuchi_reg(url, driver)
                if ret == False:
                    #last_url = u"https://app.tzuchi.com.tw/tchw/opdreg/SecList_DL.aspx"
                    pass

main()