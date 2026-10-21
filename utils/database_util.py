import sqlite3
import json
from datetime import datetime
from utils.data_util import  timestamp_to_str

class SqliteDB:
    
    def __init__(self):
        self.conn = sqlite3.connect('douyin-spider.db')
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS SpiderDYAdvertisingLog (work_id INTEGER PRIMARY KEY, work_title TEXT, work_type TEXT, work_url TEXT, user_id TEXT, nickname TEXT,publish_time NUMERIC, create_time NUMERIC)''')
        except sqlite3.Error as e:
            print(f"SqliteDB 数据库初始化发生错误: {e}")
            self.conn.rollback()
            self.cursor.close()
            self.conn.close()

    def AddLog(self, advJson, **kwargs):
        """
        添加日志.
        :param self: object object.
        :param advJson: 广告信息.
        :return: JSON.
        """
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute(f''' INSERT INTO SpiderDYAdvertisingLog (work_id, work_title, work_type, work_url, user_id, nickname, publish_time, create_time)
            VALUES ({advJson['work_id']}, '{advJson['title']}', '{advJson['work_type']}', '{advJson['work_url']}', '{advJson['user_id']}', '{advJson['nickname']}', '{timestamp_to_str(advJson['create_time'] * 1000)}', '{current_datetime}')''')
            self.conn.commit()
            return {'work_id':{advJson['work_id']}}
        except sqlite3.Error as e:
            print(f"SqliteDB.AddLog 添加数据时发生错误： {e}")
            self.conn.rollback()

    def GetWhere(self, **kwargs):
        """
        根据id查询日志
        :param self: object object.
        :return: JSON.
        """
        try:
            sqlwhere = "WHERE 1=1";
            for key, value in kwargs.items():
                sqlwhere += f" AND {key}='{value}'"
            self.cursor.execute(f'''SELECT work_id, work_title, work_type, work_url, user_id, nickname, publish_time, create_time FROM SpiderDYAdvertisingLog {sqlwhere};''')
            rows = self.cursor.fetchall()
            # 1. 获取列名（例如 ['id', 'name', 'age', 'created_at']）
            columns = [desc[0] for desc in self.cursor.description]
            # 2. 将每一行数据与列名组合成字典，生成字典列表
            data_list = [dict(zip(columns, row)) for row in rows]
            # 3. 将字典列表转换为 JSON 字符串（ensure_ascii=False 保证中文正常显示）
            json_data = json.dumps(data_list, indent=4, ensure_ascii=False)
            return json_data
        except sqlite3.Error as e:
            print(f"SqliteDB.GetId 获取数据时发生错误：{e}，id：{id}")
            self.conn.rollback()

    def GetExist(self, **kwargs):
        """
        根据id查询日志
        :param self: object object.
        :return: JSON.
        """
        try:
            sqlwhere = "WHERE 1=1";
            for key, value in kwargs.items():
                sqlwhere += f" AND {key}='{value}'"
            self.cursor.execute(f'''SELECT work_id, work_title, work_type, work_url, user_id, nickname, publish_time, create_time FROM SpiderDYAdvertisingLog {sqlwhere};''')
            rows = self.cursor.fetchall()
            if len(rows) > 0:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print(f"SqliteDB.GetId 获取数据时发生错误：{e}，id：{id}")
            self.conn.rollback()

    def GetCount(self, begin_time, end_time):
        """
        获取数量
        :param self: object object.
        :return: JSON.
        """
        try:
            time1 = begin_time.strftime("%Y-%m-%d %H:%M:%S")
            time2 = end_time.strftime("%Y-%m-%d %H:%M:%S")
            sqlwhere = f"WHERE 1=1 AND create_time > '{time1}' AND create_time < '{time2}'";
            self.cursor.execute(f'''SELECT COUNT(*) FROM SpiderDYAdvertisingLog {sqlwhere};''')
            rows = self.cursor.fetchall()
            return rows[0][0]
        except sqlite3.Error as e:
            print(f"SqliteDB.GetId 获取数据时发生错误：{e}，id：{id}")
            self.conn.rollback()
    