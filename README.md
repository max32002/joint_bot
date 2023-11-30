# Max掛號機器人
MaxRegBot是一個免費、開放原始碼的掛號機器人。祝您掛號成功。

MaxRegBot help you quickly make your registration online

# Download (應用程式下載)
https://github.com/max32002/joint_bot/releases

# Demo (示範影片)

* 2023-02-19：https://youtu.be/RwXAOIhXA9I (支援驗證碼自動輸入)
* 2022-02-17：https://youtu.be/bpuI2m-L7X0
* 2022-05-06：https://youtu.be/QRLAFMY4yJY

# How to use (如何使用)
https://max-everyday.com/2018/08/max-auto-reg-bot/

在「進階設定」中，如果你的 webdriver 類別是使用 selenium, 那你除了主程式，請另外再下載 ChromeDriver 元件。如果你沒有修改預設值的話，程式會自動下載最新版的 webdriver 元件，你只需更新chrome 瀏覽器到最新版即可。

# How to execute source code (透過原始碼的執行方法)
1: download chromedrive to "webdriver" folder:
http://chromedriver.chromium.org/downloads

change the chromedrive in chrome_tixcraft.py, source code:
<code>chromedriver_path =Root_Dir+ "webdriver/chromedriver"</code>
the default path is the script path + "webdriver/chromedriver", My suggestion is to create a new directory, then move the chromedrive under new folder.

2: <code>python3 -m pip install selenium</code>

3: <code>python3 settings.py</code>

PS:
* 原始碼只可以在 python3 下執行。
* 請先確定你的python 執行環境下已安裝 selenium 相關的套件，請參考 pip-reg.txt 檔案內容。
* 請到ChromeDriver網站 (https://chromedriver.chromium.org/) 下載與您目前相同版本的 ChromeDriver 的執行檔，放在搶票程式的webdriver目錄下(Mac電腦請放到 MaxBot.app 套件裡的 /Contents/Resources/webdriver/)，在執行搶票程式前，第一次執行搶票主程式前，前請先手動點 ChromeDriver 的執行檔。
* 最後透過 python3 執行 settings.py 就可以有 GUI 的設定界面。)
* 如果你是使用 macOS 並且執行環境沒有 python3，請 python 官方網站(https://www.python.org/downloads/)來安裝 python3, 如果在 macOS 裡會使用終端機(Terminal)，建議使用 https://brew.sh/ 安裝 python3.
* 如果你是使用 Firefox, ChromeDriver 的元件是叫 geckodriver，下載點在：https://github.com/mozilla/geckodriver/releases ，與 ChromeDriver 的處理方式是一樣，如果是 mac 電腦，要在元件按右鍵開啟，做一次授權的動作，mac 有2個版本，-macos.tar.gz 與 -macos-aarch64.tar.gz ，如果是 intel CPU 的版本，請服用前面沒有 aarch64 的版本。

# Introduce the implement (實作方法)
https://stackoverflow.max-everyday.com/2018/03/selenium-chrome-webdriver/

# Execute suggestion (掛號建議)
please run this source code with high performance hardware computer and high speed + stable network.

掛號的「限量」是殘酷的，建議不要用破舊的電腦或連線不穩的手機網路來掛號，因為只要比別人慢個 0.1 秒，名額可能就沒了。為了要搶到限量的名額真心建議去網咖或找一個網路連線穩定且快的地方並使用硬體不差的電腦來搶票。


# File description (檔案說明)

* MaxBot_xxxxxx.zip ：Apple Mac 的App。
* joint_xxxxxx.zip ： Windows 版執行檔。


# Introduce the implement (實作方法)

https://stackoverflow.max-everyday.com/2018/03/selenium-chrome-webdriver/

# TODO about cpatcha (關於驗證碼)

目前自動輸入驗證碼用的元件是:

https://github.com/sml2h3/ddddocr

附註：
* macOS 新的電腦 arm 系列, 暫時沒有提供自動輸入驗證碼功能, 使用上的限制和 ddddocr 相同. 
* macOS 舊款intel CPU 的電腦裡的 python 版本要降到低於等於 3.10 版。

想自動輸入驗證碼，可以參考看看：實作基於CNN的台鐵訂票驗證碼辨識以及透過模仿及資料增強的訓練集產生器 (Simple captcha solver based on CNN and a training set generator by imitating the style of captcha and data augmentation)

https://github.com/JasonLiTW/simple-railway-captcha-solver

# Donate (贊助Max)

如果你覺得這篇文章或MaxRegBot寫的很好，想打賞Max，贊助方式如下： https://max-everyday.com/about/#donate
