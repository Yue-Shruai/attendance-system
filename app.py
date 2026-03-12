"""
考勤管理系统 - Streamlit 应用
功能：
1. 学生管理（添加/删除学生）
2. 考勤记录（选择日期，勾选学生签到）
3. 查询统计（选择学生、日期区间，显示上课次数）
4. 点击展开详情
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta

# ============ 页面配置 ============
st.set_page_config(
    page_title="考勤管理系统",
    page_icon="📋",
    layout="wide"  # 手机友好
)

# ============ 数据存储文件 ============
DATA_FILE = "attendance_data.json"

# ============ 初始化数据 ============
def load_data():
    """加载数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"students": [], "attendance": []}

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============ 主界面 ============
def main():
    st.title("📋 考勤管理系统")
    
    # 加载数据
    data = load_data()
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["👥 学生管理", "📝 考勤记录", "🔍 查询统计"])
    
    # ============ 学生管理 ============
    with tab1:
        st.subheader("添加学生")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_student = st.text_input("学生姓名", placeholder="输入姓名")
        with col2:
            if st.button("添加", use_container_width=True):
                if new_student and new_student not in data["students"]:
                    data["students"].append(new_student)
                    save_data(data)
                    st.success(f"添加成功: {new_student}")
                    st.rerun()
        
        # 显示学生列表
        st.subheader(f"学生列表 ({len(data['students'])}人)")
        if data["students"]:
            for i, student in enumerate(data["students"]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {student}")
                with col2:
                    if st.button("删除", key=f"del_{i}", use_container_width=True):
                        data["students"].remove(student)
                        save_data(data)
                        st.rerun()
        else:
            st.info("暂无学生，请添加")
    
    # ============ 考勤记录 ============
    with tab2:
        st.subheader("记录考勤")
        
        if not data["students"]:
            st.warning("请先添加学生")
        else:
            # 选择日期
            selected_date = st.date_input("选择日期", value=datetime.now())
            
            # 勾选学生
            st.write("勾选到课学生：")
            selected_students = []
            for student in data["students"]:
                if st.checkbox(student, key=f"att_{student}"):
                    selected_students.append(student)
            
            # 保存
            if st.button("保存考勤记录", use_container_width=True):
                if selected_students:
                    # 检查是否已存在该日期的记录
                    existing_idx = None
                    for idx, record in enumerate(data["attendance"]):
                        if record["date"] == str(selected_date):
                            existing_idx = idx
                            break
                    
                    if existing_idx is not None:
                        # 更新已有记录
                        data["attendance"][existing_idx]["students"] = selected_students
                    else:
                        # 添加新记录
                        data["attendance"].append({
                            "date": str(selected_date),
                            "students": selected_students
                        })
                    
                    save_data(data)
                    st.success(f"已保存 {len(selected_students)} 人的考勤记录")
                else:
                    st.warning("请至少选择一个学生")
    
    # ============ 查询统计 ============
    with tab3:
        st.subheader("查询统计")
        
        if not data["students"]:
            st.warning("暂无数据")
        else:
            # 选择学生
            selected_student = st.selectbox("选择学生", ["请选择"] + data["students"])
            
            # 选择日期区间
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("开始日期", value=datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("结束日期", value=datetime.now())
            
            # 查询
            if st.button("查询", use_container_width=True):
                if selected_student != "请选择":
                    # 统计
                    count = 0
                    dates = []
                    for record in data["attendance"]:
                        record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
                        if start_date <= record_date <= end_date:
                            if selected_student in record["students"]:
                                count += 1
                                dates.append(record["date"])
                    
                    # 显示结果
                    st.info(f"{selected_student} 在该期间共上课 {count} 次")
                    
                    # 详情（可展开）
                    with st.expander("查看详细日期"):
                        if dates:
                            for d in sorted(dates):
                                st.write(f"• {d}")
                        else:
                            st.write("无记录")
                else:
                    st.warning("请选择学生")

if __name__ == "__main__":
    main()