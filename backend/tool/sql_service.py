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
    conn = None
    cursor = None
    try:
        conn = pool.get_connection()  # 获取连接
        cursor = conn.cursor()  # 创建游标
        cursor.execute(query, params)  # 执行SQL语句
        # SELECT 有结果集：先 fetchall 消费完结果再返回（绝不能先 commit）
        if cursor.description is not None:
            rs = cursor.fetchall()  # 获取结果
            return rs
        # INSERT/UPDATE/DELETE 无结果集：此时才需要提交事务
        conn.commit()
        return []
    except Exception as e:
        print("异常错误", e)
        return "sql执行失败"
    finally:
        # 先关游标再还连接，且 close 失败不再向外抛出，避免二次异常
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception as e:
                print("异常错误", e)

if __name__ == '__main__':
    userName = "sql01"
    password = "123456"
    sql = "SELECT user_id FROM user_info WHERE user_name=%s AND password=%s"
    params =  (userName, password)
    res = sql_tool_pool(sql, params)
    data = res[0]
    print(data,type(data))

