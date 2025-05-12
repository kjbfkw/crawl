import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime
import os
from decimal import Decimal


class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '259399',
            'database': 'price_pages',
            'port': 3306,
            'charset': 'utf8mb4',
            'auth_plugin': 'mysql_native_password'
        }
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("数据库连接成功")
        except Error as e:
            print(f"数据库连接错误: {e}")
            return None

    def calculate_change_percentage(self, change_amount, price_avg):
        """计算涨跌幅"""
        if price_avg and change_amount:
            try:
                # 当前价格减去涨跌额得到前一日价格
                prev_price = float(price_avg) - float(change_amount)
                if prev_price != 0:
                    return (float(change_amount) / prev_price) * 100
            except (ValueError, TypeError):
                pass
        return None

    # def process_excel_data(self, df):
    #     """处理Excel数据"""
    #     # 设置列名
    #     df.columns = ['日期', '产品代码', '产品名称', '规格', '价格区间', '均价', '涨跌额',
    #                   '涨跌幅', '单位', '备注', '最低价', '最高价', '中间价']
    #
    #     # 转换日期格式
    #     df['日期'] = pd.to_datetime(df['日期'])
    #
    #     # 处理数值列
    #     numeric_columns = ['均价', '涨跌额', '最低价', '最高价']
    #     for col in numeric_columns:
    #         df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
    #
    #     return df

    @staticmethod
    def parse_date(date_str):
        """静态方法解析日期字符串"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def preprocess_data(self, excel_path):
        try:
            """预处理Excel数据"""
            # 读取Excel文件
            df = pd.read_excel(excel_path, header=1, engine="openpyxl")
            df = df[df["日期"] != "总均价"]

            # # 电解钴数据
            # df_cobalt = df.iloc[:, [0, 1, 2, 3, 4]].copy()
            # df_cobalt["product_name"] = "电解钴(Co≥99.8%)"
            # df_cobalt.columns = ["date", "price_low", "price_high", "price_avg", "change_amount", "product_name"]
            #
            # # 电池级氢氧化锂数据
            # df_lithium = df.iloc[:, [0, 5, 6, 7, 8]].copy()
            # df_lithium["product_name"] = "电池级氢氧化锂（粗颗粒）"
            # df_lithium.columns = ["date", "price_low", "price_high", "price_avg", "change_amount", "product_name"]

            # 获取所有产品数据
            products = ["电池级硫酸镍", "镍豆", "SMM1#电解镍", "1#金川镍", "电池级硫酸锰（出厂价）", "硫酸钴", "氯化钴", "四氧化三钴", "电解钴（Co>99.8%）", "电池级氢氧化锂（粗颗粒）"]
            products_data = []
            for idx, product_name in enumerate(products):
                # 计算每组数据的起始列（日期列为0，每组占4列）
                start_col = 1 + 4 * idx
                # 提取日期列和当前产品的4列数据
                product_df = df.iloc[:, [0] + list(range(start_col, start_col + 4))].copy()

                # 统一列名并添加产品名称
                product_df.columns = ["date", "price_low", "price_high", "price_avg", "change_amount"]
                product_df["product_name"] = product_name
                products_data.append(product_df)

            # 合并数据
            final_df = pd.concat(products_data, ignore_index=True)
            final_df = final_df.where(pd.notnull(final_df), None)
            final_df["unit"] = "元/吨"
            # 使用静态方法解析日期
            final_df['date'] = final_df['date'].apply(DatabaseManager.parse_date)
            final_df = final_df.dropna(subset=['date'])

            # 转换数值列
            numeric_columns = ['price_low', 'price_high', 'price_avg', 'change_amount']
            for col in numeric_columns:
                final_df[col] = pd.to_numeric(final_df[col].astype(str).str.replace(',', ''), errors='coerce')
            return final_df
        except Exception as e:
            print(f"预处理数据错误: {e}")
            raise

    def import_excel_data(self, excel_path):
        try:
            # 预处理数据
            df = self.preprocess_data(excel_path)

            if not self.connection.is_connected():
                self.connect()

            cursor = self.connection.cursor()
            current_time = datetime.now()

            # 遍历数据框并插入数据库
            for _, row in df.iterrows():
                change_percentage = self.calculate_change_percentage(row['change_amount'], row['price_avg'])
                date_str = row['date'].strftime("%Y-%m-%d")
                # 处理价格区间
                query = """
                               INSERT INTO smm_price_data (
                                   product_name, date, price_low, price_high, 
                                   price_avg, change_amount, change_percentage, unit,
                                   create_by, create_time, del_flag
                               ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               """
                values = (
                    row['product_name'],
                    date_str,
                    row['price_low'],
                    row['price_high'],
                    row['price_avg'],
                    row['change_amount'],
                    change_percentage,
                    row['unit'],
                    'system',  # create_by
                    current_time,  # create_time
                    '0'  # del_flag
                )

                try:
                    cursor.execute(query, values)
                    self.connection.commit()
                except Error as e:
                    print(f"插入数据错误 - 产品: {row['product_name']}, 日期: {row['date']}, 错误: {e}")
                    self.connection.rollback()

            print("数据导入成功")

        except Error as e:
            print(f"数据导入错误: {e}")
        finally:
            cursor.close()

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
