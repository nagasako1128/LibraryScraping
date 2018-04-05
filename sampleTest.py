from selenium import webdriver

browser = webdriver.PhantomJS() #DO NOT FORGET to set path
browser.get("https://www.google.co.jp/") #enables to access page
print(browser.title)