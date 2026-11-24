"""Notificações por email. As credenciais e a conexão SMTP vêm de quem cria o serviço."""
import logging
import smtplib

from utils.helpers import utcnow

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, host, port, user, password, smtp_factory=smtplib.SMTP):
        self.email_host = host
        self.email_port = port
        self.email_user = user
        self.email_password = password
        self.smtp_factory = smtp_factory
        self.notifications = []

    @classmethod
    def from_config(cls, config):
        return cls(
            host=config['SMTP_HOST'],
            port=config['SMTP_PORT'],
            user=config['SMTP_USER'],
            password=config['SMTP_PASSWORD'],
        )

    def is_configured(self):
        return bool(self.email_user and self.email_password)

    def send_email(self, to, subject, body):
        if not self.is_configured():
            logger.warning('Email não enviado: SMTP_USER e SMTP_PASSWORD não configurados')
            return False
        try:
            server = self.smtp_factory(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            logger.info('Email enviado para %s', to)
            return True
        except (smtplib.SMTPException, OSError):
            logger.exception('Erro ao enviar email')
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}"
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utcnow()
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [
            notification for notification in self.notifications
            if notification['user_id'] == user_id
        ]
