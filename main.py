from flask import Flask, request, abort
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

app = Flask(__name__)

#LINE Access Token
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
#LINE Channel Secret
YOUR_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

options = Options()
options.binary_location = '/app/.apt/usr/bin/google-chrome'
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=options)

url = "https://www.lib100.nexs-service.jp/etajima/webopac/selectsearch.do?searchkbn=2&histnum=1"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        driver.get(url)
#         driver.find_element_by_css_selector('input#title.iw20').send_keys("孤狼の血")
        driver.find_element_by_css_selector('input#title.iw20').send_keys(body)
        driver.find_element_by_css_selector("div.page_content_frame_control button").click()
        posts = driver.find_elements_by_css_selector("table#sheet tr td") #ページ内のタイトル複数
        name_list = []   #初期化
        for post in posts:
            try:
                name_list.append(post.text)
            except Exception as e:
                print(e)
        if not name_list:
            strname = ','.join(name_list)
            handler.handle(strname, signature)
        else:
            handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
