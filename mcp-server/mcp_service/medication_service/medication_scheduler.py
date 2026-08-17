# medication_scheduler.py
import asyncio
import datetime
import json
from fastmcp import Client

DEBUG_MODE = False      # 调试模式，启动立即发送测试邮件
CHECK_INTERVAL = 60     # 每分钟检查一次
TIME_WINDOW = 1         # ±1分钟内发送


async def send_medication_reminders():
    """
    定时检查数据库中的用药提醒，并发送邮件
    """
    async with Client("http://localhost:8008/sse") as client:
        try:
            query = """
            SELECT mr.id, mr.patient_id, mr.drug_name, mr.dosage, 
                   mr.reminder_time, mr.last_sent_at, p.email
            FROM medication_reminder mr
            JOIN patients p ON mr.patient_id = p.id
            WHERE mr.status = 'active';
            """
            rs = await client.call_tool("sql_tool_pool", {"query": query})
            data_str = rs.data.strip()

            print("原始返回数据:", data_str)

            if not data_str or "失败" in data_str:
                print("SQL 查询失败或无结果")
                return []

            try:
                plans_list = json.loads(data_str)
            except:
                try:
                    plans_list = eval(data_str)
                except:
                    plans_list = []

            reminders_to_send = []
            now = datetime.datetime.now()
            now_time = now.time()

            for plan in plans_list:
                email = plan.get("email")
                if not email:
                    continue

                # 获取 reminder_time
                reminder_times = []
                if DEBUG_MODE:
                    reminder_times = ["DEBUG"]
                else:
                    rt = plan.get("reminder_time")
                    if rt:
                        reminder_times = [rt]

                for r_time in reminder_times:
                    send_now = False
                    if DEBUG_MODE:
                        send_now = True
                    else:
                        try:
                            target_time = datetime.datetime.strptime(r_time, "%H:%M:%S").time()
                            diff_seconds = (datetime.datetime.combine(now.date(), now_time) -
                                            datetime.datetime.combine(now.date(), target_time)).total_seconds()
                            if abs(diff_seconds) <= TIME_WINDOW * 60:
                                send_now = True
                        except Exception as e:
                            print("[WARN] reminder_time 格式解析错误:", r_time, e)
                            continue

                    if send_now:
                        message = f"您的用药提醒：{plan['drug_name']}，剂量：{plan['dosage']}，时间：{r_time}"
                        result = await client.call_tool("send_email_tool", {
                            "to_email": email,
                            "subject": "用药提醒",
                            "content": message
                        })
                        print(f"[INFO] 向 {email} 发送提醒: {message}")
                        print(f"[DEBUG] 邮件发送结果: {result}")

                        reminders_to_send.append({
                            "drug_name": plan['drug_name'],
                            "dosage": plan['dosage'],
                            "reminder_time": r_time,
                            "message": message
                        })

                        # 更新 last_sent_at
                        update_query = f"""
                        UPDATE medication_reminder
                        SET last_sent_at = NOW()
                        WHERE id = {plan['id']};
                        """
                        try:
                            update_rs = await client.call_tool("sql_tool_pool", {"query": update_query})
                            print(f"[DEBUG] 更新 last_sent_at 结果: {update_rs.data}")
                        except Exception as e:
                            print("[ERROR] 更新 last_sent_at 异常:", e)

            return reminders_to_send

        except Exception as e:
            print("检查用药提醒异常:", e)
            return []


async def scheduler_loop():
    """
    调度器主循环，每 CHECK_INTERVAL 秒检查一次提醒
    """
    print("用药提醒调度器启动...")
    if DEBUG_MODE:
        print("DEBUG_MODE: 立即尝试发送一次提醒")
        await send_medication_reminders()

    while True:
        try:
            await send_medication_reminders()
        except Exception as e:
            print("检查用药提醒异常:", e)
        await asyncio.sleep(CHECK_INTERVAL)