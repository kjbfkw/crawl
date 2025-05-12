from db_config import DatabaseManager

excel_path = r"D:\工作\战略投资部\战略投资部爬虫\有色网_价格获取\temp_download\prices_20250507 (2).xlsx"
db_manager = DatabaseManager()
db_manager.import_excel_data(excel_path)
print("数据已成功导入数据库")