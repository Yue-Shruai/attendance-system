# -*- coding: utf-8 -*-
"""一次性运行脚本：创建飞书多维表格应用及数据表（学生信息表 + 考勤记录表）。

使用方法:
    1. 复制 .env.example 为 .env，填入 FEISHU_APP_ID 和 FEISHU_APP_SECRET
    2. 运行: python bitable_setup.py
    3. 脚本会输出 BITABLE_APP_TOKEN 及两张表的 TABLE_ID，请将它们填入 .env
"""

from bitable_client import (
    get_client,
    create_bitable_app,
    create_students_table,
    create_attendance_table,
)


def main():
    client = get_client()

    # 1. 创建多维表格应用
    print("正在创建多维表格应用...")
    app_info = create_bitable_app(client, name="考勤管理系统")
    app_token = app_info["app_token"]
    print(f"  应用创建成功!")
    print(f"  BITABLE_APP_TOKEN={app_token}")
    if app_info.get("url"):
        print(f"  URL: {app_info['url']}")

    # 2. 创建学生信息表
    print("\n正在创建学生信息表...")
    students_table_id = create_students_table(client, app_token)
    print(f"  学生信息表创建成功!")
    print(f"  STUDENTS_TABLE_ID={students_table_id}")

    # 3. 创建考勤记录表
    print("\n正在创建考勤记录表...")
    attendance_table_id = create_attendance_table(client, app_token)
    print(f"  考勤记录表创建成功!")
    print(f"  ATTENDANCE_TABLE_ID={attendance_table_id}")

    # 4. 汇总
    print("\n" + "=" * 50)
    print("设置完成！请将以下配置添加到 .env 文件中：")
    print("=" * 50)
    print(f"BITABLE_APP_TOKEN={app_token}")
    print(f"BITABLE_TABLE_ID={students_table_id}")
    print(f"ATTENDANCE_TABLE_ID={attendance_table_id}")
    print("=" * 50)


if __name__ == "__main__":
    main()
