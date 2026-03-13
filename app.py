# -*- coding: utf-8 -*-
import os
from datetime import datetime, date

import streamlit as st

from bitable_client import (
    get_client,
    get_app_token,
    get_table_id,
    list_records,
    create_record,
    update_record,
    delete_record,
    batch_create_records,
    get_env,
)

# Streamlit 页面配置（移动端友好的宽布局）
st.set_page_config(
    page_title="考勤管理系统",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("考勤管理系统")

# 飞书客户端初始化（兼容本地 .env 和 Streamlit Cloud secrets）
try:
    client = get_client()
    APP_TOKEN = get_app_token()
    STUDENTS_TABLE_ID = get_table_id("BITABLE_TABLE_ID")
    ATTENDANCE_TABLE_ID = get_table_id("ATTENDANCE_TABLE_ID")
    
    # 检查是否配置完成
    if not APP_TOKEN or not STUDENTS_TABLE_ID or not ATTENDANCE_TABLE_ID:
        st.error("请先配置飞书多维表格信息！")
        st.info("本地开发请查看 .env.example 并创建 .env 文件")
        st.info("Streamlit Cloud 请在 Settings > Secrets 中配置")
        st.stop()
except Exception as e:
    st.error(f"初始化飞书客户端失败: {e}")
    st.stop()

# 创建三个功能标签页
tab_students, tab_attendance, tab_stats = st.tabs(["学生管理", "考勤记录", "查询统计"])

# ==================== 学生管理 ====================
with tab_students:
    st.header("学生管理")

    # 添加学生表单
    with st.expander("添加学生", expanded=False):
        with st.form("add_student_form"):
            name = st.text_input("姓名")
            submitted = st.form_submit_button("添加")
            if submitted:
                if not name.strip():
                    st.warning("请输入姓名")
                else:
                    try:
                        create_record(client, APP_TOKEN, STUDENTS_TABLE_ID, {
                            "姓名": name.strip(),
                        })
                        st.success(f"学生 {name} 添加成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"添加失败，请检查网络连接或飞书配置: {e}")

    # 显示学生列表
    try:
        students = list_records(client, APP_TOKEN, STUDENTS_TABLE_ID)
        if students:
            for s in students:
                fields = s["fields"]
                col1, col2 = st.columns([3, 1])
                col1.write(fields.get("姓名", ""))
                if col2.button("删除", key=f"del_{s['record_id']}"):
                    try:
                        delete_record(client, APP_TOKEN, STUDENTS_TABLE_ID, s["record_id"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"删除失败: {e}")
        else:
            st.info("暂无学生数据，请先添加学生。")
    except Exception as e:
        st.error(f"获取学生列表失败: {e}")

# ==================== 考勤记录 ====================
with tab_attendance:
    st.header("考勤记录")

    # 日期选择器
    selected_date = st.date_input("选择日期", value=date.today())
    date_timestamp = int(datetime.combine(selected_date, datetime.min.time()).timestamp()) * 1000

    # 显示学生列表并标记考勤
    try:
        students = list_records(client, APP_TOKEN, STUDENTS_TABLE_ID)
        if students:
            status_options = ["出勤", "缺勤", "迟到", "请假"]
            attendance_data = []

            for s in students:
                fields = s["fields"]
                col1, col2 = st.columns([3, 2])
                col1.write(f"**{fields.get('姓名', '')}**")
                status = col2.selectbox(
                    "状态",
                    status_options,
                    key=f"att_{s['record_id']}",
                    label_visibility="collapsed",
                )
                attendance_data.append({
                    "日期": date_timestamp,
                    "学生": fields.get("姓名", ""),
                    "状态": status,
                })

            if st.button("提交考勤记录"):
                try:
                    batch_create_records(client, APP_TOKEN, ATTENDANCE_TABLE_ID, attendance_data)
                    st.success(f"{selected_date} 考勤记录提交成功！")
                except Exception as e:
                    st.error(f"提交失败: {e}")
        else:
            st.info("暂无学生数据，请先在「学生管理」中添加学生。")
    except Exception as e:
        st.error(f"加载学生列表失败: {e}")

    # 显示已有考勤记录
    st.subheader("已有考勤记录")
    try:
        att_records = list_records(client, APP_TOKEN, ATTENDANCE_TABLE_ID)
        if att_records:
            for r in att_records:
                f = r["fields"]
                raw_date = f.get("日期", 0)
                if isinstance(raw_date, (int, float)) and raw_date > 0:
                    display_date = datetime.fromtimestamp(raw_date / 1000).strftime("%Y-%m-%d")
                else:
                    display_date = str(raw_date)
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                col1.write(display_date)
                col2.write(f.get("学生", ""))
                col3.write(f.get("状态", ""))
                if col4.button("删除", key=f"del_att_{r['record_id']}"):
                    try:
                        delete_record(client, APP_TOKEN, ATTENDANCE_TABLE_ID, r["record_id"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"删除考勤记录失败: {e}")
        else:
            st.info("暂无考勤记录。")
    except Exception as e:
        st.error(f"获取考勤记录失败: {e}")

# ==================== 查询统计 ====================
with tab_stats:
    st.header("查询统计")

    # 按日期范围查询
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("开始日期", value=date.today(), key="start")
    with col2:
        end_date = st.date_input("结束日期", value=date.today(), key="end")

    if st.button("查询"):
        try:
            records = list_records(client, APP_TOKEN, ATTENDANCE_TABLE_ID)
            start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp()) * 1000
            end_ts = int(datetime.combine(end_date, datetime.max.time()).timestamp()) * 1000

            filtered = [
                r for r in records
                if start_ts <= (r["fields"].get("日期", 0) or 0) <= end_ts
            ]

            if filtered:
                # 统计数据
                stats = {}
                for r in filtered:
                    student = r["fields"].get("学生", "未知")
                    status = r["fields"].get("状态", "未知")
                    stats.setdefault(student, {"出勤": 0, "缺勤": 0, "迟到": 0, "请假": 0})
                    if status in stats[student]:
                        stats[student][status] += 1

                # 显示统计表格
                import pandas as pd
                df = pd.DataFrame.from_dict(stats, orient="index")
                total = df.sum(axis=1)
                df["出勤率"] = (df["出勤"] / total * 100).round(1).astype(str) + "%"
                st.dataframe(df, use_container_width=True)

                # 显示详细记录
                with st.expander("详细记录"):
                    for r in filtered:
                        f = r["fields"]
                        st.write(f"- {f.get('学生', '')} | {f.get('状态', '')}")
            else:
                st.info("该日期范围内无考勤记录。")
        except Exception as e:
            st.error(f"查询失败: {e}")
