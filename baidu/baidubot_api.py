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
from pydantic import BaseModel #fastapi解析json请求
from fastapi import FastAPI, HTTPException,File, UploadFile
import asyncio



# 配置区
URL = "https://chat.baidu.com/search"
# USER = ''
# PWD = ''
# USER_DATA_DIR = "" 
# INPUT_MODE = "cli"  # cli|file|auto
# MESSAGE_FILE = "messages.txt"  

class BaiduChatBot:
    def __init__(self):
        self.driver = self._init_driver()
        self.wait = WebDriverWait(self.driver, 60, poll_frequency=0.5)
        self.count = 0
        self.dp_flag = 0
        self.it_flag = 0

    def _init_driver(self):
        """浏览器初始化"""
        # options = webdriver.ChromeOptions()
        # options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        # options.add_argument("--disable-infobars")
        driver = webdriver.Chrome()
        # driver.execute_cdp_cmd("Network.enable", {})
        return driver
    def login(self,username,password):
        self.driver.get(URL)
        time.sleep(random.uniform(0.5,0.7))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "login-btn"))).click()
        time.sleep(random.uniform(0.5,0.7))
        self.wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_11__isAgree"))).click()
        print("开始登录操作...")
        time.sleep(random.uniform(0.5,0.7))
        self.wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_11__userName"))).send_keys(username)
        print("正在输入账号...")
        time.sleep(random.uniform(0.5,0.7))
        self.wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_11__password"))).send_keys(password)
        print("正在输入密码...")
        time.sleep(random.uniform(0.5,0.7))
        self.wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_11__submit"))).click()
        print("正在登录...")
        time.sleep(random.uniform(3,5))
        # time.sleep(random.uniform(0.5,0.7))
        self.wait.until(EC.presence_of_element_located((By.ID, "goToVerify"))).click()
        print('正在发送验证码...')
        # #程序打开网页后20秒内手动登陆账户
        # time.sleep(30)
        return '正在发送验证码...注意接收！！！'

        
    def verify_code(self,verify_code):
        
        try:
            # if verify_code == 0:
            #     print("重新发送验证码...")
            #     self.wait.until(EC.presence_of_element_located((By.ID, "authVerifyCode"))).click()
            # else:
            print("正在输入验证码...")
            self.wait.until(EC.presence_of_element_located((By.ID, "passAuthVcode"))).send_keys(verify_code)
            time.sleep(random.uniform(0.5,0.7))
            print("下一步...")
            self.wait.until(EC.presence_of_element_located((By.ID, "passAuthSubmitCode"))).click()
            print("登录成功！")
            time.sleep(random.uniform(0.5,0.7))
            return "登录成功！"
        except Exception as e:
            print("登录失败！\n{e}")
            return "登录失败！"
    def save_cookie(self,cookie_name):
        import json
        import os
        if not os.path.exists('cookies'):
            os.makedirs('cookies')
        with open(f'cookies/{cookie_name}.txt','w') as cookief:
            #将cookies保存为json格式
            cookief.write(json.dumps(self.driver.get_cookies()))
        print(f"cookie保存成功,名为{cookie_name}")
        return f"cookie保存成功,名为{cookie_name}"
       
    def login_with_cookie(self,cookie_name):
        self.driver.get(URL)
        try:
            WebDriverWait(self.driver, 60,0.5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cs-input-model"))
                )
            print("页面加载完成")
        except Exception as e:
            print(f'页面加载失败，错误信息：{e}')
        time.sleep(3)
        self.driver.delete_all_cookies()
        print('删除cookie成功')

        with open(f'cookies/{cookie_name}.txt','r') as cookief:
            #使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookieslist = json.load(cookief)

            # 方法1 将expiry类型变为int
            for cookie in cookieslist:
                #并不是所有cookie都含有expiry 所以要用dict的get方法来获取
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                self.driver.add_cookie(cookie)
            print(f"{cookie_name}加载成功")
        time.sleep(random.uniform(0.5,0.7))
        self.driver.refresh()
        print("刷新完毕，登录成功")
        return '刷新完毕，登录成功'

        

    # def _human_type(self, element, text):
    #     """拟人化输入"""
    #     for char in text:
    #         element.send_keys(char)
    #         time.sleep(random.uniform(0.05, 0.2))
    def _get_answer_element(self):
        try:
            for i in range(30):
                answer_element = self.driver.find_elements(By.CLASS_NAME, "marklang")
                print(f'第{self.count}个提问,{len(answer_element)} 个回答.')
                if len(answer_element) == self.count*2:
                    for i in range(30):
                        element = self.driver.find_elements(By.CLASS_NAME, "cs-question-closely-single-bub")
                        print(f'第{self.count}个提问,{len(element)}个拓展框')
                        if len(element) == self.count*3:
                            answer_element = self.driver.find_elements(By.CLASS_NAME, "marklang")
                            return answer_element
                        else:
                            time.sleep(3)
                else:
                    time.sleep(3)
        except Exception as e:
            return [f"[超时] 未检测到AI响应\n{e}"]
    def _refresh(self):
        self.count = 0
        self.driver.refresh()
    def _get_response(self):
        """捕获最新AI回复"""
        try:
            WebDriverWait(self.driver, 60,0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cs-question-closely-single-bub"))
                )

            # 取后两条
            res = ''
            answer_element = self._get_answer_element()
            final_answer = answer_element[-2:]
            think_html = final_answer[0].get_attribute('outerHTML')
            think_md = md(think_html)
            answer_html = final_answer[1].get_attribute('outerHTML')
            answer_md = md(answer_html)
            return {"think": think_md, "answer": answer_md}
        except Exception as e:
            return {"think": f"[超时] 未检测到AI响应\n{e}", "answer": f"[超时] 未检测到AI响应\n{e}"}
    def _dp_upload(self):
        try:
            active = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
            print(f"{len(active)},deepseek模型已挂载")
        except:
            print("deepseek模型未启用，现在启用...")
            submit_button = self.driver.find_element(By.CLASS_NAME, "cs-input-model")
            submit_button.click()
            active = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
            print(f"{len(active)},deepseek模型已挂载")
        self.dp_flag = 1
    def _internet_search(self):
        if self.dp_flag == 1:
            active = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
            if len(active) == 1:
                print("未启用联网搜索，现在启用...")
                internet_search = self.driver.find_element(By.CLASS_NAME,'internet-search-icon')
                internet_search.click()
                active = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
                print(f"{len(active)},开启联网功能")
        else:
            print("未启用dpR1，现在启用...")
            submit_button = self.driver.find_element(By.CLASS_NAME, "cs-input-model")
            submit_button.click()
            active = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
            print(f"{len(active)},deepseek模型已挂载")
            if len(active) == 3:
                print(f'{len(active)},联网搜索已启用')
            else:
                print(f'{len(active)},联网搜索未启用')
                internet_search = self.driver.find_element(By.CLASS_NAME,'internet-search-icon')
                internet_search.click()
                active = self.driver.find_elements(By.CLASS_NAME, "cs-input-model-button-active")
                print(f"{len(active)},联网搜索已启用")
        self.it_flag = 1
    def start_chat(self,input,deepseek="1",internet="1"):
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
        if self.dp_flag == 0 and deepseek=='1':
            self._dp_upload()
            # 定位到输入框
            time.sleep(random.uniform(0.5,0.7))
            if self.it_flag == 0 and internet =="1" :
                self._internet_search()
        input_box = self.driver.find_element(By.ID, "chat-input-box")
        if input:
            message = input
            if message.lower() == "exit":
                self.driver.quit()
                return "对话结束已退出"
            self.count += 1
            res = self._send_message(input_box, message)
            return res


    def _send_message(self, input_box, message):
        """单次消息发送"""
        try:
            # 输入问题
            input_box.send_keys(message)
            # 模拟按下回车键
            input_box.send_keys(Keys.RETURN)
            # self.driver.find_element(By.CLASS_NAME,"cos-icon cos-icon-arrow-up-circle-fill send-icon ").click()
            # 等待AI响应
            print('已发送请求\n')
            print(message)
            # time.sleep(10)
            print('等待AI响应\n')
            res = self._get_response()
            print("AI:", res)
            return res
        except Exception as e:
            print(f"发送失败: {str(e)}")
            return {"error": f"发送失败: {str(e)}"}
    def _quit(self):
        self.driver.quit()
        print("浏览器已退出")
        return "浏览器已退出"
# 定义 Pydantic 模型
class login(BaseModel):
    username: str
    password: str

class verify(BaseModel):
    verify_code: str       

class chat(BaseModel):
    chat_input: str  
    deepseek: str      
    internet: str

class cookie(BaseModel):
    cookie_name: str

app = FastAPI()
@app.post("/init_chat/")
async def init_chat():
    # 创建一个实例
    global bot 
    bot = BaiduChatBot()
    return {"message": "初始化成功"}
@app.post("/login/")
async def login_post(login_data: login):
    global bot 
    # 获取请求参数
    username = login_data.username
    password = login_data.password
    res = bot.login(username,password)
    return {"message": res}
@app.post("/verify/")
async def verify_post(verify_data: verify):
    global bot 
    verify_code = verify_data.verify_code
    res = bot.verify_code(verify_code)
    return {"message": res}
@app.post("/save_cookies/")
async def save_cookie_post(save_cookie_data: cookie):
    global bot
    cookie_name = save_cookie_data.cookie_name
    res = bot.save_cookie(cookie_name)
    return {"message": res}

@app.post("/login_with_cookie/")
async def login_with_cookie_post(login_with_cookie_data: cookie):
    global bot
    cookie_name = login_with_cookie_data.cookie_name
    res = bot.login_with_cookie(cookie_name)
    return {"message": res}
@app.post("/chat/")
async def chat_post(chat_data: chat):
    global bot
    input = chat_data.chat_input
    ds = chat_data.deepseek
    internet = chat_data.internet
    res = bot.start_chat(input,ds,internet)
    return {"message": res}
@app.post("/quit/")
async def quit_post():
    global bot
    res = bot._quit()
    return {"message": res}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1111)
