# 考勤管理系统

基于 Streamlit 和飞书多维表格的考勤管理系统，支持学生管理、考勤记录和查询统计功能。

## 功能特性

- **学生管理** - 添加、编辑、删除学生信息
- **考勤记录** - 快速记录学生出勤状态（出勤/缺勤/迟到/请假）
- **查询统计** - 按日期、学生查询考勤记录，生成统计报表
- **云端存储** - 数据存储在飞书多维表格（Bitable），多端同步

## 技术栈

- **前端界面**: Streamlit（支持移动端访问）
- **数据存储**: 飞书多维表格（Bitable）
- **API 接入**: lark-oapi（飞书开放平台 SDK）
- **配置管理**: python-dotenv

## 安装与使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
FEISHU_APP_ID=你的飞书应用ID
FEISHU_APP_SECRET=你的飞书应用密钥
BITABLE_APP_TOKEN=多维表格的app_token
BITABLE_TABLE_ID=数据表的table_id
```

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器访问 `http://localhost:8501` 即可使用。
