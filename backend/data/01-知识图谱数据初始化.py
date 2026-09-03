import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph

import warnings
from langchain_core._api import LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
# 加载环境变量
load_dotenv()
class Neo4jChatBot:
    def __init__(self):
        # 连接Neo4j
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URL"),
            username=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_DB"),
        )

    def _init_sample_data(self):
        """初始化示例数据"""
        init_queries = [
            # 清空现有数据
            "MATCH (n) DETACH DELETE n",

            # 创建医生节点
            "CREATE (:Doctor {name: '张明', age: 45, specialty: '心血管内科', title: '主任医师', hospital: '北京协和医院'})",
            "CREATE (:Doctor {name: '李华', age: 38, specialty: '神经外科', title: '副主任医师', hospital: '上海华山医院'})",
            "CREATE (:Doctor {name: '王强', age: 52, specialty: '肿瘤科', title: '主任医师', hospital: '中山大学肿瘤医院'})",
            "CREATE (:Doctor {name: '陈雪', age: 41, specialty: '儿科', title: '副主任医师', hospital: '北京儿童医院'})",
            "CREATE (:Doctor {name: '刘洋', age: 36, specialty: '骨科', title: '主治医师', hospital: '华西医院'})",
            "CREATE (:Doctor {name: '赵敏', age: 48, specialty: '妇产科', title: '主任医师', hospital: '复旦大学附属妇产科医院'})",
            "CREATE (:Doctor {name: '周涛', age: 39, specialty: '眼科', title: '副主任医师', hospital: '同仁医院'})",
            "CREATE (:Doctor {name: '吴芳', age: 44, specialty: '消化内科', title: '主任医师', hospital: '瑞金医院'})",

            # 创建患者节点
            "CREATE (:Patient {name: '王建国', age: 65, gender: '男', condition: '高血压', admission_date: '2024-01-15'})",
            "CREATE (:Patient {name: '李秀英', age: 72, gender: '女', condition: '糖尿病', admission_date: '2024-01-20'})",
            "CREATE (:Patient {name: '张伟', age: 45, gender: '男', condition: '腰椎间盘突出', admission_date: '2024-01-25'})",
            "CREATE (:Patient {name: '刘芳', age: 38, gender: '女', condition: '甲状腺结节', admission_date: '2024-02-01'})",
            "CREATE (:Patient {name: '陈明', age: 56, gender: '男', condition: '冠心病', admission_date: '2024-02-05'})",
            "CREATE (:Patient {name: '杨丽', age: 29, gender: '女', condition: '妊娠期糖尿病', admission_date: '2024-02-10'})",
            "CREATE (:Patient {name: '黄强', age: 61, gender: '男', condition: '白内障', admission_date: '2024-02-15'})",
            "CREATE (:Patient {name: '周婷', age: 42, gender: '女', condition: '胃溃疡', admission_date: '2024-02-20'})",

            # 创建医院节点
            "CREATE (:Hospital {name: '北京协和医院', level: '三甲', location: '北京', established: 1921})",
            "CREATE (:Hospital {name: '上海华山医院', level: '三甲', location: '上海', established: 1907})",
            "CREATE (:Hospital {name: '中山大学肿瘤医院', level: '三甲', location: '广州', established: 1964})",
            "CREATE (:Hospital {name: '北京儿童医院', level: '三甲', location: '北京', established: 1942})",
            "CREATE (:Hospital {name: '华西医院', level: '三甲', location: '成都', established: 1892})",
            "CREATE (:Hospital {name: '瑞金医院', level: '三甲', location: '上海', established: 1907})",

            # 创建药品节点
            "CREATE (:Drug {name: '阿司匹林', type: '抗血小板', manufacturer: '拜耳', approval_date: '1990-05-15'})",
            "CREATE (:Drug {name: '胰岛素', type: '降血糖', manufacturer: '诺和诺德', approval_date: '1985-08-20'})",
            "CREATE (:Drug {name: '阿托伐他汀', type: '降血脂', manufacturer: '辉瑞', approval_date: '1997-03-10'})",
            "CREATE (:Drug {name: '左甲状腺素', type: '激素', manufacturer: '默克', approval_date: '2000-11-05'})",

            # 创建诊疗关系
            "MATCH (d:Doctor {name: '张明'}), (p:Patient {name: '王建国'}) CREATE (d)-[:TREATS {diagnosis: '原发性高血压', date: '2024-01-16'}]->(p)",
            "MATCH (d:Doctor {name: '李华'}), (p:Patient {name: '陈明'}) CREATE (d)-[:TREATS {diagnosis: '冠状动脉粥样硬化', date: '2024-02-06'}]->(p)",
            "MATCH (d:Doctor {name: '王强'}), (p:Patient {name: '李秀英'}) CREATE (d)-[:CONSULTS {purpose: '糖尿病并发症筛查', date: '2024-01-21'}]->(p)",
            "MATCH (d:Doctor {name: '陈雪'}), (p:Patient {name: '杨丽'}) CREATE (d)-[:TREATS {diagnosis: '妊娠期糖尿病', date: '2024-02-11'}]->(p)",
            "MATCH (d:Doctor {name: '刘洋'}), (p:Patient {name: '张伟'}) CREATE (d)-[:TREATS {diagnosis: '腰椎间盘突出症', date: '2024-01-26'}]->(p)",
            "MATCH (d:Doctor {name: '赵敏'}), (p:Patient {name: '刘芳'}) CREATE (d)-[:CONSULTS {purpose: '甲状腺结节评估', date: '2024-02-02'}]->(p)",
            "MATCH (d:Doctor {name: '周涛'}), (p:Patient {name: '黄强'}) CREATE (d)-[:TREATS {diagnosis: '老年性白内障', date: '2024-02-16'}]->(p)",
            "MATCH (d:Doctor {name: '吴芳'}), (p:Patient {name: '周婷'}) CREATE (d)-[:TREATS {diagnosis: '胃溃疡', date: '2024-02-21'}]->(p)",

            # 创建工作关系
            "MATCH (d:Doctor {name: '张明'}), (h:Hospital {name: '北京协和医院'}) CREATE (d)-[:WORKS_AT {department: '心血管内科', since: 2005}]->(h)",
            "MATCH (d:Doctor {name: '李华'}), (h:Hospital {name: '上海华山医院'}) CREATE (d)-[:WORKS_AT {department: '神经外科', since: 2010}]->(h)",
            "MATCH (d:Doctor {name: '王强'}), (h:Hospital {name: '中山大学肿瘤医院'}) CREATE (d)-[:WORKS_AT {department: '肿瘤科', since: 2000}]->(h)",
            "MATCH (d:Doctor {name: '陈雪'}), (h:Hospital {name: '北京儿童医院'}) CREATE (d)-[:WORKS_AT {department: '儿科', since: 2008}]->(h)",
            "MATCH (d:Doctor {name: '刘洋'}), (h:Hospital {name: '华西医院'}) CREATE (d)-[:WORKS_AT {department: '骨科', since: 2012}]->(h)",
            "MATCH (d:Doctor {name: '赵敏'}), (h:Hospital {name: '复旦大学附属妇产科医院'}) CREATE (d)-[:WORKS_AT {department: '妇产科', since: 2003}]->(h)",
            "MATCH (d:Doctor {name: '周涛'}), (h:Hospital {name: '同仁医院'}) CREATE (d)-[:WORKS_AT {department: '眼科', since: 2009}]->(h)",
            "MATCH (d:Doctor {name: '吴芳'}), (h:Hospital {name: '瑞金医院'}) CREATE (d)-[:WORKS_AT {department: '消化内科', since: 2006}]->(h)",

            # 创建用药关系
            "MATCH (p:Patient {name: '王建国'}), (dr:Drug {name: '阿司匹林'}) CREATE (p)-[:TAKES {dosage: '100mg', frequency: '每日一次', start_date: '2024-01-16'}]->(dr)",
            "MATCH (p:Patient {name: '李秀英'}), (dr:Drug {name: '胰岛素'}) CREATE (p)-[:TAKES {dosage: '10单位', frequency: '每日两次', start_date: '2024-01-21'}]->(dr)",
            "MATCH (p:Patient {name: '陈明'}), (dr:Drug {name: '阿托伐他汀'}) CREATE (p)-[:TAKES {dosage: '20mg', frequency: '每晚一次', start_date: '2024-02-06'}]->(dr)",
            "MATCH (p:Patient {name: '刘芳'}), (dr:Drug {name: '左甲状腺素'}) CREATE (p)-[:TAKES {dosage: '50mcg', frequency: '每日一次', start_date: '2024-02-02'}]->(dr)",

            # 创建医生合作关系
            "MATCH (d1:Doctor {name: '张明'}), (d2:Doctor {name: '王强'}) CREATE (d1)-[:COLLABORATES_WITH {project: '心血管疾病与肿瘤关联研究', since: 2020}]->(d2)",
            "MATCH (d1:Doctor {name: '李华'}), (d2:Doctor {name: '陈雪'}) CREATE (d1)-[:COLLABORATES_WITH {project: '儿童神经系统疾病研究', since: 2022}]->(d2)",
            "MATCH (d1:Doctor {name: '赵敏'}), (d2:Doctor {name: '吴芳'}) CREATE (d1)-[:COLLABORATES_WITH {project: '妊娠期消化系统疾病研究', since: 2021}]->(d2)",

            # 创建医院转诊关系
            "MATCH (h1:Hospital {name: '北京儿童医院'}), (h2:Hospital {name: '北京协和医院'}) CREATE (h1)-[:REFERS_TO {reason: '复杂病例会诊', frequency: '月度'}]->(h2)",
            "MATCH (h1:Hospital {name: '华西医院'}), (h2:Hospital {name: '上海华山医院'}) CREATE (h1)-[:REFERS_TO {reason: '神经外科专家会诊', frequency: '季度'}]->(h2)"
        ]
        for query in init_queries:
            self.graph.query(query)
        print("数据初始化完毕")


if __name__ == "__main__":
    chatbot = Neo4jChatBot()
    chatbot._init_sample_data()

