from concurrent.futures.thread import ThreadPoolExecutor
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from tool.sql_tool_pool import sql_tool_pool
from tool.email_tool import send_email_tool
from model.model_management import MyModel

class LoginAgent:
    # 创建一个智能体对象
    _agent = None

    # 初始化操作
    def __init__(self):
        # 创建一个模型对象
        chat = MyModel()
        self.llm = chat.get_line_model()
        # 创建一个智能体
        self._agent = self.create_agent()

    # 创建一个智能体对象
    def create_agent(self):
        # 1 创建工具列表
        tools = [sql_tool_pool, send_email_tool]
        # 2 创建提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个ai助手，你有两个工具：
            
                       1 sql_tool_pool sql 查询工具
                      数据库表的结构信息是以下信息：
                        user_info - 用户信息表
                           user_id 用户编号，user_name 用户名,password 密码,email 邮箱
                        注意：
                          请返回以下数据格式：{{userId:1,userName:'张三',email:'3333@qq.com'}},其他文本信息不需要
                          如果没有查询到数据，请返回0
                          
                       2 send_email_tool 邮箱发送工具
                       提示：邮件地址没有空格
                       请按照以下步骤执行：
                       1. 生成一个4位数的随机数作为正文的验证码发送(验证码尽量每次不重样)
                       2. 只返回以下信息:xxxx
                       """

                       ),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        # 3 创建智能体
        agent = create_tool_calling_agent(llm=self.llm, tools=tools, prompt=prompt)
        # 4 创建智能体执行器
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor

    # 对话函数
    def speak(self, question: str):
        res = self._agent.invoke({"input": question})
        return res["output"]


# 定义一个并行优化的函数，单独执行的函数
def more_speak_login(questions: list):
    agent = LoginAgent()
    with ThreadPoolExecutor(max_workers=5) as executor:
        rs = list(executor.map(agent.speak, questions))
    return rs


if __name__ == '__main__':
    # agent = ChatAgent()
    # q1 = "陈志强的薪水是多少"
    # q2 = "张明在那个医院工作"
    # print(agent.cache_speak(q2, "2"))
    questions = [
        # "请查询用户信息表，条件是用户名是rock22，密码是1234的用户信息",
        "请给邮箱1103254414@qq.com发送一封邮件，主题是: xxxx公司登录验证码，内容: 你当前的验证码为"
    ]
    rs = more_speak_login(questions)
    print("答案是：")
    print(rs[0])
    print(type(rs[0]))



