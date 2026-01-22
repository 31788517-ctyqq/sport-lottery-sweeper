"""
通知发送任务
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from celery import Task
from backend.tasks import DatabaseTask, celery_app
from backend.services.notification_service import NotificationService
from backend.config import settings
from backend.api.websocket import notify_system_message


class NotificationTask(Task):
    def __init__(self):
        self.notification_service = NotificationService()


@celery_app.task(base=NotificationTask, bind=True)
def send_notification_task(self, message: str, user_id: str = None):
    """发送通知任务"""
    result = self.notification_service.send_notification(message, user_id)
    return result


logger = logging.getLogger(__name__)

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.notification_tasks.send_email_notification")
def send_email_notification(self, to_email: str, subject: str, content: str, 
                           content_type: str = "html"):
    """
    发送邮件通知任务
    
    Args:
        to_email: 收件人邮箱
        subject: 邮件主题
        content: 邮件内容
        content_type: 内容类型（html/text）
    """
    logger.info(f"开始发送邮件通知: {to_email}, 主题: {subject}")
    
    try:
        # 检查邮件配置
        if not all([settings.SMTP_HOST, settings.SMTP_PORT, 
                   settings.SMTP_USER, settings.SMTP_PASSWORD]):
            logger.error("邮件服务未配置")
            return {
                "success": False,
                "message": "邮件服务未配置"
            }
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = to_email
        
        # 添加内容
        if content_type == "html":
            part = MIMEText(content, 'html')
        else:
            part = MIMEText(content, 'plain')
        
        msg.attach(part)
        
        # 发送邮件
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"邮件发送成功: {to_email}")
        
        # 记录发送日志
        db = self.db
        notification_service = NotificationService(db)
        notification_service.log_notification(
            notification_type="email",
            recipient=to_email,
            subject=subject,
            content=content,
            success=True
        )
        
        return {
            "success": True,
            "message": "邮件发送成功",
            "to_email": to_email,
            "subject": subject
        }
        
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        
        # 记录失败日志
        try:
            db = self.db
            notification_service = NotificationService(db)
            notification_service.log_notification(
                notification_type="email",
                recipient=to_email,
                subject=subject,
                content=content,
                success=False,
                error_message=str(e)
            )
        except Exception as log_error:
            logger.error(f"记录通知日志失败: {str(log_error)}")
        
        return {
            "success": False,
            "message": f"邮件发送失败: {str(e)}",
            "to_email": to_email,
            "subject": subject
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.notification_tasks.send_bulk_emails")
def send_bulk_emails(self, emails: List[Dict[str, str]]):
    """
    批量发送邮件任务
    
    Args:
        emails: 邮件列表，每个元素包含 to_email, subject, content
    """
    logger.info(f"开始批量发送邮件，数量: {len(emails)}")
    
    try:
        db = self.db
        notification_service = NotificationService(db)
        
        sent = 0
        failed = 0
        errors = []
        
        for email_data in emails:
            try:
                # 发送单封邮件
                result = send_email_notification(
                    email_data["to_email"],
                    email_data["subject"],
                    email_data.get("content", ""),
                    email_data.get("content_type", "html")
                )
                
                if result.get("success", False):
                    sent += 1
                else:
                    failed += 1
                    errors.append(f"邮件发送失败: {email_data['to_email']} - {result.get('message', '未知错误')}")
                
            except Exception as e:
                failed += 1
                errors.append(f"邮件发送失败: {email_data.get('to_email', '未知')} - {str(e)}")
        
        logger.info(f"批量邮件发送完成: 成功={sent}, 失败={failed}")
        
        return {
            "success": True,
            "message": "批量邮件发送完成",
            "total": len(emails),
            "sent": sent,
            "failed": failed,
            "errors": errors[:20]
        }
        
    except Exception as e:
        logger.error(f"批量邮件发送任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "total": len(emails),
            "sent": 0,
            "failed": len(emails),
            "errors": [str(e)]
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.notification_tasks.send_system_alert")
def send_system_alert(self, title: str, message: str, level: str = "warning", 
                     recipients: List[str] = None):
    """
    发送系统告警任务
    
    Args:
        title: 告警标题
        message: 告警消息
        level: 告警级别（info/warning/error/critical）
        recipients: 接收人列表（邮箱），为None时发送给管理员
    """
    logger.info(f"开始发送系统告警: {title}, 级别: {level}")
    
    try:
        db = self.db
        notification_service = NotificationService(db)
        
        # 获取告警接收人
        if not recipients:
            recipients = notification_service.get_admin_emails()
        
        if not recipients:
            logger.warning("没有找到告警接收人")
            return {
                "success": False,
                "message": "没有找到告警接收人"
            }
        
        # 构建告警内容
        alert_content = f"""
        <h2>系统告警: {title}</h2>
        <p><strong>级别:</strong> {level.upper()}</p>
        <p><strong>时间:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        <p><strong>消息:</strong></p>
        <pre>{message}</pre>
        <hr>
        <p><em>此邮件由系统自动发送，请勿回复。</em></p>
        """
        
        # 发送告警邮件
        email_results = []
        for recipient in recipients:
            try:
                result = send_email_notification(
                    recipient,
                    f"[{level.upper()}] {title}",
                    alert_content,
                    "html"
                )
                email_results.append({
                    "recipient": recipient,
                    "success": result.get("success", False)
                })
            except Exception as e:
                email_results.append({
                    "recipient": recipient,
                    "success": False,
                    "error": str(e)
                })
        
        # 发送WebSocket通知
        try:
            # 这里需要导入websocket模块
            import asyncio
            asyncio.run(notify_system_message(
                f"系统告警: {title}",
                level=level
            ))
        except Exception as ws_error:
            logger.error(f"WebSocket通知发送失败: {str(ws_error)}")
        
        # 记录告警
        notification_service.log_alert(
            title=title,
            message=message,
            level=level,
            recipients=recipients
        )
        
        logger.info(f"系统告警发送完成: 接收人={len(recipients)}")
        
        return {
            "success": True,
            "message": "系统告警发送完成",
            "title": title,
            "level": level,
            "recipients_count": len(recipients),
            "email_results": email_results
        }
        
    except Exception as e:
        logger.error(f"系统告警发送任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "title": title,
            "level": level
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.notification_tasks.send_match_notifications")
def send_match_notifications(self, match_id: int, notification_type: str = "reminder"):
    """
    发送比赛通知任务
    
    发送比赛相关的通知（提醒、更新、结果等）
    
    Args:
        match_id: 比赛ID
        notification_type: 通知类型（reminder/update/result）
    """
    logger.info(f"开始发送比赛通知: 比赛ID={match_id}, 类型={notification_type}")
    
    try:
        db = self.db
        notification_service = NotificationService(db)
        match_service = MatchService(db)
        
        # 获取比赛信息
        match = match_service.get_match_by_id(match_id)
        if not match:
            return {
                "success": False,
                "message": f"比赛不存在: {match_id}"
            }
        
        # 获取订阅该比赛的用户
        subscribers = notification_service.get_match_subscribers(match_id)
        
        if not subscribers:
            logger.info(f"没有找到比赛 {match_id} 的订阅者")
            return {
                "success": True,
                "message": "没有订阅者",
                "match_id": match_id,
                "subscribers_count": 0
            }
        
        # 构建通知内容
        notification_data = notification_service.build_match_notification(
            match, notification_type
        )
        
        sent = 0
        failed = 0
        errors = []
        
        for subscriber in subscribers:
            try:
                # 发送通知
                if subscriber.get("email_notifications", False):
                    # 发送邮件通知
                    email_result = send_email_notification(
                        subscriber["email"],
                        notification_data["subject"],
                        notification_data["email_content"],
                        "html"
                    )
                    
                    if not email_result.get("success", False):
                        failed += 1
                        errors.append(f"邮件发送失败: {subscriber['email']}")
                        continue
                
                if subscriber.get("push_notifications", False):
                    # 这里可以集成推送通知服务
                    # 例如：Firebase Cloud Messaging, Apple Push Notification Service等
                    pass
                
                # 发送WebSocket通知
                try:
                    import asyncio
                    asyncio.run(notify_system_message(
                        notification_data["push_content"],
                        level="info",
                        user_id=str(subscriber["user_id"])
                    ))
                except Exception as ws_error:
                    logger.error(f"WebSocket通知发送失败: {str(ws_error)}")
                
                sent += 1
                
                # 记录用户通知
                notification_service.log_user_notification(
                    user_id=subscriber["user_id"],
                    notification_type=f"match_{notification_type}",
                    title=notification_data["subject"],
                    content=notification_data["push_content"],
                    match_id=match_id
                )
                
            except Exception as e:
                failed += 1
                errors.append(f"用户 {subscriber.get('user_id', '未知')} 通知失败: {str(e)}")
        
        logger.info(f"比赛通知发送完成: 比赛={match_id}, 成功={sent}, 失败={failed}")
        
        return {
            "success": True,
            "message": "比赛通知发送完成",
            "match_id": match_id,
            "notification_type": notification_type,
            "subscribers_count": len(subscribers),
            "sent": sent,
            "failed": failed,
            "errors": errors[:10]
        }
        
    except Exception as e:
        logger.error(f"比赛通知发送任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "match_id": match_id,
            "notification_type": notification_type
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.notification_tasks.send_intelligence_alert")
def send_intelligence_alert(self, intelligence_id: int):
    """
    发送重要情报告警任务
    
    当有重要情报时，发送告警通知
    
    Args:
        intelligence_id: 情报ID
    """
    logger.info(f"开始发送重要情报告警: 情报ID={intelligence_id}")
    
    try:
        db = self.db
        notification_service = NotificationService(db)
        intelligence_service = IntelligenceService(db)
        
        # 获取情报信息
        intelligence = intelligence_service.get_intelligence_by_id(intelligence_id)
        if not intelligence:
            return {
                "success": False,
                "message": f"情报不存在: {intelligence_id}"
            }
        
        # 检查是否重要情报（权重 > 0.8）
        if intelligence.calculated_weight < 0.8:
            logger.info(f"情报 {intelligence_id} 权重较低，不发送告警")
            return {
                "success": True,
                "message": "情报权重较低，不发送告警",
                "intelligence_id": intelligence_id,
                "weight": intelligence.calculated_weight
            }
        
        # 获取订阅相关比赛或联赛的用户
        subscribers = notification_service.get_intelligence_subscribers(intelligence)
        
        if not subscribers:
            logger.info(f"没有找到情报 {intelligence_id} 的订阅者")
            return {
                "success": True,
                "message": "没有订阅者",
                "intelligence_id": intelligence_id,
                "subscribers_count": 0
            }
        
        # 构建告警内容
        alert_data = notification_service.build_intelligence_alert(intelligence)
        
        sent = 0
        failed = 0
        
        for subscriber in subscribers:
            try:
                # 发送通知
                if subscriber.get("email_notifications", False):
                    send_email_notification(
                        subscriber["email"],
                        alert_data["subject"],
                        alert_data["email_content"],
                        "html"
                    )
                
                # 发送WebSocket通知
                try:
                    import asyncio
                    asyncio.run(notify_system_message(
                        alert_data["push_content"],
                        level="warning",
                        user_id=str(subscriber["user_id"])
                    ))
                except Exception as ws_error:
                    logger.error(f"WebSocket通知发送失败: {str(ws_error)}")
                
                sent += 1
                
                # 记录用户通知
                notification_service.log_user_notification(
                    user_id=subscriber["user_id"],
                    notification_type="intelligence_alert",
                    title=alert_data["subject"],
                    content=alert_data["push_content"],
                    intelligence_id=intelligence_id
                )
                
            except Exception as e:
                failed += 1
                logger.error(f"用户 {subscriber.get('user_id', '未知')} 告警发送失败: {str(e)}")
        
        logger.info(f"重要情报告警发送完成: 情报={intelligence_id}, 成功={sent}, 失败={failed}")
        
        return {
            "success": True,
            "message": "重要情报告警发送完成",
            "intelligence_id": intelligence_id,
            "subscribers_count": len(subscribers),
            "sent": sent,
            "failed": failed
        }
        
    except Exception as e:
        logger.error(f"重要情报告警发送任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "intelligence_id": intelligence_id
        }