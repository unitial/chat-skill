# 手动安装指南

如果 `quickstart.sh` 脚本遇到问题，请按照以下步骤手动安装。

## 方法 1: 使用虚拟环境（推荐）

### 步骤 1: 检查 Python 版本

```bash
python3 --version
# 应该是 Python 3.10 或更高版本
```

### 步骤 2: 安装 python3-venv（如果需要）

如果创建虚拟环境失败，可能需要安装 venv 模块：

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-venv
```

**RHEL/CentOS:**
```bash
sudo yum install python3-venv
```

### 步骤 3: 创建虚拟环境

```bash
cd claude-skill-chat
python3 -m venv venv
```

### 步骤 4: 激活虚拟环境

```bash
source venv/bin/activate
```

你应该看到命令提示符前面出现 `(venv)`。

### 步骤 5: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 6: 安装项目

```bash
pip install -e .
```

### 步骤 7: 设置 DeepSeek API Key

```bash
export DEEPSEEK_API_KEY='your-deepseek-key-here'
```

### 步骤 8: 运行

```bash
chat-with-skills --skills-dir ./demo_skills --show-routing
```

## 方法 2: 全局安装（不推荐）

如果你确实想全局安装（不使用虚拟环境）：

```bash
# 使用 --user 标志
pip install --user -r requirements.txt
pip install --user -e .

# 确保 ~/.local/bin 在 PATH 中
export PATH="$HOME/.local/bin:$PATH"

# 设置 API Key
export DEEPSEEK_API_KEY='your-key'

# 运行
chat-with-skills --skills-dir ./demo_skills --show-routing
```

## 方法 3: 使用 --break-system-packages（不推荐）

**警告**: 这可能会破坏系统 Python 包。仅在你了解风险的情况下使用。

```bash
pip install --break-system-packages -r requirements.txt
pip install --break-system-packages -e .
```

## 常见问题排查

### 问题 1: "command not found: chat-with-skills"

**原因**: 命令没有在 PATH 中

**解决方案**:
```bash
# 如果使用虚拟环境，确保已激活
source venv/bin/activate

# 如果使用 --user 安装，添加到 PATH
export PATH="$HOME/.local/bin:$PATH"

# 或者直接运行
python3 -m skill_chat.cli --skills-dir ./demo_skills --show-routing
```

### 问题 2: "No module named 'agentscope'"

**原因**: 依赖没有安装成功

**解决方案**:
```bash
# 重新安装依赖
pip install agentscope pydantic click rich

# 然后安装项目
pip install -e .
```

### 问题 3: 虚拟环境创建失败

**原因**: 缺少 python3-venv 包

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# 然后重试
python3 -m venv venv
```

### 问题 4: "This environment is externally managed"

**原因**: 系统 Python 由包管理器管理

**解决方案**: 必须使用虚拟环境（方法 1）或 --user 标志（方法 2）

### 问题 5: pip 版本太旧

**原因**: pip 版本过旧

**解决方案**:
```bash
# 在虚拟环境中升级 pip
python3 -m pip install --upgrade pip
```

## 验证安装

运行验证脚本检查安装：

```bash
python3 verify.py
```

## 获取帮助

```bash
chat-with-skills --help
```

## 完整示例（从头开始）

```bash
# 1. 进入项目目录
cd claude-skill-chat

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 升级 pip
pip install --upgrade pip

# 5. 安装依赖
pip install -r requirements.txt

# 6. 安装项目
pip install -e .

# 7. 设置 API Key
export DEEPSEEK_API_KEY='sk-your-key-here'

# 8. 运行
chat-with-skills --skills-dir ./demo_skills --show-routing

# 9. 完成后退出虚拟环境
deactivate
```

## 下次使用

虚拟环境创建后，以后只需：

```bash
cd claude-skill-chat
source venv/bin/activate
export DEEPSEEK_API_KEY='your-key'
chat-with-skills --skills-dir ./demo_skills --show-routing
```

## 永久设置 API Key

编辑 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export DEEPSEEK_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## 使用 .env 文件

```bash
# 复制模板
cp .env.example .env

# 编辑文件
nano .env

# 在 .env 中设置：
DEEPSEEK_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.deepseek.com/v1
CHAT_MODEL=deepseek-chat
ROUTER_MODEL=deepseek-chat

# 然后运行时会自动读取
```
