import json
import datetime
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path)

pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=20,
    host=os.getenv("MYSQL_URL"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)

def timedelta_to_str(td):
    """将 timedelta 转为 HH:MM:SS 字符串"""
    if td is None:
        return None
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def serialize_row(row):
    """将数据库行中的非 JSON 序列化类型转为字符串"""
    new_row = {}
    for key, value in row.items():
        if isinstance(value, datetime.datetime):
            new_row[key] = value.isoformat()
        elif isinstance(value, datetime.date):
            new_row[key] = value.isoformat()
        elif isinstance(value, datetime.time):
            new_row[key] = value.isoformat()
        elif isinstance(value, datetime.timedelta):
            new_row[key] = timedelta_to_str(value)  # ← 关键转换！
        else:
            new_row[key] = value
    return new_row

def sql_tool_pool(query: str, params: tuple = None) -> str:
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        serializable_rows = [serialize_row(row) for row in rows]
        return json.dumps(serializable_rows, ensure_ascii=False)
    except Exception as e:
        print("SQL 执行异常:", e)
        return json.dumps([])
    finally:
        conn.close()