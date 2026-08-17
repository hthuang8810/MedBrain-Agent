import mysql.connector.pooling
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=20,
    host=os.getenv("MYSQL_URL"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)


class MySQLArgs(BaseModel):
    query: str = Field(..., description="sql语句")
def sql_tool_pool(query: str, params: tuple = None)->str:
    """
    MySQL数据库查询
    """
    conn = pool.get_connection()  # 获取连接
    cursor = conn.cursor()  # 创建游标
    try:
        cursor.execute(query, params)  # 执行SQL语句
        rs = cursor.fetchall()  # 获取结果
        return rs
    except Exception as e:
        print("异常错误", e)
        return "sql执行失败"
    finally:
        conn.close()

if __name__ == '__main__':
    userName = "sql01"
    password = "123456"
    sql = "SELECT user_id FROM user_info WHERE user_name=%s AND password=%s"
    params =  (userName, password)
    res = sql_tool_pool(sql, params)
    data = res[0]
    print(data,type(data))

