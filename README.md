# MedBrain_Agent 医疗健康智能助手

MedBrain_Agent 是一个医疗健康领域的 AI 智能助手，采用**三服务架构**：Vue.js 前端、FastAPI 后端（LangChain 智能体）与 FastMCP 工具服务。通过聊天交互，为用户提供**医疗问诊咨询、用药提醒、健康管理**等一站式服务。

## 功能特性

- 🩺 **智能医疗问诊**：基于 LangChain Agent 路由分发，结合 MySQL 病历数据、Neo4j 医疗知识图谱、FAISS 向量检索（RAG）进行医疗问答。
- 💊 **用药提醒**：后台定时调度（60s 周期）检测服药时间，通过邮件自动发送用药提醒通知。
- 🎤 **语音识别**：基于 Vosk 的中文语音转文字（STT），支持语音输入问诊。
- 📧 **邮箱注册 / 登录**：支持邮箱验证码注册、登录流程，并可按邮箱检索患者个人信息。
- 📄 **医疗报告生成**：自动生成医疗报告 Word 文档。
- 🗺️ **高德地图服务**：接入高德 API，提供地理位置相关查询。
- 💬 **会话管理**：支持多会话、侧边栏聊天记录，可新建 / 切换 / 删除对话。
- 🖥️ **友好交互界面**：Vue 3 + Element Plus 单页应用，Markdown 渲染、代码高亮、打字指示器，医疗风格浅色主题。

## 系统架构

三服务架构：

```
Vue.js 前端 (8080) → FastAPI 后端 (8000) → MCP 服务 (8008)
                            ↓                        ↓
                      LangChain Agents          Tool 工具实现
                            ↓                        ↓
              MySQL / Neo4j / Redis / FAISS   Email / 高德 / 文档
```

| 模块 | 说明 |
| --- | --- |
| **前端** `frontend/` | Vue 3 + Element Plus + Vite SPA，路由：`/`（登录）、`/register`（注册）、`/chat`（聊天，需鉴权） |
| **后端** `backend/` | FastAPI 服务，承载三个 LangChain Agent，负责请求路由分发与业务编排 |
| **MCP 服务** `mcp-server/` | FastMCP 工具服务，通过 SSE 暴露数据库、邮件、RAG、定位、文档、用药提醒等工具 |

## Agent 路由

后端根据用户输入关键词将请求分发到不同 Agent：

- **ChatAgent**（`chat_agent.py`）：通用医疗问答。工具：SQL、Neo4j、FAISS（RAG）、高德、文档生成。
- **ChatAgentPatient**（`chat_agent_patient.py`）：患者相关查询（由 "邮箱" 关键词触发）。工具：SQL、邮件。
- **LoginAgent**（`login_agent.py`）：邮箱验证码的生成与发送。

## 目录结构

```
MedBrain_Agent/
├── backend/                    # FastAPI 后端 + LangChain Agents
│   ├── Agent/                  # 三个智能体（chat_agent / chat_agent_patient / login_agent）
│   ├── data/                   # 数据初始化脚本（Neo4j 知识图谱、MySQL 建库建表）
│   ├── model/                  # 模型管理与 VOSK 语音识别
│   ├── tool/                   # 工具层（SQL / Neo4j / FAISS / 高德 / 邮件 / 文档）
│   ├── utils/                  # 工具类（Redis 会话历史）
│   ├── mcp_test/               # MCP 调用测试脚本
│   └── main.py                 # FastAPI 入口（端口 8000）
├── mcp-server/                 # FastMCP 工具服务
│   └── mcp_service/
│       ├── amap_service/       # 高德定位服务
│       ├── count_service/      # 计数工具
│       ├── database_service/   # MySQL / Neo4j 数据服务
│       ├── email_service/      # 邮件服务
│       ├── file_service/       # 文档生成工具
│       ├── hello_service/      # 示例服务
│       ├── medication_service/ # 用药提醒定时调度器
│       ├── RAG_service/        # 向量检索（RAG）
│       └── server.py           # MCP 服务入口（端口 8008，HTTP/SSE）
├── frontend/                   # Vue 3 + Element Plus + Vite 前端
│   └── src/
│       ├── views/              # Chat.vue / Login.vue / Register.vue
│       ├── components/         # ChatSidebar / ChatMessage / ChatInput / TypingIndicator
│       ├── router/             # 路由配置
│       └── api/                # 接口封装
├── docs/                       # 技术文档
└── README.md
```

## 环境要求

- Python 3.12（建议使用 conda 环境）
- Node.js / npm（Node 18+）
- 本地服务：**MySQL、Neo4j、Redis**（启动后端和 MCP 服务前必须全部运行）

## 快速开始

> 首次运行前请先配置各服务所需的 `.env`，并完成数据初始化（见「配置说明」与「数据初始化」）。并确认本地已安装 **ffmpeg**（语音识别依赖）。

### 1. 数据初始化

```bash
cd backend/data
python 01-知识图谱数据初始化.py     # 填充 Neo4j 知识图谱
# 02-mysql数据初始化.sql 为 MySQL 建库建表脚本，在 MySQL 中执行
```

### 2. 启动 MCP 服务

```bash
cd mcp-server
pip install -r requirements.txt   # 首次运行安装依赖（或使用包管理工具）
python mcp_service/server.py      # MCP 服务，端口 8008（HTTP/SSE）
```

### 3. 启动后端

```bash
cd backend
python main.py                    # FastAPI 服务，端口 8000（uvicorn 自动重载）
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev                       # 开发服务器，localhost:8080
npm run build                     # 生产构建
```

## 配置说明

配置文件位于 `backend/.env` 与 `mcp-server/.env`，包含以下关键配置：

- **数据库**：MySQL（连接信息、连接池）、Neo4j、Redis
- **LLM**：后端使用 DeepSeek（OpenAI 兼容接口），MCP 服务使用 Qwen 2.5-72B（阿里云 DashScope，OpenAI 兼容接口）
- **词嵌入模型**：BAAI bge-large-zh-v1.5（本地加载）
- **语音识别模型**：Vosk 中文模型路径
- **邮件**：QQ 邮箱 SMTP（发件人、授权码）
- **高德**：高德地图 API Key

> 说明：真实 `.env` 文件含敏感凭据，已被 `.gitignore` 忽略，不会提交到仓库。可参考 `mcp-server/.env(脱敏)`（脱敏模板）配齐各字段后复制为对应服务的 `.env`。

模型文件（bge-large-zh-v1.5 权重等）体积较大，未纳入版本控制，需按 `.env` 中配置的路径自行下载。

### 数据库命名

| 服务 | 库名 | 说明 |
| --- | --- | --- |
| MySQL | `medbrain_agent` | 用户、患者、医生、病历、药品、处方、用药提醒等表 |
| Neo4j | `medbrain-graph` | 医生、患者、医院等节点及诊疗 / 工作 / 用药 / 转诊等关系 |

> Neo4j 库名（`medbrain-graph`）含连字符，在创建 / 删除该库时需使用反引号包裹：`CREATE DATABASE \`medbrain-graph\``。

## API 接口（后端 8000 端口）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/login` | 用户名/密码登录 |
| POST | `/chat` | 与医疗 Agent 聊天（`{message, session_id}`） |
| POST | `/send_code` | 发送邮箱验证码 |
| POST | `/code_verify` | 校验邮箱验证码 |
| POST | `/speech_to_text` | 语音文件转文字（multipart form） |

## 技术栈

- **后端**：Python 3.12、FastAPI、LangChain、FastMCP 2.x、Redis
- **前端**：Vue 3、Element Plus、Vite、Vue Router、Axios、Markdown
- **数据存储**：MySQL、Neo4j、Redis、FAISS
- **模型**：DeepSeek / Qwen 2.5-72B（OpenAI 兼容接口）、BAAI bge-large-zh-v1.5、Vosk
