"""
Email helpers that read SMTP credentials from SiteSettings at call time.
This means admins can update credentials in the Django admin without a redeploy.
"""
import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger('store')


def _get_smtp_config():
    """Return SiteSettings, importing lazily to avoid circular imports."""
    from store.models import SiteSettings
    return SiteSettings.get()


def send_email(to: str | list, subject: str, html_body: str, text_body: str = '') -> bool:
    """
    Send a single email via the SMTP settings stored in SiteSettings.
    Returns True on success, False on failure (never raises).
    """
    cfg = _get_smtp_config()

    if not cfg.smtp_user or not cfg.smtp_password:
        logger.warning("SMTP not configured in Site Settings — email not sent to %s", to)
        return False

    recipients = [to] if isinstance(to, str) else to
    from_addr = cfg.effective_from_email

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = ', '.join(recipients)

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        if cfg.smtp_use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(cfg.smtp_host, cfg.smtp_port, context=context) as server:
                server.login(cfg.smtp_user, cfg.smtp_password)
                server.sendmail(from_addr, recipients, msg.as_bytes())
        else:
            with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as server:
                if cfg.smtp_use_tls:
                    server.starttls(context=ssl.create_default_context())
                server.login(cfg.smtp_user, cfg.smtp_password)
                server.sendmail(from_addr, recipients, msg.as_bytes())

        logger.info("Email sent to %s — subject: %s", recipients, subject)
        return True

    except Exception as exc:
        logger.exception("Failed to send email to %s: %s", recipients, exc)
        return False


def send_otp_email(to: str, otp: str, first_name: str = '') -> bool:
    """Send the OTP verification email for new signups."""
    greeting = f"Hi {first_name}," if first_name else "Hello,"
    subject = "Verify your NAPTRIO account"
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:32px;background:#f9f9f9;border-radius:12px;">
      <h2 style="color:#0c5faa;margin-bottom:4px;">NAPTRIO</h2>
      <p style="color:#555;font-size:14px;margin-bottom:24px;">India's Premium Audio Brand</p>
      <p style="color:#1a1a1a;font-size:15px;">{greeting}</p>
      <p style="color:#444;font-size:14px;line-height:1.6;">
        Thanks for signing up! Use the OTP below to verify your email address.
        This code expires in <strong>10 minutes</strong>.
      </p>
      <div style="text-align:center;margin:32px 0;">
        <span style="display:inline-block;font-size:36px;font-weight:700;letter-spacing:12px;
                     color:#0c5faa;background:#e8f0fb;padding:16px 32px;border-radius:12px;">
          {otp}
        </span>
      </div>
      <p style="color:#888;font-size:12px;">
        If you didn't create an account, you can safely ignore this email.
      </p>
    </div>
    """
    text_body = f"{greeting}\n\nYour NAPTRIO verification OTP is: {otp}\n\nThis code expires in 10 minutes."
    return send_email(to, subject, html_body, text_body)
