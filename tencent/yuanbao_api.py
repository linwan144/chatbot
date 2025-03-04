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
from fastapi import FastAPI, HTTPException,File, UploadFile,Form
from pydantic import BaseModel #fastapi解析json请求
# 配置区
URL = "https://yuanbao.tencent.com/chat/"
# USER = '18777128615'
# PWD = 'a18777128615'
# USER_DATA_DIR = "C:\\Users\\YOUYU-PUBLIC\\AppData\Local\\Google\\Chrome\\User Data\\Profile 1" 
# INPUT_MODE = "cli"  # cli|file|auto
# MESSAGE_FILE = "messages.txt"  

class yuanbaoChatBot:
    def __init__(self):
        self.driver = self._init_driver()
        self.wait = WebDriverWait(self.driver, 120, poll_frequency=0.5)
        self.count = 0
        self.flag = 0

    def _init_driver(self):
        """浏览器初始化"""
        # options = webdriver.ChromeOptions()
        # options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        # options.add_argument("--disable-infobars")
        driver = webdriver.Chrome()
        # driver.execute_cdp_cmd("Network.enable", {})
        return driver
    def login(self,username):
        self.driver.get(URL)
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "agent-dialogue__tool__login"))).click()
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
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "t-input__inner"))).send_keys(username)
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
    def _dp_it_up(self):
        # 模型选择下拉
        time.sleep(random.uniform(0.5, 0.7))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "style__switch-model--arrow___LxKWQ"))).click()
        # 选择dp模型
        time.sleep(random.uniform(0.5, 0.7))
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//li[.//div[text()='DeepSeek']]"))).click()
        # 开启联网
        time.sleep(random.uniform(0.5, 0.7))
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='联网搜索']"))).click()
        print("deepseek模型已挂载,联网开启")

    def _get_response(self):
        """捕获最新AI回复"""
        try:
            start = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'agent-chat__conv--ai__toolbar--loading')))
            print("回答ing")
            end = self.wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, 'agent-chat__conv--ai__toolbar--loading')))
            print("回答结束,开始处理结果")
            search_list = self.driver.find_elements(By.CLASS_NAME, 'hyc-component-reasoner__search-list')[-1]
            thk = self.driver.find_elements(By.CLASS_NAME, 'hyc-component-reasoner__think--expand')[-1]
            ans = self.driver.find_elements(By.CLASS_NAME, 'hyc-component-reasoner__text')[-1]
            return {"think": search_list.text + '\n' + thk.text, "answer": ans.text}
        except Exception as e:
            return f"[超时] 未检测到AI响应\n{e}"

    def start_chat(self,chat_input):
        """主对话流程""" 
        # 等待核心组件加载
        # 挂载dp模型，联网启动
        if self.flag == 0:
            self._dp_it_up()
            self.flag = 1
        time.sleep(random.uniform(0.5,0.7))
        input_box = bot.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ql-editor")))
        time.sleep(random.uniform(0.5,0.7))
        res = self._send_message(input_box, chat_input)
        return res

    def _send_message(self, input_box, message):
        """单次消息发送"""
        try:
            # 输入问题
            input_box.send_keys(message)
            # 模拟按下回车键
            time.sleep(1)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "style__send-btn___ZsLmU"))).click()
            # 等待AI响应
            print('已发送请求')
            print(message)
            # time.sleep(10)
            print('等待AI响应')
            res = self._get_response()
            print("AI:", res)
            return res
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

class data(BaseModel):
    username : str
    verify_code : str
    chat_input : str

app = FastAPI()
@app.post("/init_chat/")
async def init_chat():
    global bot
    bot = yuanbaoChatBot()
    return {"message": "init_chat"}


@app.post("/login/")
async def login_post(data: data):
    global bot
    bot.login(data.username)
    return {"message": "验证码已发送，注意查收！！！"}

@app.post("/verify/")
async def verify_post(data: data):
    global bot
    bot.verify(data.verify_code)
    return {"message": "登录成功！！！"}

@app.post("/chat/")
async def chat_post(data: data):
    global bot
    res = bot.start_chat(data.chat_input)
    return {"message": res}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2222)

