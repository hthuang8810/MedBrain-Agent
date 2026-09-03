from concurrent.futures.thread import ThreadPoolExecutor
from model.model_management import MyModel
from tool.sql_tool_pool import sql_tool_pool
from tool.email_tool import send_email_tool
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from utils.inMemoryHistory_redis import get_session_history
import hashlib
import redis

# 连接redis
client = redis.Redis(host='localhost', port=6379, db=0, protocol=2)  # protocol=2: 兼容 Redis<6,避免 HELLO 命令

class ChatAgentPatient:
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
        tools = [sql_tool_pool, send_email_tool]
        # 创建提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system","""
            你是一个医疗助手，你有两个查询工具:
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
            
            "2 send_email_tool 邮件发送工具"
            重要：请严格按照以下步骤执行：
            1 : 请用工具 sql_tool_pool 查询病人的病历信息
            2. 组织语言生成标准化报告.
            报告格式如下：
            病人基本信息:
            - 姓名: 李四
            - 性别: 男
            - 年龄: 40岁 (出生日期: 1985年10月12日)
            - 身份证号: 110101198510123456
            - 联系电话: 13900139001
            - 紧急联系人: 李小红
            - 血型: A型

            最近就诊记录:
            - 主诉: 胸闷、心悸3天
            - 诊断结果: 冠心病
            - 治疗方案: 药物治疗，定期复查
            - 就诊日期: 2025年10月25日
            - 复诊日期: 2025年10月26日
            - 诊疗费用: ￥350.00
            初步诊断建议：
            - xxx
            3: 请查询病人的邮箱
            4：请把报告发送到病人的邮箱里  
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

# 定义一个并行优化的函数，单独执行的函数
def more_speak_patient(questions: list, session_ids: list):
    agent = ChatAgentPatient()
    with ThreadPoolExecutor(max_workers=5) as executor:
        rs = list(executor.map(agent.cache_speak, questions, session_ids))
    return rs

if __name__ == '__main__':
    questions = [
        "写一份张丽华病例报告，并把报告发送到病人的邮箱里",
    ]
    session_ids = [
        "1"
    ]
    rs = more_speak_patient(questions, session_ids)
    print("答案是：")
    print(rs)
