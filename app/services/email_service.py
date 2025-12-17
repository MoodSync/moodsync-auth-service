import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
    
    async def send_otp_email(self, to_email: str, otp_code: str, purpose: str):
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            print(f"[EMAIL SIMULATION] OTP for {to_email}: {otp_code}")
            return
        
        subject = self._get_subject(purpose)
        body = self._render_template(purpose, otp_code)
        
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
            # In production, log to monitoring service
    
    def _get_subject(self, purpose: str) -> str:
        subjects = {
            "registration": "Verify Your Account",
            "login": "Your Login OTP",
            "reset_password": "Reset Your Password"
        }
        return subjects.get(purpose, "Your OTP Code")
    
    def _render_template(self, purpose: str, otp_code: str) -> str:
        templates = {
            "registration": """
            <h2>Verify Your Account</h2>
            <p>Your verification code is: <strong>{{ otp_code }}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
            """,
            "login": """
            <h2>Login Verification</h2>
            <p>Your login code is: <strong>{{ otp_code }}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            """,
            "reset_password": """
            <h2>Reset Your Password</h2>
            <p>Your password reset code is: <strong>{{ otp_code }}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request a password reset, please ignore this email.</p>
            """
        }
        
        template_str = templates.get(purpose, templates["registration"])
        template = Template(template_str)
        return template.render(otp_code=otp_code)