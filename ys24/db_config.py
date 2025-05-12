import mysql.connector
import hashlib
from datetime import datetime
import json


class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '259399',
            'database': 'news_url',
            'port': 3306,
            'charset': 'utf8mb4',
            'auth_plugin': 'mysql_native_password',
            'buffered': True
        }
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
            print("数据库连接成功")
        except mysql.connector.Error as err:
            print(f"数据库连接失败: {err}")
            raise

    def get_content_hash(self, content):
        """计算内容的SHA256哈希值"""
        return hashlib.sha256(str(content).encode()).hexdigest()

    def check_url_exists(self, url, table_name):
        """检查URL是否已存在于指定表中"""
        sql = f"SELECT content_hash FROM {table_name} WHERE url = %s AND del_flag = '0'"
        self.cursor.execute(sql, (url,))
        return self.cursor.fetchone()


    def save_article(self, url, content, images_name, source, publish_time):
        """保存主要文章内容"""
        try:
            content_hash = self.get_content_hash(content)
            existing = self.check_url_exists(url, 'article_pages')
            print(existing)

            if existing and existing['content_hash'] == content_hash:
                print("文章内容未变化，跳过保存")
                return None

            sql = """
            INSERT INTO article_pages 
            (url, content, content_hash, images_name, source, publish_time, crawl_time, last_crawled)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            self.cursor.execute(sql, (url, content, content_hash, images_name, source, publish_time))
            self.conn.commit()
            return self.cursor.lastrowid

        except mysql.connector.Error as err:
            print(f"保存文章失败: {err}")
            self.conn.rollback()
            return None

    def save_related_article(self, parent_id, url, content, title, image_name, source, publish_time):
        """保存相关文章内容"""
        try:
            content_hash = self.get_content_hash(content)
            existing = self.check_url_exists(url, 'related_pages')

            if existing and existing['content_hash'] == content_hash:
                print("相关文章内容未变化，跳过保存")
                return

            sql = """
            INSERT INTO related_pages 
            (parent_article_id, url, content, title, image_name, content_hash, 
            source, publish_time, crawl_time, last_crawled)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            self.cursor.execute(sql, (
                parent_id, url, content, title, image_name,
                content_hash, source, publish_time
            ))
            self.conn.commit()

        except mysql.connector.Error as err:
            print(f"保存相关文章失败: {err}")
            self.conn.rollback()

    def update_related_news_status(self, article_id):
        """更新文章的相关资讯状态"""
        try:
            sql = """
            UPDATE article_pages 
            SET related_news = 'Yes'
            WHERE id = %s
            """
            self.cursor.execute(sql, (article_id,))
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"更新相关资讯状态失败: {err}")
            self.conn.rollback()

    def add_to_queue(self, url, status):
        """添加URL到爬取队列"""
        try:
            update_queue = """
                    UPDATE `news_url`.`crawling_queue` 
                    SET status = %s, last_crawled = NOW(), create_time = NOW()
                    WHERE url = %s
                    """
            self.cursor.execute(update_queue, (url, status))
            print(f"已更新状态为{status}的URL: {url}")

        except mysql.connector.Error as err:
            print(f"添加URL到队列失败: {err}")
            self.conn.rollback()

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

