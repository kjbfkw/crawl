from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import pandas as pd
import re
import shutil
import mysql.connector
import hashlib
from datetime import datetime
from db_config import DatabaseManager



class FileFetcher(object):
    def __init__(url, start_date, end_date):
        chrome_options = ChromeOptions()
        #反屏蔽
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension',False)

        #允许不安全的连接
        chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=http://www.cninfo.com.cn")

        # 设置临时下载目录
        temp_download_path = os.path.join(os.getcwd(), 'temp_downloads')
        os.makedirs(temp_download_path, exist_ok=True)

        # 设置网络共享云盘路径
        network_drive = r"D:\\厦钨新能源云盘7.0 (2)\\信息管理\\16战略资讯系统\\0战略系统\\3报价系统\\1产品价格"

        # 设置下载路径
        final_download_path = os.path.join(network_drive, "价格")
        base_html_path = os.path.join(network_drive, "HTML")
        # 创建带日期的HTML文件夹
        current_date = time.strftime("%Y%m%d")
        html_path = os.path.join(base_html_path, current_date)
        # 创建文件夹
        os.makedirs(final_download_path, exist_ok=True)
        os.makedirs(html_path, exist_ok=True)

        # 确保网络共享目录存在
        try:
            os.makedirs(final_download_path, exist_ok=True)
            os.makedirs(html_path, exist_ok=True)
            print(f"成功创建网络共享目录: {final_download_path}")
            print(f"成功创建网络共享目录: {html_path}")
        except Exception as e:
            print(f"创建网络共享目录失败: {e}")
            raise Exception("无法访问网络共享，请检查网络连接和权限")

        # 配置Chrome下载设置
        chrome_options.add_experimental_option("prefs", {
            # 使用绝对路径并确保是Windows格式
            "download.default_directory": temp_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            # 允许不安全证书
            "acceptInsecureCerts": True

        })


        browser = webdriver.Chrome(options=chrome_options)
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
        # 隐式等待，直到网页加载完毕，最长等待时间为20s
        browser.implicitly_wait(20)


    def calculate_content_hash(self, content):
        """计算内容的SHA256哈希值"""
        return hashlib.sha256(content.encode()).hexdigest()

    def check_url_status(self, url):
        """检查URL的爬取状态"""
        query = """
        SELECT id, status, retries FROM `cninfo_url`.`crawling_queue`
        WHERE url = %s AND del_flag = '0'
        """
        self.cursor.execute(query, (url,))
        result = self.cursor.fetchone()

        if not result:
            insert_query = """
            INSERT INTO `cninfo_url`.`crawling_queue` (url, status, last_crawled, create_by) 
            VALUES (%s, 'pending', NOW(), %s)
            """
            self.cursor.execute(insert_query, (url, self.code))
            self.db.commit()
            return True

        if result['status'] == 'completed':
            return False

        if result['retries'] >= 10:
            return False

        return True

    def update_crawling_status(self, url, status, content_hash = None):
        """更新URL的爬取状态"""
        update_queue = """
        UPDATE `cninfo_url`.`crawling_queue` 
        SET status = %s, last_crawled = NOW(), update_time = NOW(), update_by = %s
        WHERE url = %s
        """
        self.cursor.execute(update_queue, (status, self.code, url))

        if status == 'completed' and content_hash:
            insert_content = """
            INSERT INTO `cninfo_url`.`crawled_pages` (url, content_hash, last_crawled, create_by)
            VALUES (%s, %s, NOW(), %s)
            """
            self.cursor.execute(insert_content, (url, content_hash, self.code))

        self.db.commit()


    def search(browser, start_date, end_date):
        try:
            # 输入公司代码
            element_code = self.browser.find_element(By.XPATH,'//*[@id="searchTab"]/div/div[2]/div/div[1]/div/div/input')
            ActionChains(self.browser).double_click(element_code).perform()
            element_code.send_keys(self.code)
            #点击空白处
            ActionChains(self.browser).move_by_offset(0, 0).click().perform()
            time.sleep(1)
        except Exception as e:
            print(f"无法找到搜索输入框: {e}")

        try:
            #输入开始日期
            element_start_date = self.browser.find_element(By.XPATH,'//*[@id="searchTab"]/div/div[4]/div/input[1]')
            ActionChains(self.browser).double_click(element_start_date).perform()
            element_start_date.clear()
            element_start_date.send_keys(self.start_date)
            #点击空白处
            ActionChains(self.browser).move_by_offset(0, 0).click().perform()
            time.sleep(1)
        except Exception as e:
            print(f"无法找到开始日期输入框: {e}")

        try:
            #输入结束日期
            element_end_date = self.browser.find_element(By.XPATH,'//*[@id="searchTab"]/div/div[4]/div/input[2]')
            ActionChains(self.browser).double_click(element_end_date).perform()
            element_end_date.clear()
            element_end_date.send_keys(self.end_date)
            #点击空白处
            ActionChains(self.browser).move_by_offset(0, 0).click().perform()
            time.sleep(1)
        except Exception as e:
            print(f"无法找到结束日期输入框: {e}")

        # try:
        #     # 点击"今日"按钮选择最新日期
        #     element_time = self.browser.find_element(By.XPATH,'//*[@id="searchTab"]/div/div[4]/div/i[1]')
        #     element_time.click()
        #     time.sleep(1)
        #     today_button = self.browser.find_element(By.CSS_SELECTOR, 'body > div.el-picker-panel.el-date-range-picker.el-popper.has-sidebar > div.el-picker-panel__body-wrapper > div.el-picker-panel__sidebar > button:nth-child(2)')
        #     today_button.click()
        #     time.sleep(1)
        # except Exception as e:
        #     print(f"无法找到'今日'按钮: {e}")

        # 提交“查询”
        self.browser.find_element(By.XPATH,'//*[@id="searchTab"]/div/div[5]/button').click()
        print('查询完成')

    def wait_for_download(self, timeout=30):
        """等待文件下载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # 检查下载目录中的文件
            files = os.listdir(self.temp_download_path)
            # 检查是否有正在下载的临时文件（.crdownload 或 .tmp）
            downloading = any(f.endswith(('.crdownload', '.tmp')) for f in files)
            if files and not downloading:
                # 如果有文件且没有临时文件，说明下载完成
                return True
            time.sleep(0.5)
        return False

    def download_pdf(self):

        # 找到当前页面所有可点击的公告链接
        sublink_list = self.browser.find_elements(By.XPATH,'//span[@class="ahover ell"]')
        #计算当前页面的公告数
        max_node_num = len(sublink_list)
        print('本页含有文件数: ', max_node_num)
        for node_num in range(1, max_node_num + 1):
            #制造每条公告的XPATH
            subpath = '//tbody/tr[{}]/td[3]/div/span/a'.format(node_num)
            #找到公告的链接
            sub_link = self.browser.find_element(By.XPATH, subpath)
            self.browser.execute_script("arguments[0].click();", sub_link)
            #切换到新打开的窗口（公告详情页）
            self.browser.switch_to.window(self.browser.window_handles[-1])

            time.sleep(2)

            # 保存公告详情页面HTML
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            detail_page_source = self.browser.page_source
            # 从当前URL中提取域名
            current_url = self.browser.current_url
            print('当前URL:', current_url)

            # 检查URL是否需要爬取
            if not self.check_url_status(current_url):
                print(f"跳过URL: {current_url}")
                self.browser.close()
                self.browser.switch_to.window(self.browser.window_handles[0])
                continue
            try:
                # 更新状态为处理中
                self.update_crawling_status(current_url, 'processing')
                # 保存HTML和下载PDF的代码
                detail_page_source = self.browser.page_source
                content_hash = self.calculate_content_hash(detail_page_source)
                current_url_replaced = current_url.replace("://", "_").replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")
                detail_html_file = os.path.join(self.html_path, f"{current_url_replaced}_{timestamp}.html")
                with open(detail_html_file, "w", encoding="utf-8") as f:
                    f.write(detail_page_source)
                print(f"已保存公告详情HTML: {detail_html_file}")

                #点击“下载”
                self.browser.find_element(By.XPATH,'//*[@id="noticeDetail"]/div/div[1]/div[3]/div[1]/button').click()
                # 等待文件下载完成
                if self.wait_for_download():
                    print("文件下载完成")
                    self.update_crawling_status(current_url, 'completed', content_hash)
                else:
                    print("文件下载超时")
                    self.update_crawling_status(current_url, 'pending')
            except Exception as e:
                print(f"下载失败: {e}")
                self.update_crawling_status(current_url, 'pending')
            time.sleep(1)

            #关闭当前的公告详情窗口
            self.browser.close()
            #切换回主窗口，继续处理下一条公告
            self.browser.switch_to.window(self.browser.window_handles[0])
            print('当前页面已下载到第', node_num, '条')
            time.sleep(1)


    def move_files_to_network_drive(self):
        """将临时目录中的文件移动到网络驱动器"""
        try:
            # 确保目标目录存在
            os.makedirs(self.final_download_path, exist_ok=True)

            # 获取临时目录中的所有文件
            files = os.listdir(self.temp_download_path)

            for file in files:
                src_path = os.path.join(self.temp_download_path, file)
                dst_path = os.path.join(self.final_download_path, file)

                try:
                    # 使用 shutil.move 替代 os.rename
                    shutil.move(src_path, dst_path)
                    print(f"已移动文件: {file} 到 {self.final_download_path}")
                except Exception as e:
                    print(f"移动文件失败 {file}: {e}")

            print("文件移动完成")

        except Exception as e:
            print(f"移动文件到网络驱动器时出错: {e}")

    def search_and_download(self):
        self.browser.get(self.url)

        # 等待页面加载完成
        time.sleep(3)  # 基础等待时间
        try:
            # 等待搜索框出现，确认页面加载完成
            self.browser.find_element(By.XPATH,'//*[@id="searchTab"]/div/div[2]/div/div[1]/div/div/input')
        except:
            print("等待页面加载...")
            # 如果没找到元素，额外等待
            time.sleep(5)

        # 获取当前时间作为文件名的一部分
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        init_page_source = self.browser.page_source
        print('当前URL：', self.url)
        init_url = self.url.replace("://", "_").replace("/", "_")
        init_html_file = os.path.join(self.html_path, f"{init_url}_{timestamp}.html")
        with open(init_html_file, "w", encoding="utf-8") as f:
            f.write(init_page_source)
        print(f"已保存HTML文件: {init_html_file}")
        # 输入搜索条件
        self.search()
        time.sleep(0.5)

        page = 1
        while True:
            # 从当前页面URL获取域名
            current_url = self.browser.current_url
            print('当前URL：', current_url)
            # 保存搜索结果页面HTML
            search_page_source = self.browser.page_source
            current_url_replaced = current_url.replace("://", "_").replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")
            search_html_file = os.path.join(self.html_path, f"{current_url_replaced}_search_{timestamp}.html")
            with open(search_html_file, "w", encoding="utf-8") as f:
                f.write(search_page_source)
            print(f"已保存第{page}页搜索结果HTML: {search_html_file}")
            # 翻页循环
            print('开始下载第', page, '页')
            self.download_pdf()  # 下载当前页面所有pdf文件
            # 在每一页下载完成后，移动文件到网络驱动器
            self.move_files_to_network_drive()

            try:
                a = self.browser.find_element(By.XPATH,'//button[@class="btn-next" and @disabled="disabled"]')
                print('已下载到最后一页')
                time.sleep(3)
                break
            except:
                next_page_button = self.browser.find_element(By.XPATH,'//button[@class="btn-next"]')
                next_page_button.click()  # 翻页
                page += 1
                time.sleep(1)

            try:
                os.rmdir(self.temp_download_path)
                print("临时下载目录已删除")
            except Exception as e:
                print(f"删除临时目录失败: {e}")
        self.browser.close()
        # input("按Enter键关闭浏览器...")
        time.sleep(3)



# 导入公司代码
df = pd.read_csv('C:\\Users\\HC25939\\Desktop\\公司代码.csv', encoding='gbk',names=['company_name', 'code'],skiprows=1)

url = 'https://price.smm.cn/'


fetched_file = FileFetcher(url, '2024-03-01', '2024-3-26')
fetched_file.search_and_download()