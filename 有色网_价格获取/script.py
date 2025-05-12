import random
from urllib.parse import urlparse

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
import shutil
from db_config import DatabaseManager
from datetime import datetime

def create_download_path():
    # 创建临时下载目录
    init_download_path = os.path.join(os.getcwd(), "temp_download")
    os.makedirs(init_download_path, exist_ok=True)

    # 设置网络共享云盘路径
    network_drive = r"D:\\厦钨新能源云盘7.0 (2)\\信息管理\\16战略资讯系统\\0战略系统\\3报价系统\\1产品价格"

    # 设置下载路径
    full_download_path = os.path.join(network_drive, "价格")
    base_html_path = os.path.join(network_drive, "HTML")
    # 创建带日期的HTML文件夹
    current_date = time.strftime("%Y%m%d")
    init_html_path = os.path.join(base_html_path, current_date)
    # 创建文件夹
    os.makedirs(full_download_path, exist_ok=True)
    os.makedirs(init_html_path, exist_ok=True)

    # 确保网络共享目录存在
    try:
        os.makedirs(full_download_path, exist_ok=True)
        os.makedirs(init_html_path, exist_ok=True)
        print(f"成功创建网络共享目录: {full_download_path}")
        print(f"成功创建网络共享目录: {init_html_path}")
    except Exception as e:
        print(f"创建网络共享目录失败: {e}")
        raise Exception("无法访问网络共享，请检查网络连接和权限")
    result = {
        "temp_download_path": init_download_path,
        "final_download_path": full_download_path,
        "html_path": init_html_path,
    }
    return result

def wait_for_download(timeout=60):
    """等待下载完成"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # 检查是否存在临时下载文件
        temp_files = [f for f in os.listdir(temp_download_path) if f.endswith('.download')]
        if not temp_files:
            excel_files = [f for f in os.listdir(temp_download_path) if f.endswith('.xlsx')]
            if excel_files:
                return os.path.join(temp_download_path, excel_files[0])
        time.sleep(1)
    raise TimeoutError("下载超时")


def move_files_to_network_drive():
    """将临时目录中的文件移动到网络驱动器"""
    try:
        # 确保目标目录存在
        os.makedirs(final_download_path, exist_ok=True)

        # 获取临时目录中的所有文件
        files = os.listdir(temp_download_path)

        for file in files:
            src_path = os.path.join(temp_download_path, file)
            dst_path = os.path.join(final_download_path, file)

            try:
                # 使用 shutil.move 替代 os.rename
                shutil.move(src_path, dst_path)
                print(f"已移动文件: {file} 到 {final_download_path}")
            except Exception as e:
                print(f"移动文件失败 {file}: {e}")

        print("文件移动完成")

    except Exception as e:
        print(f"移动文件到网络驱动器时出错: {e}")


def setup_chrome_options(temp_download_path):
    """配置Chrome选项"""
    chrome_options = Options()

    # 下载设置
    prefs = {
        "download.default_directory": temp_download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        # 允许不安全证书
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # 添加反爬虫参数
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    return chrome_options



def search(browser, start_date, end_date):
    start_time = time.time()
    click_count = 0
    max_time = 30

    while True:
        try:
            if time.time() - start_time > max_time:
                print(f"已运行{max_time}秒，停止加载")
                break

            try:
                """
                使用JS方法实现按钮点击
                """
                browser.execute_script("document.querySelector('a.password-login').click();")
                click_count += 1
                print(f"已经执行JS方法实现按钮点击{click_count}次")

            except:
                """
                使用selenium方法实现按钮点击
                """
                # 查找‘加载更多’按钮
                load_more_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".password-login")))
                print("已经执行selenium方法实现按钮查找")
                # load_more_button.click()
                ActionChains(browser).move_to_element(load_more_button).click().perform()
                click_count += 1
                print(f"已经执行selenium方法实现按钮点击{click_count}次")

            time.sleep(random.randint(3, 5))

            username_input = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "userName")))
            username_input.send_keys("CXTCXNY")
            time.sleep(1)
            password_input = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "password")))
            password_input.send_keys("scb3351622")
            time.sleep(1)
            login_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "user_account_password_login_button")))
            login_button.click()
            time.sleep(3)

            browser.find_element(By.XPATH,'//*[@id="__next"]/div[2]/div[3]/div/div[1]/div[1]/div[2]/span[2]').click()
            print(f"成功点击清空")
            # 点击锂电分类
            browser.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[3]/div/div[2]/div/div[1]/div[2]/span[7]').click()
            print(f"成功点击锂电分类")
            time.sleep(random.uniform(1, 2))

            # 等待并点击锂化合物
            browser.find_element(By.CSS_SELECTOR,
                                 '[data-key="175-14042"]').click()
            print(f"成功点击锂化合物")
            time.sleep(random.uniform(1, 2))

            # 等待并勾选电池级氢氧化锂选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201102250281-14042"] input.ant-checkbox-input').click()
            print("成功选择电池级氢氧化锂")
            time.sleep(random.uniform(1, 2))


            # 等待并点击钴金属
            browser.find_element(By.CSS_SELECTOR,
                                 '[data-key="170-14042"]').click()
            print(f"成功点击钴金属")
            time.sleep(random.uniform(1, 2))

            # 等待并勾选电解钴选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201102250375-14042"] input.ant-checkbox-input').click()
            print("成功选择电解钴")
            time.sleep(random.uniform(1, 2))
            # 等待并点击钴化合物
            browser.find_element(By.CSS_SELECTOR,
                                 '[data-key="142-14042"]').click()
            print(f"成功点击钴化合物")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选四氧化三钴选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201102250240-14042"] input.ant-checkbox-input').click()
            print("成功选择四氧化三钴")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选氯化钴选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201102250301-14042"] input.ant-checkbox-input').click()
            print("成功选择氯化钴")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选硫酸钴选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201102250381-14042"] input.ant-checkbox-input').click()
            print("成功选择氯化钴")
            time.sleep(random.uniform(1, 2))
            # 等待并点击锰化合物
            browser.find_element(By.CSS_SELECTOR,
                                 '[data-key="379-14042"]').click()
            print(f"成功点击锰化合物")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选电池级硫酸锰选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201805300001-14042"] input.ant-checkbox-input').click()
            print("成功选择电池级硫酸锰")
            time.sleep(random.uniform(1, 2))
            # 点击镍分类
            browser.find_element(By.XPATH,
                                 '//*[@id="__next"]/div[2]/div[3]/div/div[2]/div/div[1]/div[2]/span[6]').click()
            print(f"成功点击镍分类")
            time.sleep(random.uniform(1, 2))
            # 等待并点击金属
            browser.find_element(By.CSS_SELECTOR,
                                 '[data-key="3-18"]').click()
            print(f"成功点击金属")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选金川镍选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201102250174-18"] input.ant-checkbox-input').click()
            print("成功选择金川镍")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选电解镍选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201102250239-18"] input.ant-checkbox-input').click()
            print("成功选择电解镍")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选镍豆选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="202008270001-18"] input.ant-checkbox-input').click()
            print("成功选择镍豆")
            time.sleep(random.uniform(1, 2))
            # 等待并点击镍化合物
            browser.find_element(By.CSS_SELECTOR,
                                 '[data-key="561-18"]').click()
            print(f"成功点击镍化合物")
            time.sleep(random.uniform(1, 2))
            # 等待并勾选电池级硫酸镍选择框
            browser.find_element(By.CSS_SELECTOR,
                                 'li[data-key="201908270001-18"] input.ant-checkbox-input').click()
            print("成功选择电池级硫酸镍")
            time.sleep(random.uniform(1, 2))










            # try:
            #     # 输入开始日期

            #     element_start_date = browser.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[3]/div/div[3]/div[1]/div[1]/span[2]/div/input')
            #     ActionChains(browser).double_click(element_start_date).perform()
            #     element_start_date.clear()
            #     element_start_date.send_keys(start_date)
            #     # 点击空白处
            #     ActionChains(browser).move_by_offset(0, 0).click().perform()
            #     time.sleep(1)
            # except Exception as e:
            #     print(f"无法找到开始日期输入框: {e}")
            #
            # try:
            #     # 输入结束日期
            #     element_end_date = browser.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[3]/div/div[3]/div[1]/div[1]/span[4]/div/input')
            #     ActionChains(browser).double_click(element_end_date).perform()
            #     element_end_date.clear()
            #     element_end_date.send_keys(end_date)
            #     # 点击空白处
            #     ActionChains(browser).move_by_offset(0, 0).click().perform()
            #     time.sleep(1)
            # except Exception as e:
            #     print(f"无法找到结束日期输入框: {e}")

            # 提交“查询”
            browser.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[3]/div/div[3]/div[1]/div[1]/button').click()
            print('查询完成')

            browser.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[3]/div/div[3]/div[1]/div[2]/div[2]/img').click()
            print("成功点击导出按钮")
            # 等待文件下载完成
            try:
                excel_path = wait_for_download()
                print(f"文件路径: {excel_path}")
                if excel_path:
                    print("文件下载完成")
                else:
                    print("文件下载超时")
            except Exception as e:(
                print(f"下载失败: {e}"))

            # 导入数据库
            try:
                db_manager = DatabaseManager()
                db_manager.import_excel_data(excel_path)
                print("数据已成功导入数据库")
                try:
                    os.remove(excel_path)
                    temp_dir = os.path.dirname(excel_path)
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    print(f"清理临时文件失败: {e}")
            except Exception as e:
                print(f"导入数据时出错: {str(e)}")

        except Exception as e:
            print(f"异常类型: {type(e)}")  # 打印异常类型
            print(f"异常信息: {str(e)}")  # 打印异常详细信息
            print(f"总点击数量: {click_count}")
            break



# def save_html_content(browser):
#     try:
#         timestamp = time.strftime("%Y%m%d_%H%M%S")
#         domain = urlparse(browser.current_url).netloc.replace('.', '_')
#         domain_folder = os.path.join(html_path, f"{domain}_{timestamp}.html")
#         os.makedirs(domain_folder, exist_ok=True)
#
#         # 创建资讯txt文件夹
#         html_folder = os.path.join(domain_folder, '网页HTML')
#         os.makedirs(html_folder, exist_ok=True)
#
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         filename = f"{domain}_{timestamp}.html"
#         filepath = os.path.join(html_folder, filename)
#
#         with open(filepath, 'w', encoding='utf-8') as f:
#             f.write(browser.page_source)
#         print(f"HTML内容已保存到 {filepath}")
#     except Exception as e:
#         print(f"保存HTML内容时出错: {str(e)}")
# def download_xlsx_file(browser):
#
#
#             # 点击“下载”
#             self.browser.find_element(By.XPATH, '//*[@id="noticeDetail"]/div/div[1]/div[3]/div[1]/button').click()
#             # 等待文件下载完成
#             if self.wait_for_download():
#                 print("文件下载完成")
#                 self.update_crawling_status(current_url, 'completed', content_hash)
#             else:
#                 print("文件下载超时")
#                 self.update_crawling_status(current_url, 'pending')
#         except Exception as e:
#             print(f"下载失败: {e}")
#             self.update_crawling_status(current_url, 'pending')
#         time.sleep(1)
#
#         # 关闭当前的公告详情窗口
#         self.browser.close()
#         # 切换回主窗口，继续处理下一条公告
#         self.browser.switch_to.window(self.browser.window_handles[0])
#         print('当前页面已下载到第', node_num, '条')
#         time.sleep(1)

download_path = create_download_path()
temp_download_path = download_path["temp_download_path"]
final_download_path = download_path["final_download_path"]
html_path = download_path["html_path"]
print(f"{temp_download_path}")

options = setup_chrome_options(temp_download_path)
browser = webdriver.Chrome(options=options)

# 设置页面加载超时
browser.set_page_load_timeout(60)
browser.set_script_timeout(60)

scrapy_url = "https://price.smm.cn/"
browser.get(scrapy_url)


search(browser, '2022-4-30','2025-4-30')
input("按Enter键关闭浏览器...")

# def run(playwright: Playwright) -> None:
#     # 设置临时下载路径
#     temp_download_path = os.path.join(os.getcwd(), 'temp_downloads')
#     os.makedirs(temp_download_path, exist_ok=True)
#
#     # 设置网络共享云盘路径
#     network_drive = r"D:\\厦钨新能源云盘7.0 (2)\\信息管理\\16战略资讯系统\\0战略系统\\3报价系统\\1产品价格"
#     # 设置下载路径
#     final_download_path = os.path.join(network_drive, "公告")
#     base_html_path = os.path.join(network_drive, "HTML")
#     # 创建带日期的HTML文件夹
#     current_date = time.strftime("%Y%m%d")
#     html_path = os.path.join(base_html_path, current_date)
#     # 创建文件夹
#     os.makedirs(final_download_path, exist_ok=True)
#     os.makedirs(html_path, exist_ok=True)
#
#     # 确保网络共享目录存在
#     try:
#         os.makedirs(final_download_path, exist_ok=True)
#         os.makedirs(html_path, exist_ok=True)
#         print(f"成功创建网络共享目录: {final_download_path}")
#         print(f"成功创建网络共享目录: {html_path}")
#     except Exception as e:
#         print(f"创建网络共享目录失败: {e}")
#         raise Exception("无法访问网络共享，请检查网络连接和权限")
#
#
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto("https://price.smm.cn/")
#     page.get_by_role("link", name="账号密码登录").click()
#     page.get_by_role("textbox", name="手机号／邮箱／用户名").click()
#     page.get_by_role("textbox", name="手机号／邮箱／用户名").fill("CXTCXNY")
#     page.get_by_role("textbox", name="输入登录密码").click()
#     page.get_by_role("textbox", name="输入登录密码").fill("scb3351622")
#     page.get_by_role("button", name="登录").click()
#     page.get_by_text("清空").click()
#     page.get_by_text("锂电").click()
#     page.get_by_role("checkbox", name="电池级氢氧化锂（粗颗粒）").check()
#     page.get_by_text("钴金属").click()
#     page.get_by_role("checkbox", name="电解钴(Co≥99.8%)").check()
#     # page.get_by_text("钴化合物").click()
#     # page.get_by_role("checkbox", name="四氧化三钴").check()
#     # page.get_by_role("checkbox", name="氯化钴").check()
#     # page.get_by_role("checkbox", name="硫酸钴", exact=True).check()
#     # page.get_by_text("锰化合物").click()
#     # page.get_by_role("checkbox", name="电池级硫酸锰（出厂价）").check()
#     # page.get_by_text("镍", exact=True).click()
#     # page.get_by_role("checkbox", name="1#金川镍", exact=True).check()
#     # page.get_by_role("checkbox", name="SMM 1#电解镍").check()
#     # page.get_by_role("checkbox", name="镍豆").check()
#     # page.get_by_text("镍化合物").click()
#     # page.get_by_role("checkbox", name="电池级硫酸镍", exact=True).check()
#     page.get_by_role("textbox", name="请选择日期").first.click()
#     page.get_by_role("button", name="上一年 (Control键加左方向键)").click()
#     page.get_by_role("button", name="上一年 (Control键加左方向键)").click()
#     page.get_by_role("button", name="上个月 (翻页上键)").click()
#     page.get_by_role("button", name="上个月 (翻页上键)").click()
#     page.get_by_role("button", name="上个月 (翻页上键)").click()
#     page.get_by_role("button", name="上个月 (翻页上键)").click()
#     page.get_by_role("button", name="上个月 (翻页上键)").click()
#     page.get_by_role("button", name="上个月 (翻页上键)").click()
#     page.get_by_title("2022年4月28日").locator("div").click()
#     page.get_by_role("button", name="查 询").click()
#     with page.expect_download() as download_info:
#         page.get_by_role("img", name="导出表格").click()
#     download = download_info.value
#
#     # # 等待下载完成并获取文件路径
#     # excel_path = wait_for_download(temp_download_path)
#     # move_files_to_network_drive(final_download_path,  temp_download_path)
#     #
#     # # 导入数据库
#     # try:
#     #     db_manager = DatabaseManager()
#     #     db_manager.import_excel_data(excel_path)
#     #     print("数据已成功导入数据库")
#     # except Exception as e:
#     #     print(f"导入数据时出错: {str(e)}")
#     #
#     #
#     input("按Enter键关闭浏览器...")
#     page.close()
#
#     # ---------------------
#     context.close()
#     # browser.close()
#
#
#
# with sync_playwright() as playwright:
#     run(playwright)

