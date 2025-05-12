from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from urllib.parse import urlparse
import os
import random
import requests
from urllib.request import urlretrieve
import hashlib


# search_input = browser.find_element(By.CSS_SELECTOR,'#kw') #找到搜索框
# search_input.send_keys("")  #输入搜索内容

def save_news_data(news_data, browser_url):
    """
    保存新闻数据到文件
    """
    try:
        # 获取当前URL的域名
        domain = urlparse(browser_url).netloc.replace('.', '_')

        # 创建域名文件夹
        domain_folder = os.path.join("D:\\工作\\战略投资部\\战略投资部爬虫\\ys24", '爬虫内容')
        os.makedirs(domain_folder, exist_ok=True)

        # 创建资讯txt文件夹
        news_folder = os.path.join(domain_folder, '资讯txt')
        os.makedirs(news_folder, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{domain}_{timestamp}.txt"
        filepath = os.path.join(news_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            dates = list(news_data.keys())
            print(f"\n总共有 {len(dates)} 个日期:")
            for date in sorted(dates, reverse=True):  # 修改：降序排列日期
                print(f"- {date}")
                print("\n")

            # 按日期降序遍历
            for date in sorted(dates, reverse=True):
                f.write(f"\n==================== {date} ====================\n\n")
                # 对每个日期下的新闻按时间降序排序
                sorted_items = sorted(news_data[date],
                                      key=lambda x: x['Time'],
                                      reverse=True)

                for item in sorted_items:
                    time_str = item['Time'].strip()
                    content_str = item['Content'].strip()
                    if time_str in content_str:
                        content_str = content_str.replace(time_str, '').strip()

                    f.write(f"时间：{time_str}\n")
                    f.write(f"内容：{content_str}\n")
                    # 写入相关资讯
                    if item.get('RelatedNews'):
                        f.write("\n相关资讯：\n")
                        f.write(f"标题：{item['RelatedNews']['title']}\n")
                        f.write(f"来源：{item['RelatedNews']['source']}\n")
                        f.write(f"发布时间：{item['RelatedNews']['publish_time']}\n")
                        f.write(f"正文：{item['RelatedNews']['content']}\n")
                        f.write("\n")
                    f.write("=" * 50 + "\n\n")
        print(f"数据已保存到 {filepath}")
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")


def convert_date_string(date_str):
    """
    将抓取到的日期字符串转换为标准格式
    """
    if "只看重要的" in date_str or "全部金属" in date_str or "设置" in date_str:
        # 使用当前日期作为最新日期
        current_date = datetime.now()
        return current_date.strftime("%Y年%m月%d日")
    return date_str


def save_html_content(browser):
    """
    保存页面HTML内容
    """
    try:
        domain = urlparse(browser.current_url).netloc.replace('.', '_')
        domain_folder = os.path.join("D:\\工作\\战略投资部\\战略投资部爬虫\\ys24", '爬虫内容')
        os.makedirs(domain_folder, exist_ok=True)

        # 创建资讯txt文件夹
        html_folder = os.path.join(domain_folder, '网页HTML')
        os.makedirs(html_folder, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{domain}_{timestamp}.html"
        filepath = os.path.join(html_folder, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(browser.page_source)
        print(f"HTML内容已保存到 {filepath}")
    except Exception as e:
        print(f"保存HTML内容时出错: {str(e)}")


def download_image(image_url, save_dir):
    """
    下载图片
    """
    try:
        image_name = hashlib.md5(image_url.encode()).hexdigest() + '.jpg'
        save_path = os.path.join(save_dir, image_name)

        if not os.path.exists(save_path):
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return save_path
    except Exception as e:
        print(f"下载图片失败: {str(e)}")
    return None


def get_related_news(browser, href):
    """
    获取相关资讯内容
    """
    try:
        # 保留当前窗口
        main_window = browser.current_window_handle
        # 打开新窗口
        browser.execute_script(f"window.open('{href}', '_blank');")
        time.sleep(2)

        # 切换到新窗口
        new_window = [handle for handle in browser.window_handles if handle != main_window][0]
        browser.switch_to.window(new_window)

        try:
            # 获取文章标题
            title = browser.find_element(By.CSS_SELECTOR, '.news-title').text
            print("成功获取标题")
        except Exception as e:
            print(f"获取标题失败: {str(e)}")
            title = "获取失败"

        try:
            # 获取文章来源
            source = browser.find_element(By.CSS_SELECTOR, 'span.detail_news_newsMr10__340aG a').text
            print("成功获取来源")
        except Exception as e:
            print(f"获取来源失败: {str(e)}")
            source = "获取失败"

        try:
            # 获取文章发布时间
            publish_time = browser.find_element(By.CSS_SELECTOR, 'time').text
            print(f"发布时间：{publish_time}")
        except Exception as e:
            print(f"获取时间失败: {str(e)}")
            publish_time = "获取失败"

        try:
            # 获取文章正文区域
            article_element = browser.find_element(By.CSS_SELECTOR, 'div[class*="news-detail-main-article"]')
            article = article_element.text
            print("成功获取正文")

            # #获取文章正文
            # article = browser.find_element(By.CSS_SELECTOR,'div[class*="news-detail-main-article"]').text
            # print("成功获取正文")

            # 获取图片
            images = article_element.find_elements(By.TAG_NAME, 'img')
            image_paths = []

            if images:
                image_dir = os.path.join("D:\\工作\\战略投资部\\战略投资部爬虫\\ys24", '爬虫内容')
                os.makedirs(image_dir, exist_ok=True)

                # 创建新闻图片文件夹
                news_folder = os.path.join(image_dir, '新闻图片')
                os.makedirs(news_folder, exist_ok=True)

                # for img in images:
                #     img_url = img.get_attribute('src')
                #     if img_url:
                #         saved_path = download_image(img_url, image_dir)
                #         if saved_path:
                #             image_paths.append(saved_path)
                # 下载图片并将图片路径添加到正文后面
                for i, img in enumerate(images, 1):
                    img_url = img.get_attribute('src')
                    if img_url:
                        saved_path = download_image(img_url, news_folder)
                        if saved_path:
                            image_paths.append(saved_path)
                            # 在正文后面添加图片路径信息
                            article += f"\n\n[图片{i}] 路径: {saved_path}"

        except Exception as e:
            print(f"获取正文失败: {str(e)}")
            article = "获取失败"

        # 关闭新窗口
        browser.close()
        browser.switch_to.window(main_window)

        # 添加相关资讯获取检查
        result = {
            'title': title,
            'source': source,
            'content': article,
            'images': image_paths,
            'publish_time': publish_time
        }

        print("\n=== 相关资讯获取结果 ===")
        print(f"标题: {result['title']}")
        print(f"来源: {result['source']}")
        print(f"发布时间: {result['publish_time']}")
        print(f"正文长度: {len(result['content'])} 字符")
        print(f"图片数量: {len(result['images'])}")
        print("========================\n")

        return result

    except Exception as e:
        print(f"获取相关资讯内容时出错: {str(e)}")
        if browser.current_window_handle != main_window:
            browser.close()
            browser.switch_to.window(main_window)
        return None


def scroll_page(browser):
    """
    滚动页面
    """
    start_time = time.time()
    click_count = 0
    max_time = 60
    processed_count = 0  # 已爬取的资讯数量
    news_data = {}


    while True:
        try:
            if time.time() - start_time > max_time:
                print(f"已运行{max_time}秒，停止加载")
                print(f"点击次数：{click_count}")
                break

            # 滚动到底部
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            print("已经执行页面滚动")
            # 等待数据加载，这里等待10秒
            time.sleep(random.randint(3, 5))

            news_items = browser.find_elements(By.XPATH, './/span[contains(@class,"live_live")]')
            current_count = len(news_items)
            print(f"当前页面资讯数量：{current_count}")

            if current_count > processed_count:
                for item in news_items[processed_count:]:
                    try:
                        parent_container = item.find_element(By.XPATH,
                                                             './ancestor::div[contains(@class, "live_LiveItem")]')

                        # 获取日期（直接从日期显示区域获取）
                        raw_date = parent_container.find_element(By.XPATH,
                                                                 './/div[contains(@class, "live_LiveItemHeaderInner")]').text
                        date = convert_date_string(raw_date)
                        # date = parent_container.find_element(By.XPATH, './/div[contains(@class, "ant-picker-input")]/input').get_attribute('value')

                        print(f"抓取日期：,{date}")

                        parent_container_time = item.find_element(By.XPATH,
                                                                  './ancestor::div[contains(@class, "live_LiveItemNews")]')
                        # 获取时间和内容
                        time_element = parent_container_time.find_element(By.XPATH,
                                                                          './/div[contains(@class, "live_Time")]/span').text
                        # 组合完整的发布时间
                        full_time = f"{date} {time_element}"
                        print(f"完整发布时间：{full_time}")

                        content = item.text

                        try:
                            related_link = parent_container_time.find_element(By.XPATH,
                                                                              './/a[.//span[contains(@class, "anticon-link")]]')
                            print("已找到相关资讯链接")
                            href = related_link.get_attribute('href')
                            if href:
                                print(f"相关资讯链接: {href}")
                                related_news = get_related_news(browser, href)
                        except:
                            print("未找到相关资讯链接")
                            related_news = None

                        if date not in news_data:
                            news_data[date] = []

                        news_data[date].append({
                            'Time': time_element,
                            'Content': content,
                            'RelatedNews': related_news
                        })
                        # print(f"已爬取资讯：{date} - {time_element} - {content}...")
                    except Exception as e:
                        print(f"单条资讯获取失败: {str(e)}")
            processed_count = current_count
            print(f"当前已处理{processed_count}条资讯")

            try:
                """
                使用JS方法实现按钮点击
                """
                browser.execute_script("document.querySelector('div.loadMore_loadMore__oXnza').click();")
                click_count += 1
                print(f"已经执行JS方法实现按钮点击{click_count}次")

            except:
                """
                使用selenium方法实现按钮点击
                """
                # 查找‘加载更多’按钮
                load_more_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".loadMore_loadMore__oXnza")))
                print("已经执行selenium方法实现按钮查找")
                # load_more_button.click()
                ActionChains(browser).move_to_element(load_more_button).click().perform()
                click_count += 1
                print(f"已经执行selenium方法实现按钮点击{click_count}次")

            time.sleep(random.randint(3, 5))


        except Exception as e:
            print(f"异常类型: {type(e)}")  # 打印异常类型
            print(f"异常信息: {str(e)}")  # 打印异常详细信息
            print(f"总点击数量: {click_count}")
            break

            # 保存HTML内容
    save_html_content(browser)

    try:
        save_news_data(news_data, browser.current_url)
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")

    return news_data


# 修改浏览器初始化部分
# chrome_options = Options()
# chrome_options.add_argument('--headless')  # 启用无头模式
# chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
# chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式
# chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
# chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口大小

# browser = webdriver.Chrome(options=chrome_options)
browser = webdriver.Chrome()

scrapy_url = "https://news.smm.cn/live"
browser.get(scrapy_url)

scroll_page(browser)

# browser.close()
input("按Enter键关闭浏览器...")
