# ✅ 修复完成！现在可以使用了

## 问题已解决

已修复 AgentScope 1.0.12 兼容性问题：
- ✅ 修正了 `agentscope.agents` → `agentscope.agent` 导入
- ✅ 修正了 `TemporaryMemory` → `InMemoryMemory`

## 立即开始使用

### 方式 1: 一键运行（推荐）

```bash
# 在项目目录中
./run.sh
```

脚本会：
- 自动激活虚拟环境
- 检查 API key（如果没有会提示输入）
- 启动聊天界面

### 方式 2: 手动运行

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 设置 API Key（如果还没设置）
export DEEPSEEK_API_KEY='sk-your-key-here'

# 3. 运行
chat-with-skills --skills-dir ./demo_skills --show-routing
```

### 方式 3: 永久设置（推荐）

将 API key 添加到你的 shell 配置：

```bash
# 对于 zsh
echo 'export DEEPSEEK_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc

# 对于 bash
echo 'export DEEPSEEK_API_KEY="sk-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

然后就可以直接运行：
```bash
./run.sh
```

## 获取 DeepSeek API Key

1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制并设置到环境变量

## 可用的命令

在聊天界面中：
- 输入消息并按 Enter - 开始对话
- `exit` 或 `quit` - 退出程序
- `reset` - 清除对话历史

命令行选项：
```bash
chat-with-skills --help  # 查看所有选项
```

## 常用配置

```bash
# 使用不同的模型
chat-with-skills --chat-model deepseek-coder --router-model deepseek-chat --skills-dir ./demo_skills

# 关闭路由显示
chat-with-skills --no-show-routing --skills-dir ./demo_skills

# 限制最大技能数量
chat-with-skills --max-skills 2 --skills-dir ./demo_skills --show-routing
```

## 故障排除

### 如果遇到 "command not found"

确保已激活虚拟环境：
```bash
source venv/bin/activate
```

### 如果遇到 "No module named"

重新安装：
```bash
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 如果遇到 API 错误

检查 API key 是否正确：
```bash
echo $DEEPSEEK_API_KEY
```

## 技术支持

- 问题报告: https://github.com/anthropics/claude-code/issues
- 文档: 查看 README.md, EXAMPLES.md, MANUAL_INSTALL.md
