from concurrent.futures.thread import ThreadPoolExecutor
from model.model_management import MyModel
from tool.sql_tool_pool import sql_tool_pool
from tool.neo4j_tool_pool import neo4j_tool_pool
from tool.faiss_tool import faiss_tool
from tool.doc_tool_api import doc_tool_pool
from tool.amap_tool import amap_tool
from tool.email_tool import send_email_tool
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from utils.inMemoryHistory_redis import get_session_history
import hashlib
import redis

# 连接redis
client = redis.Redis(host='localhost', port=6379, db=0, protocol=2)  # protocol=2: 兼容 Redis<6,避免 HELLO 命令

class ChatAgent:
    # 创建一个智能体对象
    _agent = None
    # 初始化
    def __init__(self, ):
        # 创建一个模型对象
        models = MyModel()
        self.llm = models.get_line_model()
        self._agent = self.create_agent()
    # 创建一个智能体
    def create_agent(self):
        # 创建工具列表
        tools = [sql_tool_pool, neo4j_tool_pool, faiss_tool, amap_tool, doc_tool_pool, send_email_tool]
        # 创建提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system","""
            你是一个医疗助手，你有六个工具:
            1. sql_tool_pool sql查询工具
            数据库表的结构信息是以下信息：
             departments - 科室信息表
                id 科室编号 name 科室名称 floor 所在楼层 head_doctor 科室主任 established_date 成立日期
             doctors - 医生信息表
                id 医生编号 name 医生姓名 department_id 所属科室编号 specialty 专业领域 license_number 执业证号 phone 联系电话 email 电子邮箱 hire_date 入职日期 salary 薪资
             patients - 病人信息表
                id 病人编号 name 病人姓名 id_card 身份证号 gender 性别 birth_date 出生日期 email 邮箱 phone 联系电话 emergency_contact 紧急联系人 blood_type 血型 created_at 创建时间
             medical_records - 病历表 
                id 病历编号 patient_id 病人编号 doctor_id 医生编号 department_id 科室编号 chief_complaint 主诉 diagnosis 诊断结果 treatment_plan 治疗方案 visit_date 就诊日期 next_visit_date 复诊日期 fee 诊疗费用
             edicines - 药品表
                id 药品编号 name 药品名称 type 药品类型 manufacturer 生产厂家 unit_price 单价 stock_quantity 库存数量 prescription_required 是否需要处方 approval_number 批准文号
            prescriptions - 处方表
                id 处方编号 record_id 病历编号 medicine_id 药品编号 dosage 用药剂量 frequency 用药频率 duration_days 用药天数 quantity 药品数量
            medical_exams - 检查项目表
                id 检查项目编号 name 检查项目名称 category 检查类别 normal_range 正常范围 price 检查价格 duration_minutes 检查时长
            exam_records - 检查记录表
               id 检查记录编号 record_id 病历编号 exam_id 检查项目编号 exam_date 检查日期 result 检查结果
            
            2. neo4j_tool_pool 执行Cypher查询图数据库，包括医生、病人、医院、药品以及它们之间的关系。
             数据库模式：
             节点类型: 
             - Doctor: name, age, specialty, title, hospital
             - Patient: name, age, gender, condition, admission_date
             - Hospital: name, level, location, established
             - Drug: name, type, manufacturer, approval_date
            
             关系类型和方向:
             - (Doctor)-[:TREATS]->(Patient) - 医生治疗患者
             - (Doctor)-[:CONSULTS]->(Patient) - 医生咨询患者
             - (Doctor)-[:WORKS_AT]->(Hospital) - 医生在医院工作
             - (Patient)-[:TAKES]->(Drug) - 患者服用药物
             - (Doctor)-[:COLLABORATES_WITH]->(Doctor) - 医生间合作
             - (Hospital)-[:REFERS_TO]->(Hospital) - 医院间转诊
            
            3. faiss_tool 在FAISS向量数据库中查询答案
             1. 用户会提出医疗健康相关问题，例如：症状、疾病、康复、日常护理等。
             2. 你不能直接进行诊断、开处方或给出个性化治疗方案。
             3. 你的回答应客观、准确、通俗易懂，并尽量基于现有医学知识。
             4. 如果调用工具后仍无法找到足够信息，应明确告知用户。
             5. 尽量在回答中引用或总结知识库内容，让用户知道信息来源。
             重要，请先使用工具faiss_tool来回答用户问题，如果没有答案，请直接告诉我，不要有其他信息
            
            4. amap_tool 医院推荐
             1.根据用户提问的病情类型和严重程度选择是否查询
             2.查询前先询问用户的所在地城市名称
             3.城市名称只要具体的市名，比如：北京市->北京；成都市金牛区->成都
             4.从这些医院类型中选择目标医院类型名称
             "综合医院,三级甲等医院,卫生院,专科医院,整形美容,口腔医院,眼科医院,
              耳鼻喉医院,胸科医院,骨科医院,肿瘤医院,脑科医院,妇科医院,精神病医院,
              传染病医院,诊所,急救中心,疾病预防,医药保健相关,药房"
              
            5. doc_tool_pool 生成医疗报告文档的工具,
            当用户提出以下请求时（如“生成报告”、“导出报告”、“生成PDF/Word报告”、“生成XXX的医疗报告”）：
            1. 使用 `sql_tool_pool` 查询患者在 MySQL 数据库中的详细就诊、用药、检查记录；
            2. 使用 `neo4j_tool_pool` 查询该患者在图数据库中的医生、医院、药品关联信息；
            3. 将查询结果整合成一份结构化医疗报告文本；
            4. 根据用户需求调用 `generate_word` 或 `generate_pdf` 生成报告文件。
            5. 生成完成之后提示用户生成的格式，并询问是否需要发送到邮箱

            6. send_email_tool 邮件发送工具
            参数：to_email 收件人邮箱, subject 邮件主题, content 邮件内容
            1. 收件人邮箱优先用 sql_tool_pool 从 patients 表的 email 字段查询
            2. 若该病人未登记邮箱，再向用户询问要发送到哪个邮箱
            3. 调用前必须先与用户确认收件人邮箱，用户未明确要求发送时不要发送

            ──────────────────────────────
            【报告生成格式建议】
            
            医疗报告：{{patient_name}}
            ──────────────────────────────
            基本信息：
              姓名：{{patient_name}}  性别：{{gender}}  出生日期：{{birth_date}}  
              联系电话：{{phone}}  血型：{{blood_type}}  
            
            主诉与诊断：
              主诉：{{chief_complaint}}
              诊断结果：{{diagnosis}}
              治疗方案：{{treatment_plan}}
            
            医生与医院信息：
              医生：{{doctor_name}}（{{specialty}}）
              科室：{{department_name}}
              医院：{{hospital_name}}
            
            用药记录：
            {{medicine_list}}
            
            检查记录：
            {{exam_records}}
            
            随访信息：
              费用合计：{{fee}}
            
            ──────────────────────────────
            【输出要求】
            - 若查询结果存在，生成报告文件并输出文件路径；
            - 若查询不到信息，仅输出 “未查询到该记录”；
            - 输出格式简洁明了，不附加额外说明。
            ________________________________
            
            数据库查询指南:
             1. 直接回答用户的问题，不要过度解释
             2. 如果查询不到数据，请明确告知用户
             3. 保持回答简洁明了
             4. 所有关系之间的查询使用Neo4j工具
             5. 关系方向为医生治疗患者，不是患者治疗医生。
             注意: 如果Neo4j查询返回警告说标签不存在，说明图数据库中没有相应数据，请使用SQL工具。
             
            """),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        # 创建智能体
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt,
        )
        # 创建智能体执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
        )
        # 创建多轮历史对话消息组件
        history = RunnableWithMessageHistory(
            agent_executor,
            get_session_history,
            input_messages_key="input",
            output_messages_key="output",
            history_key="history",
        )
        return history
    def get_agent(self):
        """返回 RunnableWithMessageHistory 实例，供流式调用"""
        return self._agent

    # 对话函数
    def speak(self, question: str, session_id):
        # 定义一个会话存储器
        config = {"configurable": {"session_id": session_id if session_id else "userA"}}
        rst = self._agent.invoke({"input": question}, config)
        return rst.get("output")

    # 缓存函数
    def cache_speak(self, question: str, session_id):
        # 定义一个key, 保证每个问题的唯一性
        key = hashlib.sha256(question.encode()).hexdigest()
        # 判断缓存是否有问题
        rs = client.get(key)
        if rs is None:
            print("缓存未命中")
            # 查询大模型
            rs = self.speak(question, session_id)
            # 缓存结果
            client.set(key, rs, ex=120)
            return rs
        # 缓存命中
        print("缓存命中")
        return rs.decode()

def more_speak(questions: list, session_ids):
    agent = ChatAgent()
    with ThreadPoolExecutor(max_workers=5) as executor:
        rs = list(executor.map(agent.cache_speak, questions, session_ids))
        return rs
if __name__ == '__main__':
    more_speak(["生成一份张丽华的pdf病例报告"], ["userA"])