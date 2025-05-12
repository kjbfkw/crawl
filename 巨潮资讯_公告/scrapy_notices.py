from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import time
import os
import pandas as pd
import re
import shutil

class FileFetcher(object):
    def __init__(self, url, code, company_name, start_date, end_date):
        chrome_options = ChromeOptions()
        #反屏蔽
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension',False)

        #允许不安全的连接
        chrome_options.add_argument("--unsafely-treat-insecure-origin-as-secure=http://www.cninfo.com.cn")

        # 设置临时下载目录
        self.temp_download_path = os.path.join(os.getcwd(), 'temp_downloads')
        os.makedirs(self.temp_download_path, exist_ok=True)

        # 设置网络共享云盘路径
        network_drive = r"D:\\厦钨新能源云盘7.0 (2)\\信息管理\\16战略资讯系统\\0战略系统\\2研报智能库\\1企业深度"

        folder_name = f"{company_name}_{code}"

        # # 设置下载路径
        # self.download_path = os.path.join(os.getcwd(), folder_name, "公告")
        # base_html_path = os.path.join(os.getcwd(), folder_name, "HTML")
        # 设置下载路径
        self.final_download_path = os.path.join(network_drive, folder_name, "公告")
        base_html_path = os.path.join(network_drive, folder_name, "HTML")
        # 创建带日期的HTML文件夹
        current_date = time.strftime("%Y%m%d")
        self.html_path = os.path.join(base_html_path, current_date)
        # 创建文件夹
        os.makedirs(self.final_download_path, exist_ok=True)
        os.makedirs(self.html_path, exist_ok=True)

        # 确保网络共享目录存在
        try:
            os.makedirs(self.final_download_path, exist_ok=True)
            os.makedirs(self.html_path, exist_ok=True)
            print(f"成功创建网络共享目录: {self.final_download_path}")
            print(f"成功创建网络共享目录: {self.html_path}")
        except Exception as e:
            print(f"创建网络共享目录失败: {e}")
            raise Exception("无法访问网络共享，请检查网络连接和权限")

        # 配置Chrome下载设置
        chrome_options.add_experimental_option("prefs", {
            # 使用绝对路径并确保是Windows格式
            "download.default_directory": self.temp_download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,  # 禁用安全浏览
            "safebrowsing.disable_download_protection": True,
            # 允许覆盖已存在的文件
            "download.default_directory_infobar_shown": False,
            # 禁止PDF在浏览器中预览
            "plugins.always_open_pdf_externally": True,
            # 不使用系统PDF阅读器打开
            "download.open_pdf_in_system_reader": False,
            # 禁用弹出窗口 
            "profile.default_content_settings.popups": 0,
            # 不自动打开任何类型的文件
            "download.extensions_to_open": ""  ,

        })


        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
        # 隐式等待，直到网页加载完毕，最长等待时间为20s
        self.browser.implicitly_wait(20)

        #目标网页
        self.url = url
        # 目标公司代码
        self.code = code
        # 公告时间范围               
        self.start_date = start_date
        self.end_date = end_date
        self.downloaded_urls = None

    def search(self):
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
            current_url_replaced = current_url.replace("://", "_").replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")
            detail_html_file = os.path.join(self.html_path, f"{current_url_replaced}_{timestamp}.html")
            with open(detail_html_file, "w", encoding="utf-8") as f:
                f.write(detail_page_source)
            print(f"已保存公告详情HTML: {detail_html_file}")

            try:
                #点击“下载”
                self.browser.find_element(By.XPATH,'//*[@id="noticeDetail"]/div/div[1]/div[3]/div[1]/button').click()
                # 等待文件下载完成
                if self.wait_for_download():
                    print("文件下载完成")
                else:
                    print("文件下载超时")
            except Exception as e:
                print(f"下载失败: {e}")
            time.sleep(1)

            #关闭当前的公告详情窗口
            self.browser.close()
            #切换回主窗口，继续处理下一条公告
            self.browser.switch_to.window(self.browser.window_handles[0])
            print('当前页面已下载到第', node_num, '条')
            time.sleep(1)

    def clean_duplicate_files(self):
        """清理下载目录中的重复文件"""

        # 遍历下载目录中的所有文件
        for filename in os.listdir(self.temp_download_path):
            # 检查文件名是否包含(1)、(2)等模式
            if re.search(r'\(\d+\)\.(pdf|PDF)$', filename):
                try:
                    file_path = os.path.join(self.temp_download_path, filename)
                    os.remove(file_path)
                    print(f"已删除重复文件: {filename}")
                except Exception as e:
                    print(f"删除文件失败 {filename}: {e}")
            else:
                print(f"文件 {filename} 未找到重复模式")
    # def clean_duplicate_files(self):
    #
    #     # 存储已下载的公告链接
    #     self.downloaded_urls = getattr(self, 'downloaded_urls', set())
    #     print(f"已下载的公告链接: {self.downloaded_urls}")
    #     # 获取当前公告链接
    #     current_url = self.browser.current_url
    #
    #     # 如果是重复链接，删除对应的文件
    #     if current_url in self.downloaded_urls:
    #         # 获取最新下载的文件
    #         files = os.listdir(self.temp_download_path)
    #         if files:
    #             latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(self.temp_download_path, x)))
    #             try:
    #                 file_path = os.path.join(self.temp_download_path, latest_file)
    #                 os.remove(file_path)
    #                 print(f"已删除重复公告文件: {latest_file}")
    #             except Exception as e:
    #                 print(f"删除文件失败 {latest_file}: {e}")
    #     else:
    #     # 将新的公告链接添加到集合中
    #         self.downloaded_urls.add(current_url)
    #         print(f"新公告链接已记录: {current_url}")

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
            # 清理重复文件
            self.clean_duplicate_files()
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


# # 导入目标公司代码
# code_list = ['688778','002594']

# 导入公司代码
df = pd.read_csv('C:\\Users\\HC25939\\Desktop\\公司代码.csv', encoding='gbk',names=['company_name', 'code'],skiprows=1)

url = 'http://www.cninfo.com.cn/new/index'

for _, row in df.iterrows():
    code = str(row['code'])
    company_name = row['company_name']
    print(f'开始下载：{company_name}({code})')
    fetched_file = FileFetcher(url, code, company_name, '2024-03-01', '2024-3-26')
    #fetched_file = FileFetcher(url, code, company_name, '', '')
    fetched_file.search_and_download()