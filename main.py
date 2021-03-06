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
import os, json

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
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,1024')
driver = webdriver.Chrome(chrome_options=options)

url = "https://www.lib100.nexs-service.jp/etajima/webopac/selectsearch.do?searchkbn=2&histnum=1"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)
    print(body)
    print(type(body))

    # handle webhook body
    try:
        driver.get(url)
        print(driver)
        receive_json = json.loads(body)
        line_input_message = receive_json['events'][0]['message']['text']
#         driver.find_element_by_css_selector('input#title.iw20').send_keys("孤狼の血")
        driver.find_element_by_css_selector('input#title.iw20').send_keys(line_input_message)
        print(driver)
        driver.find_element_by_css_selector("div.page_content_frame_control button").click()
        print(driver)
        posts = driver.find_elements_by_css_selector("table#sheet tr td") #ページ内のタイトル複数
        print(posts)
        name_list = []   # 初期化
        for post in posts:
            try:
                name_list.append(post.text)
            except Exception as e:
                print(e)
        print("name_list:")
        print(name_list)
        if not name_list:
            # 送信データ作成
            json_post_data = {
                'events': [{
                    'type': 'message',
                    'replyToken': receive_json['events'][0]['replyToken'],
                    'source': {
                        'userId': receive_json['events'][0]['source']['userId'],
                        'type': receive_json['events'][0]['source']['type']
                    },
                    'timestamp': receive_json['events'][0]['timestamp'],
                    'message': {
                        'type': 'text',
                        'id': receive_json['events'][0]['message']['id'],
                        'text': 'ありません！'
                        # '図書館にそんな本ねーよ！アマゾンで買え！https://www.amazon.co.jp/s/ref=nb_sb_noss_1/358-0096124-2258834?__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&url=search-alias%3Daps&field-keywords=' + line_input_message
                    }
                }]
            }
            print(type(json_post_data))
            str_post_data = json.dumps(json_post_data)
            print(str_post_data)
            print(type(str_post_data))
            handler.handle(str_post_data, signature)
        else:
            strname = ','.join(name_list)
#             TODO
#             body['events'][0]['message']['text'] = strname
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
