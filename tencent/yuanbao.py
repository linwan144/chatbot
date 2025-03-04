# -*- coding: utf-8 -*-
import sys
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json
from selenium.webdriver.common.keys import Keys
from markdownify import markdownify as md
from bs4 import BeautifulSoup
# 配置区
URL = "https://yuanbao.tencent.com/chat/"
USER = '18777128615'
PWD = 'a18777128615'
USER_DATA_DIR = "C:\\Users\\YOUYU-PUBLIC\\AppData\Local\\Google\\Chrome\\User Data\\Profile 1" 
INPUT_MODE = "cli"  # cli|file|auto
MESSAGE_FILE = "messages.txt"  

class yuanbaoChatBot:
    def __init__(self):
        self.driver = self._init_driver()
        self.wait = WebDriverWait(self.driver, 60, poll_frequency=0.5)
        self.count = 0

    def _init_driver(self):
        """浏览器初始化"""
        # options = webdriver.ChromeOptions()
        # options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        # options.add_argument("--disable-infobars")
        driver = webdriver.Chrome()
        # driver.execute_cdp_cmd("Network.enable", {})
        return driver
    def login(self):
        self.driver.get(URL)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "agent-dialogue__tool"))).click()
        print("开始登录操作...")
        time.sleep(random.uniform(0.5, 0.7))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "t-radio-button")))
        switch_btn = self.driver.find_elements(By.CLASS_NAME, "t-radio-button")
        print('选择手机号登录...')
        switch_btn[1].click()
        time.sleep(random.uniform(0.5, 0.7))
        # 勾选协议框
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "t-checkbox__input"))).click()
        print("正在输入账号...")
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "t-input__inner"))).send_keys(USER)
        time.sleep(random.uniform(0.5, 0.7))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hyc-phone-login__send-code"))).click()
        print("正在获取验证码...")

    def verify(self,verify_code):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "t-input__inner")))
        time.sleep(random.uniform(0.5, 0.7))
        self.driver.find_elements(By.CLASS_NAME, "t-input__inner")[1].send_keys(verify_code)
        time.sleep(random.uniform(0.5, 0.7))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hyc-phone-login__btn"))).click()
        print("登录成功")

    def login_with_cookie(self):
        self.driver.get(URL)
        
        self.driver.delete_all_cookies()

        with open('cookies.txt','r') as cookief:
            #使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookieslist = json.load(cookief)

            # 方法1 将expiry类型变为int
            for cookie in cookieslist:
                #并不是所有cookie都含有expiry 所以要用dict的get方法来获取
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                self.driver.add_cookie(cookie)
        time.sleep(1)
        self.driver.refresh()
        print("cookies加载成功")

    # def _human_type(self, element, text):
    #     """拟人化输入"""
    #     for char in text:
    #         element.send_keys(char)
    #         time.sleep(random.uniform(0.05, 0.2))
    def _get_answer_element(self):
        try:
                # 等候六十秒，等下次回答完成
            for i in range(10):
                answer_element = self.driver.find_elements(By.CLASS_NAME, "marklang")
                print(len(answer_element))
                if len(answer_element) == self.count*2:
                    for i in range(10):
                        element = self.driver.find_elements(By.CLASS_NAME, "cs-question-closely-single-bub")
                        if len(element) == self.count*3:
                            answer_element = self.driver.find_elements(By.CLASS_NAME, "marklang")
                            return answer_element
                        else:
                            time.sleep(6)
                else:
                    time.sleep(6)
            return  answer_element
        except Exception as e:
            return f"[超时] 未检测到AI响应\n{e}"

    def _get_response(self):
        """捕获最新AI回复"""
        try:
            WebDriverWait(self.driver, 60,0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cs-question-closely-single-bub"))
                )

            # 取后两条
            res = ''
            answer_element = self._get_answer_element()
            for ans in answer_element[-2:]:
                html_content = ans.get_attribute('outerHTML')
                # 将 HTML 转换为 Markdown 格式
                markdown_content = md(html_content)
                # print(markdown_content)
                res += markdown_content
            return res
        except Exception as e:
            return f"[超时] 未检测到AI响应\n{e}"

    def start_chat(self):
        """主对话流程""" 
        # 等待核心组件加载
        try:
            WebDriverWait(self.driver, 60,0.5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cs-input-model"))
                )
            print("页面加载完成")
        except Exception as e:
            print(f'页面加载失败，错误信息：{e}')
        time.sleep(random.uniform(0.5,0.7))
        submit_button = self.driver.find_element(By.CLASS_NAME, "cs-input-model")
        submit_button.click()
        print("deepseek模型已挂载")
        # 定位到输入框
        time.sleep(random.uniform(0.5,0.7))
        internet_search = self.driver.find_element(By.CLASS_NAME,'internet-search-icon')
        internet_search.click()
        print("开启联网功能")
        input_box = self.driver.find_element(By.ID, "chat-input-box")
        # 输入模式选择
        if INPUT_MODE == "cli":
            while True:
                self.count+=1
                print("请输入问题：\n")
                message = input("")
                if message.lower() == "exit":
                    break
                self._send_message(input_box, message)
        elif INPUT_MODE == "file":
            with open(MESSAGE_FILE, "r") as f:
                for line in f.readlines():
                    self._send_message(input_box, line.strip())

    def _send_message(self, input_box, message):
        """单次消息发送"""
        try:
            # 输入问题
            input_box.send_keys(message)
            # 模拟按下回车键
            input_box.send_keys(Keys.RETURN)
            # 等待AI响应
            print('已发送请求')
            # time.sleep(10)
            print('等待AI响应')
            print("AI:", self._get_response())
            # self.get_response()
            # # 随机滚动查看历史
            # last_height = self.driver.execute_script("return document.body.scrollHeight")
            # self.driver.execute_script(f"window.scrollBy(0, {last_height});")
            # # 等待新内容加载
            # time.sleep(random.uniform(1, 1.2))
            # # 紧接着上划
            # self.driver.execute_script(f"window.scrollBy(0, -200);")
            # time.sleep(random.uniform(1, 1.2))  # 等待页面加载
        except Exception as e:
            print(f"发送失败: {str(e)}")
            
    def check_R1_and_internet(self):
        import requests
        self.driver.get(URL)
        submit_button = self.driver.find_element(By.CLASS_NAME, "cs-input-model")
        
        a = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
        print(len(a))
        submit_button.click()
        a = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
        print(len(a))

        a = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
        print(len(a))

        a = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
        print(len(a))

        a = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
        print(len(a))
        # try:
        #     self.driver.find_element(By.CLASS_NAME, 'cs-input-model-button-active')
        #     print ('yes')
        # except Exception as e:
        #     print(f"发送失败: {str(e)}")
        #     submit_button.click()
        # try:
        #     self.driver.find_element(By.CLASS_NAME, 'cs-input-model-button-active')
        #     print ('yes')
        # except Exception as e:
        #     print(f"发送失败: {str(e)}")
        #     submit_button.click() 
if __name__ == "__main__":
    bot = yuanbaoChatBot()
    bot.login()
    verify_code = input("请输入验证码：")
    bot.verify(verify_code)
    # bot.login_with_cookie()
    # bot.start_chat()
    # bot.check_R1_and_internet()
    # finally:
    #     bot.driver.quit()
