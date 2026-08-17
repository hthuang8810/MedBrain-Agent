from pydantic import BaseModel,Field #输入参数验证
#智能体工具的装饰器
from langchain.tools import tool
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
#加载环境变量
load_dotenv()

#定义一个neo4j连接池类
class Neo4jPool:
    _driver = None
    def __init__(self,url,user,password,database,pool_size=10):
        self.url = url
        self.username = user
        self.password = password
        self.database = database
        self.pool_size = pool_size

    #创建一个ne44j驱动
    def create_driver(self):
        if self._driver is None:
            self._driver =GraphDatabase.driver(
                self.url,# 数据库地址
                auth=(self.username,self.password),# 用户名和密码
                max_connection_pool_size=self.pool_size # 连接池大小
            )

        return self._driver
     #释放资源
    def close(self):
         if self._driver is not None:
             self._driver.close()

#创建一个neo4j连接池
neo4j_pool = Neo4jPool(
    url=os.getenv("NEO4J_URL"),
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD"),
    database=os.getenv("NEO4J_DATABASE"),
)

class Neo4jArgs(BaseModel):
    query:str =Field(...,description="cypher语句")

def neo4j_tool_pool(query:str)->str:
    """
     执行cypher语句
    """
    try:
         #获取驱动
         driver = neo4j_pool.create_driver()
         #创建一个会话
         with driver.session(database=neo4j_pool.database) as session:
             rs  = session.run(query)
             print("rs：", rs)
             data = [r for r in rs]
             print("sql结果：", data)
             return str(data)
    except Exception as e:
        print("异常错误",e)
        return "cypher执行失败"
    finally:
        neo4j_pool.close()

if __name__ == '__main__':
    result = neo4j_tool_pool.invoke({
        "query": "MATCH (d:Doctor {name: '刘洋'})-[:WORKS_AT]->(h:Hospital) RETURN h.name"
    })
    print(result)
