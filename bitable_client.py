# -*- coding: utf-8 -*-
"""飞书多维表格客户端封装，提供考勤系统所需的 CRUD 操作。"""

import os
import streamlit as st
from dotenv import load_dotenv
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

# 优先从 Streamlit secrets 读取（用于 Streamlit Cloud）
# 如果不存在则从环境变量读取（用于本地开发）
def get_env(key: str, default: str = "") -> str:
    # Streamlit Cloud 方式
    if hasattr(st, 'secrets'):
        try:
            return st.secrets[key]
        except:
            pass
    # 本地环境变量方式
    return os.getenv(key, default)

load_dotenv()


def get_client() -> lark.Client:
    """创建并返回飞书客户端实例。"""
    app_id = get_env("FEISHU_APP_ID")
    app_secret = get_env("FEISHU_APP_SECRET")
    return (
        lark.Client.builder()
        .app_id(app_id)
        .app_secret(app_secret)
        .build()
    )


def get_app_token() -> str:
    return get_env("BITABLE_APP_TOKEN")


def get_table_id(key: str = "BITABLE_TABLE_ID") -> str:
    return get_env(key)


# ---------------------------------------------------------------------------
# 多维表格 / App 创建
# ---------------------------------------------------------------------------

def create_bitable_app(client: lark.Client, name: str = "考勤管理系统") -> dict:
    """创建一个新的多维表格应用，返回 app_token 等信息。"""
    from lark_oapi.api.bitable.v1 import ReqApp, ReqAppBuilder
    
    # 使用 ReqAppBuilder 构建请求体（直接调用而非 builder()）
    app_body = ReqAppBuilder().name(name).build()
    
    # 构建创建请求
    request = (
        CreateAppRequest.builder()
        .request_body(app_body)
        .build()
    )
    
    resp = client.bitable.v1.app.create(request)
    if not resp.success():
        raise Exception(f"创建多维表格失败: {resp.code} - {resp.msg}")
    app = resp.data.app
    return {"app_token": app.app_token, "name": app.name, "url": app.url}


# ---------------------------------------------------------------------------
# 数据表创建
# ---------------------------------------------------------------------------

STUDENTS_TABLE_FIELDS = [
    {"field_name": "姓名", "type": 1},   # 1 = 文本
    {"field_name": "学号", "type": 1},   # 1 = 文本
    {"field_name": "班级", "type": 1},   # 1 = 文本
]

ATTENDANCE_TABLE_FIELDS = [
    {"field_name": "日期", "type": 5},   # 5 = 日期
    {"field_name": "学生", "type": 1},   # 1 = 文本
    {
        "field_name": "状态",
        "type": 3,                        # 3 = 单选
        "property": {
            "options": [
                {"name": "出勤"},
                {"name": "缺勤"},
                {"name": "迟到"},
                {"name": "请假"},
            ]
        },
    },
]


def create_table(
    client: lark.Client,
    app_token: str,
    table_name: str,
    fields: list[dict],
) -> str:
    """在指定多维表格中创建数据表，返回 table_id。"""
    request_fields = []
    for f in fields:
        builder = AppTableCreateHeader.builder().field_name(f["field_name"]).type(f["type"])
        if "property" in f:
            builder = builder.property(f["property"])
        request_fields.append(builder.build())

    table = (
        ReqTable.builder()
        .name(table_name)
        .default_view_name(f"{table_name}视图")
        .fields(request_fields)
        .build()
    )
    request = (
        CreateAppTableRequest.builder()
        .app_token(app_token)
        .request_body(
            CreateAppTableRequestBody.builder().table(table).build()
        )
        .build()
    )
    resp = client.bitable.v1.app_table.create(request)
    if not resp.success():
        raise Exception(f"创建数据表 [{table_name}] 失败: {resp.code} - {resp.msg}")
    return resp.data.table_id


def create_students_table(client: lark.Client, app_token: str) -> str:
    """创建学生信息表，返回 table_id。"""
    return create_table(client, app_token, "学生信息", STUDENTS_TABLE_FIELDS)


def create_attendance_table(client: lark.Client, app_token: str) -> str:
    """创建考勤记录表，返回 table_id。"""
    return create_table(client, app_token, "考勤记录", ATTENDANCE_TABLE_FIELDS)


# ---------------------------------------------------------------------------
# 记录 CRUD
# ---------------------------------------------------------------------------

def list_records(
    client: lark.Client,
    app_token: str,
    table_id: str,
    filter_expr: str | None = None,
    page_size: int = 100,
) -> list[dict]:
    """查询数据表中的记录列表。"""
    builder = (
        ListAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .page_size(page_size)
    )
    if filter_expr:
        builder = builder.filter(filter_expr)
    request = builder.build()
    resp = client.bitable.v1.app_table_record.list(request)
    if not resp.success():
        raise Exception(f"查询记录失败: {resp.code} - {resp.msg}")
    items = resp.data.items or []
    return [{"record_id": r.record_id, "fields": r.fields} for r in items]


def create_record(
    client: lark.Client,
    app_token: str,
    table_id: str,
    fields: dict,
) -> str:
    """向数据表插入一条记录，返回 record_id。"""
    request = (
        CreateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .request_body(
            AppTableRecord.builder().fields(fields).build()
        )
        .build()
    )
    resp = client.bitable.v1.app_table_record.create(request)
    if not resp.success():
        raise Exception(f"创建记录失败: {resp.code} - {resp.msg}")
    return resp.data.record.record_id


def batch_create_records(
    client: lark.Client,
    app_token: str,
    table_id: str,
    records: list[dict],
) -> list[str]:
    """批量插入记录，records 为 fields dict 列表，返回 record_id 列表。"""
    app_records = [
        AppTableRecord.builder().fields(r).build() for r in records
    ]
    request = (
        BatchCreateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .request_body(
            BatchCreateAppTableRecordRequestBody.builder()
            .records(app_records)
            .build()
        )
        .build()
    )
    resp = client.bitable.v1.app_table_record.batch_create(request)
    if not resp.success():
        raise Exception(f"批量创建记录失败: {resp.code} - {resp.msg}")
    return [r.record_id for r in (resp.data.records or [])]


def update_record(
    client: lark.Client,
    app_token: str,
    table_id: str,
    record_id: str,
    fields: dict,
) -> None:
    """更新一条记录。"""
    request = (
        UpdateAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(record_id)
        .request_body(
            AppTableRecord.builder().fields(fields).build()
        )
        .build()
    )
    resp = client.bitable.v1.app_table_record.update(request)
    if not resp.success():
        raise Exception(f"更新记录失败: {resp.code} - {resp.msg}")


def delete_record(
    client: lark.Client,
    app_token: str,
    table_id: str,
    record_id: str,
) -> None:
    """删除一条记录。"""
    request = (
        DeleteAppTableRecordRequest.builder()
        .app_token(app_token)
        .table_id(table_id)
        .record_id(record_id)
        .build()
    )
    resp = client.bitable.v1.app_table_record.delete(request)
    if not resp.success():
        raise Exception(f"删除记录失败: {resp.code} - {resp.msg}")
