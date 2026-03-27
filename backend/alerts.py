"""Email alert system for detected attacks."""
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, ALERT_RECIPIENT


# In-memory alert store
alert_history = []


def record_alert(prediction_result: dict, flow_details: dict = None, send_email: bool = False):
    """Record alert for attack detection. Email only when send_email=True."""
    alert = {
        "id": len(alert_history) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attack_type": prediction_result.get("attack_type", "Unknown"),
        "confidence": prediction_result.get("confidence", 0),
        "prediction": prediction_result.get("prediction", "Unknown"),
        "flow_info": flow_details or {},
    }
    alert_history.append(alert)

    # Send individual emails only when explicitly requested by the caller.
    if send_email and SMTP_USER and SMTP_PASS and ALERT_RECIPIENT:
        threading.Thread(target=_safe_send_email, args=(alert,), daemon=True).start()

    return alert


def _safe_send_email(alert):
    try:
        send_alert_email(alert)
    except Exception as e:
        print(f"Email alert failed: {e}")


def send_upload_summary_email_async(
    filename: str,
    total_rows: int,
    processed_rows: int,
    attack_count: int,
    benign_count: int,
    attack_breakdown: dict,
):
    """Send one summary email for a batch upload when attacks are found."""
    if not (SMTP_USER and SMTP_PASS and ALERT_RECIPIENT):
        return

    threading.Thread(
        target=_safe_send_upload_summary_email,
        args=(filename, total_rows, processed_rows, attack_count, benign_count, attack_breakdown),
        daemon=True,
    ).start()


def _safe_send_upload_summary_email(
    filename: str,
    total_rows: int,
    processed_rows: int,
    attack_count: int,
    benign_count: int,
    attack_breakdown: dict,
):
    try:
        send_upload_summary_email(
            filename=filename,
            total_rows=total_rows,
            processed_rows=processed_rows,
            attack_count=attack_count,
            benign_count=benign_count,
            attack_breakdown=attack_breakdown,
        )
    except Exception as e:
        print(f"Upload summary email failed: {e}")


def send_alert_email(alert: dict):
    """Send attack alert email via SMTP."""
    subject = f"⚠️ IDS ALERT: {alert['attack_type']} Detected!"

    flow_info = ""
    if alert.get("flow_info"):
        flow_items = [f"  • {k}: {v}" for k, v in alert["flow_info"].items()]
        flow_info = "\n".join(flow_items)

    body = f"""
====================================
  INTRUSION DETECTION ALERT
====================================

Attack Type:   {alert['attack_type']}
Confidence:    {alert['confidence']}%
Timestamp:     {alert['timestamp']}
Alert ID:      {alert['id']}

Flow Details:
{flow_info if flow_info else '  No additional details available.'}

------------------------------------
This is an automated alert from the
Hybrid Attention-Based IDS System.
====================================
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"Alert email sent for: {alert['attack_type']}")


def send_upload_summary_email(
    filename: str,
    total_rows: int,
    processed_rows: int,
    attack_count: int,
    benign_count: int,
    attack_breakdown: dict,
):
    """Send a summary email for batch-uploaded logs."""
    subject = f"IDS Upload Summary: {attack_count} Attack(s) Detected in {filename}"

    breakdown_lines = [
        f"  - {attack_type}: {count}"
        for attack_type, count in sorted(attack_breakdown.items(), key=lambda item: (-item[1], item[0]))
    ]
    breakdown_text = "\n".join(breakdown_lines) if breakdown_lines else "  No attack breakdown available."

    body = f"""
====================================
   IDS BATCH UPLOAD SUMMARY
====================================

Filename:      {filename}
Timestamp:     {datetime.now(timezone.utc).isoformat()}
Total Rows:    {total_rows}
Processed:     {processed_rows}
Attacks Found: {attack_count}
Benign Rows:   {benign_count}

Attack Breakdown:
{breakdown_text}

------------------------------------
This is an automated summary from the
Hybrid Attention-Based IDS System.
====================================
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"Upload summary email sent for: {filename}")


def get_alerts(limit: int = 100, attack_type: str = None):
    """Get alert history with optional filtering."""
    alerts = list(reversed(alert_history))
    if attack_type:
        alerts = [a for a in alerts if a["attack_type"] == attack_type]
    return alerts[:limit]


def get_alert_stats():
    """Get summary of alerts."""
    if not alert_history:
        return {"total": 0, "by_type": {}}
    by_type = {}
    for a in alert_history:
        t = a["attack_type"]
        by_type[t] = by_type.get(t, 0) + 1
    return {"total": len(alert_history), "by_type": by_type}
