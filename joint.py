#!/usr/bin/env python3
#encoding=utf-8
import os
import sys
import platform
import json

from selenium import webdriver
# for close tab.
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# for selenium 4
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
# for wait #1
import time

import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

# ocr
import base64
try:
    import ddddocr
    #PS: python 3.11.1 raise PIL conflict.
    from NonBrowser import NonBrowser
except Exception as exc:
    pass

import ssl
ssl._create_default_https_context = ssl._create_unverified_context


CONST_APP_VERSION = "MaxRegBot (2023.02.19)"

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
#CONST_WEBDRIVER_TYPE_STEALTH = "stealth"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"

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
    no_google_analytics_path = os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx")
    no_ad_path = os.path.join(webdriver_path,"Adblock_3.15.2.0.crx")
    return no_google_analytics_path, no_ad_path

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_chrome_options(webdriver_path, adblock_plus_enable, browser="chrome"):
    chrome_options = webdriver.ChromeOptions()
    if browser=="edge":
        chrome_options = webdriver.EdgeOptions()
    if browser=="safari":
        chrome_options = webdriver.SafariOptions()

    # some windows cause: timed out receiving message from renderer
    if adblock_plus_enable:
        # PS: this is ocx version.
        no_google_analytics_path, no_ad_path = get_favoriate_extension_path(webdriver_path)

        if os.path.exists(no_google_analytics_path):
            chrome_options.add_extension(no_google_analytics_path)
        if os.path.exists(no_ad_path):
            chrome_options.add_extension(no_ad_path)

    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--lang=zh-TW')

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})

    #caps = DesiredCapabilities().CHROME
    caps = chrome_options.to_capabilities()

    #caps["pageLoadStrategy"] = u"normal"  #  complete
    caps["pageLoadStrategy"] = u"eager"  #  interactive
    #caps["pageLoadStrategy"] = u"none"

    #caps["unhandledPromptBehavior"] = u"dismiss and notify"  #  default
    #caps["unhandledPromptBehavior"] = u"ignore"
    #caps["unhandledPromptBehavior"] = u"dismiss"
    caps["unhandledPromptBehavior"] = u"accept"

    return chrome_options, caps

def load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable):
    chromedriver_path = get_chromedriver_path(webdriver_path)
    chrome_service = Service(chromedriver_path)
    chrome_options, caps = get_chrome_options(webdriver_path, adblock_plus_enable)
    driver = None
    try:
        # method 6: Selenium Stealth
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options, desired_capabilities=caps)
    except Exception as exc:
        error_message = str(exc)
        left_part = None
        if "Stacktrace:" in error_message:
            left_part = error_message.split("Stacktrace:")[0]
            print(left_part)

        if "This version of ChromeDriver only supports Chrome version" in error_message:
            print(CONST_CHROME_VERSION_NOT_MATCH_EN)
            print(CONST_CHROME_VERSION_NOT_MATCH_TW)

    if driver_type=="stealth":
        from selenium_stealth import stealth
        # Selenium Stealth settings
        stealth(driver,
              languages=["zh-TW", "zh"],
              vendor="Google Inc.",
              platform="Win32",
              webgl_vendor="Intel Inc.",
              renderer="Intel Iris OpenGL Engine",
              fix_hairline=True,
          )
    #print("driver capabilities", driver.capabilities)

    return driver

def load_chromdriver_uc(webdriver_path, adblock_plus_enable):
    import undetected_chromedriver as uc

    chromedriver_path = get_chromedriver_path(webdriver_path)

    options = uc.ChromeOptions()
    options.page_load_strategy="eager"

    #print("strategy", options.page_load_strategy)

    if adblock_plus_enable:
        no_google_analytics_path, no_ad_path = get_favoriate_extension_path(webdriver_path)
        no_google_analytics_folder_path = no_google_analytics_path.replace('.crx','')
        no_ad_folder_path = no_ad_path.replace('.crx','')
        load_extension_path = ""
        if os.path.exists(no_google_analytics_folder_path):
            load_extension_path += "," + no_google_analytics_folder_path
        if os.path.exists(no_ad_folder_path):
            load_extension_path += "," + no_ad_folder_path
        if len(load_extension_path) > 0:
            options.add_argument('--load-extension=' + load_extension_path[1:])

    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})

    caps = options.to_capabilities()
    caps["unhandledPromptBehavior"] = u"accept"

    driver = None
    if os.path.exists(chromedriver_path):
        print("Use user driver path:", chromedriver_path)
        #driver = uc.Chrome(service=chrome_service, options=options, suppress_welcome=False)
        is_local_chrome_browser_lower = False
        try:
            driver = uc.Chrome(executable_path=chromedriver_path, options=options, desired_capabilities=caps, suppress_welcome=False)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
                is_local_chrome_browser_lower = True
            pass

        if is_local_chrome_browser_lower:
            print("Use local user downloaded chromedriver to lunch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable)
    else:
        print("Oops! web driver not on path:",chromedriver_path )
        print('let uc automatically download chromedriver.')
        try:
            driver = uc.Chrome(options=options, desired_capabilities=caps, suppress_welcome=False)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
                is_local_chrome_browser_lower = True
            pass

    if driver is None:
        print("create web drive object fail!")
    else:
        download_dir_path="."
        params = {
            "behavior": "allow",
            "downloadPath": os.path.realpath(download_dir_path)
        }
        #print("assign setDownloadBehavior.")
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
    #print("driver capabilities", driver.capabilities)

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

    homepage = None
    browser = None
    language = "English"

    # read config.
    homepage = config_dict["homepage"]
    browser = config_dict["advanced"]["browser"]

    driver_type = config_dict["advanced"]["webdriver_type"]

    # output config:
    print("maxbot app version", CONST_APP_VERSION)
    print("python version", platform.python_version())
    print("platform", platform.platform())
    print("homepage", homepage)

    print("==[advanced]==")
    print(config_dict["advanced"])

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    print("platform.system().lower():", platform.system().lower())

    adblock_plus_enable = False

    if browser == "chrome":
        # method 6: Selenium Stealth
        if driver_type != CONST_WEBDRIVER_TYPE_UC:
            driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable)
        else:
            # method 5: uc
            # multiprocessing not work bug.
            if platform.system().lower()=="windows":
                if hasattr(sys, 'frozen'):
                    from multiprocessing import freeze_support
                    freeze_support()
            driver = load_chromdriver_uc(webdriver_path, adblock_plus_enable)

    if browser == "firefox":
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
            driver = webdriver.Firefox(service=webdriver_service)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if browser == "edge":
        # default os is linux/mac
        # download url: https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/
        chromedriver_path = os.path.join(webdriver_path,"msedgedriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"msedgedriver.exe")

        webdriver_service = Service(chromedriver_path)
        chrome_options, caps = get_chrome_options(webdriver_path, adblock_plus_enable, browser="edge")

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

    if browser == "safari":
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

def keyin_captcha_code(driver, answer):
    form_input = None
    try:
        form_input = driver.find_element(By.ID, 'txtVCode')
        if not form_input is None:
            form_input.clear()
            form_input.send_keys(answer)
            form_input.send_keys(Keys.ENTER)
    except Exception as exc:
        pass

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
    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    orc_answer = None
    if not ocr is None:
        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.Request_Captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'imgVI'
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

    if not orc_answer is None:
        orc_answer = orc_answer.strip()
        print("orc_answer:", orc_answer)
        if len(orc_answer)==5:
            is_form_sumbited = keyin_captcha_code(driver, answer = orc_answer)
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
    user_tel = config_dict["user_tel"]

    is_fill_text_by_app = False

    #print("check 初診.")
    # for "first time"
    # 初診/複診

    visit_time_html_id = 'rblRegFM_1'
    if visit_time == '初診':
        visit_time_html_id = 'rblRegFM_0'

    # default is 複診
    el_radio = None
    try:
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

    if ocr_captcha_enable:
        ocr_captcha_image_source = CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS
        previous_answer = None

        for redo_ocr in range(999):
            is_need_redo_ocr, previous_answer, is_form_sumbited =  auto_ocr(driver, ocr, previous_answer, Captcha_Browser, ocr_captcha_image_source)
            if is_form_sumbited:
                is_verifyCode_editing = False
                break
            if not is_need_redo_ocr:
                break
        

def tzuchi_reg(url, driver, config_dict, ocr, Captcha_Browser):
    #print("tzuchi_reg")
    ret = True

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
    reg_form_list = ['/RegNo.aspx', '/RegNo?']
    for each_page in reg_form_list:
        if each_page in url:
            tzuchi_RegNo(driver, config_dict, ocr, Captcha_Browser)
            break

    return ret

# purpose: check alert poped.
# PS: current version not enable...
def check_pop_alert(driver):
    is_alert_popup = False

    # https://stackoverflow.com/questions/57481723/is-there-a-change-in-the-handling-of-unhandled-alert-in-chromedriver-and-chrome
    default_close_alert_text = [
    u'「南區醫院總額醫療服務審查分級作業原則」'
    , u'無開放現場掛號及人工電話掛號'
    , u'健康檢查不需掛號，請逕洽服務台'
    ]

    if len(default_close_alert_text) > 0:
        try:
            alert = None
            if not driver is None:
                alert = driver.switch_to.alert
            if not alert is None:
                alert_text = str(alert.text)
                if not alert_text is None:
                    is_match_auto_close_text = False
                    for txt in default_close_alert_text:
                        if len(txt) > 0:
                            if txt in alert.text:
                                is_match_auto_close_text = True
                        else:
                            is_match_auto_close_text = True
                    #print("is_match_auto_close_text:", is_match_auto_close_text)
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
            pass
        except Exception as exc:
            logger.error('Exception2 for alert')
            logger.error(exc, exc_info=True)

    return is_alert_popup

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

    DISCONNECTED_MSG = ': target window already closed'

    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
            Captcha_Browser = NonBrowser()
    except Exception as exc:
        pass


    while True:
        time.sleep(0.1)

        is_alert_popup = False

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        is_alert_popup = check_pop_alert(driver)

        #MUST "do nothing: if alert popup.
        #print("is_alert_popup:", is_alert_popup)
        if is_alert_popup:
            continue

        url = ""
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
                        driver.quit()
                        sys.exit()
                        break
                except Exception as excGetDriverMessageFail:
                    #print("excGetDriverMessageFail:", excGetDriverMessageFail)
                    except_string = str(excGetDriverMessageFail)
                    if 'HTTP method not allowed' in except_string:
                        print('quit bot by close browser')
                        driver.quit()
                        sys.exit()
                        break

        except UnexpectedAlertPresentException as exc1:
            # PS: DON'T remove this line.
            is_verifyCode_editing = False
            print('UnexpectedAlertPresentException at this url:', url )
            #time.sleep(3.5)
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
            is_verifyCode_editing = False

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

            exit_bot_error_strings = [u'Max retries exceeded'
            , u'chrome not reachable'
            , u'unable to connect to renderer'
            , u'failed to check if window was closed'
            , u'Failed to establish a new connection'
            , u'Connection refused'
            , u'disconnected'
            , u'without establishing a connection'
            , u'web view not found'
            ]
            for each_error_string in exit_bot_error_strings:
                # for python2
                # say goodbye to python2
                '''
                try:
                    basestring
                    if isinstance(each_error_string, unicode):
                        each_error_string = str(each_error_string)
                except NameError:  # Python 3.x
                    basestring = str
                '''
                if isinstance(str_exc, str):
                    if each_error_string in str_exc:
                        print('quit bot by error:', each_error_string)
                        driver.quit()
                        sys.exit()
                        break

            # not is above case, print exception.
            print("Exception:", str_exc)
            pass

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
                ret = tzuchi_reg(url, driver, config_dict, ocr, Captcha_Browser)

if __name__ == "__main__":
    main()
