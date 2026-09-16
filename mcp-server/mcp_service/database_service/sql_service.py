import json
import datetime
import decimal
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

# 无参调用会从本文件所在目录逐级向上找 .env，最终命中 mcp-server/.env。
# 之前写的是 Path(__file__).parent / ".env"（即 database_service/.env），
# 那个文件并不存在 —— 之所以还能跑通，只是因为同进程的 neo4j_service 等模块
# 先一步做了无参 load_dotenv() 把环境变量灌进了进程，换个 import 顺序就会连不上库。
load_dotenv()

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
        elif isinstance(value, decimal.Decimal):
            # DECIMAL 列（fee / price / unit_price / salary）必须转换，
            # 否则 json.dumps 会抛 TypeError。
            # 若要保留 "350.50" 这种两位小数的原始格式，可换成 str(value)。
            new_row[key] = float(value)
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
        # 绝不能把异常伪装成空结果。之前这里 return json.dumps([])，
        # 模型拿到 [] 会判定"查无数据"，于是对用户回一句"未查询到该记录"，
        # 而真正的失败原因只留在服务端控制台 —— 极难排查。
        # 返回明确的错误文本，模型可以据此改写 SQL 或如实告知用户。
        print("SQL 执行异常:", e, "| SQL:", query)
        return f"SQL 执行失败：{e}"
    finally:
        conn.close()