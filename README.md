# 🤖 AI多智能体讨论系统

一个基于AutoGen的多智能体讨论系统，让哲学家、科学家、艺术家三位AI从不同角度展开思想碰撞。

## ✨ 特性

- 🧙 **三位AI智能体**：哲学家、科学家、艺术家，各自从专业角度发表观点
- 🔍 **实时搜索**：智能体可以调用DuckDuckGo搜索获取真实资料
- 💬 **实时对话流**：通过WebSocket实时推送讨论进展
- 📚 **讨论历史**：所有讨论都保存在本地SQLite数据库
- 🎨 **现代UI**：React前端，清爽的聊天界面

## 🏗️ 技术栈

### 后端
- **FastAPI** - 高性能Web框架
- **AutoGen** - 多智能体编排框架
- **SQLAlchemy** - ORM数据库管理
- **WebSocket** - 实时通信
- **DuckDuckGo Search** - 搜索引擎API

### 前端
- **React** - UI框架
- **Axios** - HTTP客户端
- **WebSocket** - 实时消息接收

### 数据库
- **SQLite** - 轻量级本地数据库

## 📦 安装和启动

### 前置要求
- Python 3.9+
- Node.js 16+
- npm 或 yarn
- OpenAI API Key

### 1. 克隆项目（如果是从git获取）

```bash
cd multi-ai
```

### 2. 配置环境变量

复制示例配置文件并填入你的OpenAI API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# 服务器配置
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=3000

# 数据库配置
DATABASE_PATH=./backend/discussions.db
```

**⚠️ 重要安全提示**：
- **立即删除test.py中的硬编码API密钥**（第70行）
- 前往 [OpenAI Platform](https://platform.openai.com/api-keys) 删除泄露的密钥
- 生成新的API密钥并配置到 `.env` 文件
- **绝不**要将 `.env` 文件提交到Git

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

或使用虚拟环境（推荐）：

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows使用: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 5. 启动应用

#### 方法一：分别启动（推荐用于开发）

**启动后端**（新终端窗口）：
```bash
cd backend
python main.py
```

后端将运行在 `http://localhost:8000`

**启动前端**（新终端窗口）：
```bash
cd frontend
npm start
```

前端将运行在 `http://localhost:3000` 并自动打开浏览器

#### 方法二：使用启动脚本（可选）

创建一个启动脚本 `start.sh`（macOS/Linux）：

```bash
#!/bin/bash
cd backend && python main.py &
cd frontend && npm start &
wait
```

## 🎯 使用方法

1. 打开浏览器访问 `http://localhost:3000`
2. 在输入框中输入讨论主题，例如：
   - "什么是真实？"
   - "AI会取代人类吗？"
   - "黑客松的评选标准应该是什么？"
3. 点击"开始讨论"按钮
4. 观看三位AI智能体从哲学、科学、艺术角度展开讨论
5. 左侧可以查看讨论历史记录

## 📁 项目结构

```
multi-ai/
├── backend/                 # Python后端
│   ├── main.py             # FastAPI入口
│   ├── agents.py           # AutoGen多智能体逻辑
│   ├── database.py         # SQLite数据库模型
│   ├── requirements.txt    # Python依赖
│   └── discussions.db      # SQLite数据库（运行后生成）
├── frontend/               # React前端
│   ├── src/
│   │   ├── App.js         # 主应用组件
│   │   └── App.css        # 样式文件
│   ├── public/
│   └── package.json       # Node.js依赖
├── .env                    # 环境变量（需自行创建）
├── .env.example           # 环境变量示例
├── .gitignore             # Git忽略文件
├── test.py                # 原始命令行版本（已废弃）
└── README.md              # 本文件
```

## 🔧 API接口

### REST API

- `GET /` - 健康检查
- `POST /discussions` - 创建新讨论
- `GET /discussions` - 获取讨论列表
- `GET /discussions/{id}` - 获取单个讨论
- `GET /discussions/{id}/messages` - 获取讨论消息

### WebSocket

- `WS /ws/discuss/{discussion_id}` - 实时讨论通信

## 🐛 常见问题

### 后端无法启动

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决**：
```bash
cd backend
pip install -r requirements.txt
```

### 前端无法连接后端

**问题**：前端显示"连接错误，请检查后端是否运行"

**解决**：
1. 确认后端已启动：访问 `http://localhost:8000`
2. 检查CORS配置（已在代码中配置）
3. 检查端口是否被占用

### OpenAI API错误

**问题**：`AuthenticationError` 或 `Rate limit exceeded`

**解决**：
1. 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
2. 确认OpenAI账户有余额
3. 如果超过速率限制，等待几分钟后重试

### 讨论没有实时更新

**问题**：消息不实时显示

**原因**：当前版本的消息拦截机制是临时实现，AutoGen的输出需要更深度集成

**临时解决方案**：讨论完成后刷新页面查看完整历史

## 🚀 后续优化建议

1. **消息实时推送优化**
   - 当前：AutoGen是同步执行，消息拦截较困难
   - 改进：实现AutoGen的消息钩子或使用流式输出

2. **用户交互增强**
   - 允许用户中途加入讨论
   - 支持自定义AI角色和人设
   - 调整讨论轮数和搜索策略

3. **部署优化**
   - Docker容器化
   - 使用PostgreSQL替代SQLite
   - 添加用户认证系统

4. **性能优化**
   - 异步处理讨论任务
   - 缓存搜索结果
   - 消息分页加载

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**警告**：请务必保护好你的OpenAI API密钥，不要泄露到公共代码仓库！
