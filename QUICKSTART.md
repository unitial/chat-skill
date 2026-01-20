# 🚀 完全修复！立即可用

## ✅ 所有问题已解决

1. ✅ AgentScope 1.0.12 API 完全适配
2. ✅ 异步 API 正确处理
3. ✅ SOCKS 代理支持
4. ✅ 虚拟环境配置

## 立即开始（2 步）

### 1. 设置 DeepSeek API Key

```bash
export DEEPSEEK_API_KEY='sk-your-key-here'
```

### 2. 运行

```bash
./run.sh
```

就这么简单！🎉

## 获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com/
2. 注册/登录
3. 创建 API Key
4. 复制 key（格式: sk-...）

## 完整示例

```bash
# 1. 设置 key
export DEEPSEEK_API_KEY='sk-xxxxx'

# 2. 运行
./run.sh

# 3. 开始对话
You: 帮我创建一个 8 周的 Python 课程大纲

# 系统会自动：
# - 检测查询类型
# - 选择相关技能（Course Outline）
# - 注入技能上下文
# - 生成结构化回复
```

## 聊天命令

- 输入消息 + Enter → 对话
- `exit` 或 `quit` → 退出
- `reset` → 清除历史

## 技能示例

### ✅ 触发技能

- "帮我创建课程大纲"
- "总结这个 PDF"
- "评审这篇论文"

### 💬 普通聊天

- "你好"
- "今天天气怎么样"

## 永久设置 API Key

```bash
# 对于 zsh (推荐)
echo 'export DEEPSEEK_API_KEY="sk-your-key"' >> ~/.zshrc
source ~/.zshrc

# 对于 bash
echo 'export DEEPSEEK_API_KEY="sk-your-key"' >> ~/.bashrc
source ~/.bashrc
```

然后就可以直接运行 `./run.sh`，不需要每次设置！

## 高级用法

```bash
# 显示路由决策
chat-with-skills --skills-dir ./demo_skills --show-routing

# 使用不同模型
chat-with-skills --chat-model deepseek-coder --router-model deepseek-chat --skills-dir ./demo_skills

# 限制技能数量
chat-with-skills --max-skills 2 --skills-dir ./demo_skills --show-routing

# 查看所有选项
chat-with-skills --help
```

## 故障排除

### "command not found"

```bash
source venv/bin/activate
./run.sh
```

### "No API key provided"

```bash
export DEEPSEEK_API_KEY='your-key'
```

### 代理用户

如果使用 SOCKS/HTTP 代理，已自动支持，无需额外配置！

### 其他错误

```bash
# 查看详细错误
DEBUG=1 ./run.sh
```

## 技术文档

- `ASYNC_API_FIX.md` - 异步 API 修复详情
- `AGENTSCOPE_1.0.12_MIGRATION.md` - 完整迁移指南
- `README.md` - 完整文档
- `EXAMPLES.md` - 使用示例

## 完整功能列表

✅ 智能技能路由（JSON 严格校验）
✅ 技能内容安全注入
✅ 对话历史管理
✅ Rich 格式化输出
✅ 异步 API 支持
✅ SOCKS 代理支持
✅ 支持 DeepSeek/OpenAI/Ollama
✅ 3 个演示技能

## 演示技能

1. **PDF Summary** - PDF 文档总结框架
2. **Paper Review** - 学术论文评审模板
3. **Course Outline** - 课程大纲生成指南

## 立即测试

```bash
./run.sh
```

开始享受技能感知的 AI 对话！🚀
