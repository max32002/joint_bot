#!/usr/bin/env python3
#encoding=utf-8
#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
import json
import logging
import os
import pathlib
import platform
import random
import re
import sys
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import (NoAlertPresentException,
                                        NoSuchWindowException,
                                        UnexpectedAlertPresentException,
                                        WebDriverException)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

#from DrissionPage import ChromiumPage

logging.basicConfig()
logger = logging.getLogger('logger')
import warnings

# for check kktix reg_info
import requests
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore',InsecureRequestWarning)
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# ocr
import base64

try:
    import ddddocr

    #PS: python 3.11+ raise PIL conflict.
    from NonBrowser import NonBrowser
except Exception as exc:
    pass

import argparse
import webbrowser

import chromedriver_autoinstaller

CONST_APP_VERSION = "MaxRegBot (2023.11.29)"

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"
CONST_WEBDRIVER_TYPE_DP = "DrissionPage"

def force_press_button(driver, select_by, select_query, force_submit=True):
    ret = False
    next_step_button = None
    try:
        next_step_button = driver.find_element(select_by ,select_query)
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True
    except Exception as exc:
        #print("find %s clickable Exception:" % (select_query))
        #print(exc)
        pass

        if force_submit:
            if not next_step_button is None:
                is_visible = False
                try:
                    if next_step_button.is_enabled():
                        is_visible = True
                except Exception as exc:
                    pass

                if is_visible:
                    try:
                        driver.set_script_timeout(1)
                        driver.execute_script("arguments[0].click();", next_step_button)
                        ret = True
                    except Exception as exc:
                        pass
    return ret

def assign_text(driver, by, query, val, overwrite = False, submit=False, overwrite_when = ""):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if val is None:
        val = ""

    is_visible = False

    if len(val) > 0:
        el_text = None
        try:
            el_text = driver.find_element(by, query)
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if not el_text is None:
            try:
                if el_text.is_enabled() and el_text.is_displayed():
                    is_visible = True
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass

    is_text_sent = False
    if is_visible:
        try:
            inputed_text = el_text.get_attribute('value')
            if not inputed_text is None:
                is_do_keyin = False
                if len(inputed_text) == 0:
                    is_do_keyin = True
                else:
                    if inputed_text == val:
                        is_text_sent = True
                    else:
                        if len(overwrite_when) > 0:
                            if overwrite_when == inputed_text:
                                overwrite = True
                        if overwrite:
                            is_do_keyin = True

                if is_do_keyin:
                    if len(inputed_text) > 0:
                        builder = ActionChains(driver)
                        builder.move_to_element(el_text)
                        builder.click(el_text)
                        if platform.system() == 'Darwin':
                            builder.key_down(Keys.COMMAND)
                        else:
                            builder.key_down(Keys.CONTROL)
                        builder.send_keys("a")
                        if platform.system() == 'Darwin':
                            builder.key_up(Keys.COMMAND)
                        else:
                            builder.key_up(Keys.CONTROL)
                        builder.send_keys(val)
                        if submit:
                            builder.send_keys(Keys.ENTER)
                        builder.perform()
                    else:
                        el_text.click()
                        el_text.send_keys(val)
                        if submit:
                            el_text.send_keys(Keys.ENTER)
                    is_text_sent = True
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

    return is_text_sent

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

def get_favoriate_extension_path(webdriver_path):
    #print("webdriver_path:", webdriver_path)
    extension_list = []
    return extension_list

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_chrome_options(webdriver_path, config_dict):
    browser=config_dict["browser"]

    chrome_options = webdriver.ChromeOptions()
    if browser=="edge":
        chrome_options = webdriver.EdgeOptions()
    if browser=="safari":
        chrome_options = webdriver.SafariOptions()

    # some windows cause: timed out receiving message from renderer
    if config_dict["advanced"]["adblock_plus_enable"]:
        # PS: this is ocx version.
        extension_list = get_favoriate_extension_path(webdriver_path)
        for ext in extension_list:
            if os.path.exists(ext):
                chrome_options.add_extension(ext)

    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--lang=zh-TW')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument("--no-sandbox");
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    if browser=="brave":
        brave_path = get_brave_bin_path()
        if os.path.exists(brave_path):
            chrome_options.binary_location = brave_path

    chrome_options.page_load_strategy = 'eager'
    #chrome_options.page_load_strategy = 'none'
    chrome_options.unhandled_prompt_behavior = "accept"

    return chrome_options

def load_chromdriver_normal(config_dict, driver_type):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    driver = None

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(webdriver_path):
        os.mkdir(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("WebDriver not exist, try to download to:", webdriver_path)
        chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)

    if not os.path.exists(chromedriver_path):
        print("Please download chromedriver and extract zip to webdriver folder from this url:")
        print("請下在面的網址下載與你chrome瀏覽器相同版本的chromedriver,解壓縮後放到webdriver目錄裡：")
        print(URL_CHROME_DRIVER)
    else:
        chrome_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict)
        try:
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            if show_debug_message:
                print(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

                # remove exist chromedriver, download again.
                try:
                    print("Deleting exist and download ChromeDriver again.")
                    os.unlink(chromedriver_path)
                except Exception as exc2:
                    print(exc2)
                    pass

                chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)
                chrome_service = Service(chromedriver_path)
                try:
                    chrome_options = get_chrome_options(webdriver_path, config_dict)
                    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
                except Exception as exc2:
                    print("Selenium 4.11.0 Release with Chrome For Testing Browser.")
                    try:
                        chrome_options = get_chrome_options(webdriver_path, config_dict)
                        driver = webdriver.Chrome(service=Service(), options=chrome_options)
                    except Exception as exc3:
                        print(exc3)
                        pass

    return driver

def clean_uc_exe_cache():
    exe_name = "chromedriver%s"

    platform = sys.platform
    if platform.endswith("win32"):
        exe_name %= ".exe"
    if platform.endswith(("linux", "linux2")):
        exe_name %= ""
    if platform.endswith("darwin"):
        exe_name %= ""

    d = ""
    if platform.endswith("win32"):
        d = "~/appdata/roaming/undetected_chromedriver"
    elif "LAMBDA_TASK_ROOT" in os.environ:
        d = "/tmp/undetected_chromedriver"
    elif platform.startswith(("linux", "linux2")):
        d = "~/.local/share/undetected_chromedriver"
    elif platform.endswith("darwin"):
        d = "~/Library/Application Support/undetected_chromedriver"
    else:
        d = "~/.undetected_chromedriver"
    data_path = os.path.abspath(os.path.expanduser(d))

    is_cache_exist = False
    p = pathlib.Path(data_path)
    files = list(p.rglob("*chromedriver*?"))
    for file in files:
        if os.path.exists(str(file)):
            is_cache_exist = True
            try:
                os.unlink(str(file))
            except Exception as exc2:
                print(exc2)
                pass

    return is_cache_exist

def get_uc_options(uc, config_dict, webdriver_path):
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    #options.page_load_strategy = 'none'
    options.unhandled_prompt_behavior = "accept"

    #print("strategy", options.page_load_strategy)

    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')
    options.add_argument('--disable-web-security')
    options.add_argument("--no-sandbox");
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    if config_dict["browser"]=="brave":
        brave_path = get_brave_bin_path()
        if os.path.exists(brave_path):
            options.binary_location = brave_path

    return options

def load_chromdriver_uc(config_dict):
    import undetected_chromedriver as uc

    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    chromedriver_path = get_chromedriver_path(webdriver_path)

    if not os.path.exists(webdriver_path):
        os.mkdir(webdriver_path)

    if not os.path.exists(chromedriver_path):
        print("ChromeDriver not exist, try to download to:", webdriver_path)
        try:
            chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)
        except Exception as exc:
            print(exc)
    else:
        print("ChromeDriver exist:", chromedriver_path)

    driver = None
    if os.path.exists(chromedriver_path):
        # use chromedriver_autodownload instead of uc auto download.
        is_cache_exist = clean_uc_exe_cache()

        try:
            options = get_uc_options(uc, config_dict, webdriver_path)
            driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options, headless=config_dict["advanced"]["headless"])
        except Exception as exc:
            print(exc)
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

            # remove exist chromedriver, download again.
            try:
                print("Deleting exist and download ChromeDriver again.")
                os.unlink(chromedriver_path)
            except Exception as exc2:
                print(exc2)
                pass

            try:
                chromedriver_autoinstaller.install(path=webdriver_path, make_version_dir=False)
                options = get_uc_options(uc, config_dict, webdriver_path)
                driver = uc.Chrome(driver_executable_path=chromedriver_path, options=options)
            except Exception as exc2:
                print(exc2)
                pass
    else:
        print("WebDriver not found at path:", chromedriver_path)

    if driver is None:
        print('WebDriver object is None..., try again..')
        try:
            options = get_uc_options(uc, config_dict, webdriver_path)
            driver = uc.Chrome(options=options)
        except Exception as exc:
            print(exc)
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
            pass

    if driver is None:
        print("create web drive object by undetected_chromedriver fail!")

        if os.path.exists(chromedriver_path):
            print("Unable to use undetected_chromedriver, ")
            print("try to use local chromedriver to launch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(config_dict, driver_type)
        else:
            print("建議您自行下載 ChromeDriver 到 webdriver 的資料夾下")
            print("you need manually download ChromeDriver to webdriver folder.")

    return driver

def close_browser_tabs(driver):
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count > 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

def get_driver_by_config(config_dict):
    global driver

    language = "English"

    # read config.
    homepage = config_dict["homepage"]
    browser = config_dict["browser"]

    if " http" in homepage:
        homepage = " http" + homepage.split(" http")[1]

    # output config:
    print("maxbot app version", CONST_APP_VERSION)
    print("python version", platform.python_version())
    print("platform", platform.platform())
    print("homepage", homepage)

    print("==[advanced]==")
    if config_dict["advanced"]["verbose"]:
        print(config_dict["advanced"])

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    print("platform.system().lower():", platform.system().lower())

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    #print("platform.system().lower():", platform.system().lower())

    if config_dict["browser"] in ["chrome","brave"]:
        # method 6: Selenium Stealth
        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_SELENIUM:
            driver = load_chromdriver_normal(config_dict, config_dict["webdriver_type"])
        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_UC:
            # method 5: uc
            # multiprocessing not work bug.
            if platform.system().lower()=="windows":
                if hasattr(sys, 'frozen'):
                    from multiprocessing import freeze_support
                    freeze_support()
            driver = load_chromdriver_uc(config_dict)
        if config_dict["webdriver_type"] == CONST_WEBDRIVER_TYPE_DP:
            #driver = ChromiumPage()
            pass

    if config_dict["browser"] == "firefox":
        # default os is linux/mac
        # download url: https://github.com/mozilla/geckodriver/releases
        chromedriver_path = os.path.join(webdriver_path,"geckodriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")

        if "macos" in platform.platform().lower():
            if "arm64" in platform.platform().lower():
                chromedriver_path = os.path.join(webdriver_path,"geckodriver_arm")

        webdriver_service = Service(chromedriver_path)
        driver = None
        try:
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if config_dict["advanced"]["headless"]:
                options.add_argument('--headless')
                #options.add_argument('--headless=new')
            if platform.system().lower()=="windows":
                binary_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = os.path.expanduser('~') + "\\AppData\\Local\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
                if not os.path.exists(binary_path):
                    binary_path = "D:\\Program Files\\Mozilla Firefox\\firefox.exe"
                options.binary_location = binary_path

            driver = webdriver.Firefox(service=webdriver_service, options=options)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)
            else:
                print(exc)

    if config_dict["browser"] == "edge":
        # default os is linux/mac
        # download url: https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/
        chromedriver_path = os.path.join(webdriver_path,"msedgedriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"msedgedriver.exe")

        webdriver_service = Service(chromedriver_path)
        chrome_options = get_chrome_options(webdriver_path, config_dict)

        driver = None
        try:
            driver = webdriver.Edge(service=webdriver_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if config_dict["browser"] == "safari":
        driver = None
        try:
            driver = webdriver.Safari()
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if driver is None:
        print("create web driver object fail @_@;")
    else:
        try:
            print("goto url:", homepage)
            driver.get(homepage)
            time.sleep(3.0)
        except Exception as exc:
            print('get URL Exception:', exc)
            pass

    return driver

    if driver is None:
        print("create web driver object fail @_@;")
    else:
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

        try:
            print("goto url:", homepage_url)
            driver.get(homepage_url)
        except WebDriverException as exce2:
            print('oh no not again, WebDriverException')
            print('WebDriverException:', exce2)
        except Exception as exce1:
            print('get URL Exception:', exce1)
            pass

    return driver


# start to find dr name.
def tzuchi_OpdTimeShow(driver, config_dict):
    ret = True

    dr_name = config_dict["dr_name"]
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

def reload_captcha(driver):
    el_btn = None
    try:
        el_btn = driver.find_element(By.ID, 'Button4')
        if not el_btn is None:
            el_btn.click()
    except Exception as exc:
        pass

def auto_ocr(driver, ocr, previous_answer, Captcha_Browser, ocr_captcha_image_source):
    show_debug_message = True       # debug.
    show_debug_message = False      # online
    #print("start to ddddocr")

    is_need_redo_ocr = False

    orc_answer = None
    if not ocr is None:
        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.Request_Captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'MainContent_imgVI'
            try:
                form_verifyCode_base64 = driver.execute_async_script("""
                    var canvas = document.createElement('canvas');
                    var context = canvas.getContext('2d');
                    var img = document.getElementById('%s');
                    canvas.height = img.naturalHeight;
                    canvas.width = img.naturalWidth;
                    context.drawImage(img, 0, 0);
                    callback = arguments[arguments.length - 1];
                    callback(canvas.toDataURL());
                    """ % (image_id))
                img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
            except Exception as exc:
                if show_debug_message:
                    print("canvas exception:", str(exc))
                pass
        if not img_base64 is None:
            try:
                orc_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass
        else:
            if previous_answer is None:
                # page is not ready, retry again.
                # PS: usually occur in async script get captcha image.
                is_need_redo_ocr = True
                time.sleep(0.1)

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))

    else:
        print("ddddocr is None")

    is_form_sumbited = False
    if not orc_answer is None:
        orc_answer = orc_answer.strip()
        print("orc_answer:", orc_answer)
        if len(orc_answer)==5:
            is_form_sumbited = assign_text(driver, By.CSS_SELECTOR, '#MainContent_tbxVCode', orc_answer)
        else:
            is_need_redo_ocr = True

            if previous_answer != orc_answer:
                previous_answer = orc_answer
                print("get new captcha.")
                reload_captcha(driver)

                if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                    time.sleep(0.1)

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def tzuchi_RegNo(driver, config_dict, ocr, Captcha_Browser):
    ocr_captcha_enable = config_dict["ocr_captcha"]["enable"]

    visit_time = config_dict["visit_time"]
    user_id = config_dict["user_id"]
    user_name = config_dict["user_name"]
    user_tel = config_dict["user_tel"]
    user_birthday = config_dict["user_birthday"]
    user_sextype = config_dict["user_sextype"]

    #print("check 初診.")
    # for "first time"
    # 初診/複診

    visit_time_html_id = 'rblRegFM_1'
    if visit_time == '初診':
        visit_time_html_id = 'rblRegFM_0'

    # default is 複診
    el_radio = None
    try:
        # version 1:
        el_radio = driver.find_element(By.ID, visit_time_html_id)
    except Exception as exc:
        pass
        #print("find #visit_time_html_id fail")
        
        # version 2:
        try:
            el_radio = driver.find_element(By.ID, 'MainContent_'+visit_time_html_id)
        except Exception as exc:
            print("find #MainContent_tbxMRNo fail")

    if el_radio is not None:
        try:
            if not el_radio.is_selected():
                el_radio.click()
        except Exception as exc:
            print("click rblRegFM_0 radio fail")

    sextyp_html_id = 'MainContent_rtbSexType_0'
    if user_sextype == '女':
        sextyp_html_id = 'MainContent_rtbSexType_1'
    if user_sextype == '不明':
        sextyp_html_id = 'MainContent_rtbSexType_2'

    el_radio = None
    try:
        el_radio = driver.find_element(By.ID, sextyp_html_id)
        if el_radio is not None:
            if not el_radio.is_selected():
                el_radio.click()
    except Exception as exc:
        pass


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

    is_id_sent = False
    if el_text_id is not None:
        try:
            text_id_value = str(el_text_id.get_attribute('value'))
            if len(text_id_value) == 0:
                #el_text_id.click()
                print("try to send keys")
                el_text_id.send_keys(user_id)
                is_id_sent = True
            else:
                is_id_sent = True
        except Exception as exc:
            print("send user_id fail")

    # user name
    is_name_sent = assign_text(driver, By.CSS_SELECTOR, '#MainContent_SpanName > input', user_name)

    # tel
    is_tel_sent = assign_text(driver, By.CSS_SELECTOR, '#MainContent_tbxTel', user_tel)

    # birthday
    is_birthday_sent = assign_text(driver, By.CSS_SELECTOR, '#MainContent_spnBirthday > input', user_birthday)

    is_form_sumbited = False
    if is_id_sent:
        if ocr_captcha_enable:
            ocr_captcha_image_source = CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS
            previous_answer = None

            for redo_ocr in range(9):
                is_need_redo_ocr, previous_answer, is_form_sumbited =  auto_ocr(driver, ocr, previous_answer, Captcha_Browser, ocr_captcha_image_source)
                if is_form_sumbited:
                    is_verifyCode_editing = False
                    break
                if not is_need_redo_ocr:
                    break

            if is_form_sumbited:
                print("is_form_sumbited:", is_form_sumbited)
                is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'input[value="掛號"]')
                print("is_button_clicked:", is_button_clicked)
                
                if not is_button_clicked:
                    # plan B.
                    try:
                        print("run js")
                        js="return Confirm();"
                        driver.execute_script(js)
                        pass
                    except Exception as exc:
                        print(exc)
                        pass
                
                try:
                    # Wait for the alert to be displayed and store it in a variable
                    wait = WebDriverWait(driver, 1)
                    alert = wait.until(EC.alert_is_present())

                    # Store the alert text in a variable
                    text = alert.text
                    print("popup alert.text", text)

                    # Press the OK button
                    alert.accept()                
                except Exception as exc:
                    print(exc)
                    pass

    return is_form_sumbited


def get_current_url(driver):
    DISCONNECTED_MSG = ': target window already closed'

    url = ""
    is_quit_bot = False

    try:
        url = driver.current_url
    except NoSuchWindowException:
        print('NoSuchWindowException at this url:', url )
        #print("last_url:", last_url)
        #print("get_log:", driver.get_log('driver'))
        window_handles_count = 0
        try:
            window_handles_count = len(driver.window_handles)
            #print("window_handles_count:", window_handles_count)
            if window_handles_count >= 1:
                driver.switch_to.window(driver.window_handles[0])
                driver.switch_to.default_content()
                time.sleep(0.2)
        except Exception as excSwithFail:
            #print("excSwithFail:", excSwithFail)
            pass
        if window_handles_count==0:
            try:
                driver_log = driver.get_log('driver')[-1]['message']
                print("get_log:", driver_log)
                if DISCONNECTED_MSG in driver_log:
                    print('quit bot by NoSuchWindowException')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()
            except Exception as excGetDriverMessageFail:
                #print("excGetDriverMessageFail:", excGetDriverMessageFail)
                except_string = str(excGetDriverMessageFail)
                if 'HTTP method not allowed' in except_string:
                    print('quit bot by close browser')
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

    except UnexpectedAlertPresentException as exc1:
        print('UnexpectedAlertPresentException at this url:', url )
        # PS: do nothing...
        # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
        # raise exception at selenium/webdriver/remote/errorhandler.py
        # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
        is_pass_alert = False
        is_pass_alert = True
        if is_pass_alert:
            try:
                driver.switch_to.alert.accept()
            except Exception as exc:
                pass

    except Exception as exc:
        logger.error('Maxbot URL Exception')
        logger.error(exc, exc_info=True)

        #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
        str_exc = ""
        try:
            str_exc = str(exc)
        except Exception as exc2:
            pass

        if len(str_exc)==0:
            str_exc = repr(exc)

        exit_bot_error_strings = ['Max retries exceeded'
        , 'chrome not reachable'
        , 'unable to connect to renderer'
        , 'failed to check if window was closed'
        , 'Failed to establish a new connection'
        , 'Connection refused'
        , 'disconnected'
        , 'without establishing a connection'
        , 'web view not found'
        , 'invalid session id'
        ]
        for each_error_string in exit_bot_error_strings:
            if isinstance(str_exc, str):
                if each_error_string in str_exc:
                    print('quit bot by error:', each_error_string)
                    is_quit_bot = True
                    driver.quit()
                    sys.exit()

        # not is above case, print exception.
        print("Exception:", str_exc)
        pass

    return url, is_quit_bot

def tzuchi_main(driver, url, config_dict, tzuchi_dict, ocr, Captcha_Browser):
    # get the first hyperlink.
    is_match_dr_page_url = False
    dr_page_list = ['/OpdTimeShow.aspx', '/OpdTimeShow?']
    for each_page in dr_page_list:
        #print("each_page:", each_page)
        if each_page in url:
            is_match_dr_page_url = True
            break
    if is_match_dr_page_url:
        #print("star to query dr name hyperlink")
        ret = tzuchi_OpdTimeShow(driver, config_dict)

    # step 3: reg
    # app.tzuchi.com.tw/tchw/opdreg/RegNo.aspx
    is_match_reg_page_url = False
    reg_form_list = ['/RegNo.aspx', '/RegNo?']
    for each_page in reg_form_list:
        if each_page in url:
            is_match_reg_page_url = True
            
            break

    if is_match_reg_page_url:
        if not tzuchi_dict["is_popup_alert"]:
            is_form_sumbited = tzuchi_RegNo(driver, config_dict, ocr, Captcha_Browser)
            if is_form_sumbited:
                tzuchi_dict["is_popup_alert"] = True
    else:
        # reset
        tzuchi_dict["is_popup_alert"] = False

    return tzuchi_dict


def main():
    config_dict = get_config_dict()

    driver = None
    if not config_dict is None:
        driver = get_driver_by_config(config_dict)
    else:
        print("Load config error!")

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    # for tzuchi
    tzuchi_dict = {}
    tzuchi_dict["is_popup_alert"] = False


    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
            Captcha_Browser = NonBrowser()
    except Exception as exc:
        pass


    while True:
        time.sleep(0.05)

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        url, is_quit_bot = get_current_url(driver)
        if is_quit_bot:
            break

        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        # 說明：輸出目前網址，覺得吵的話，請註解掉這行。
        #print("url:", url)

        if len(url) > 0 :
            if url != last_url:
                print(url)
            last_url = url



        tzuchi_domain_list = ['tzuchi-healthcare.org.tw','tzuchi.com.tw']
        for each_domain in tzuchi_domain_list:
            if each_domain in url:
                tzuchi_dict = tzuchi_main(driver, url, config_dict, tzuchi_dict, ocr, Captcha_Browser)

if __name__ == "__main__":
    main()
