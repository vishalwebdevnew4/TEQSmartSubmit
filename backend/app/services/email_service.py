#!/usr/bin/env python3
"""
Email Service - Sends client outreach emails with tracking.
"""

import json
import sys
import os
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    attachment_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Send an email with HTML content and optional attachments.
    
    Returns:
        Dict with success status and message ID
    """
    # Get SMTP settings from environment or parameters
    smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
    smtp_user = smtp_user or os.getenv("SMTP_USER")
    smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
    from_email = from_email or smtp_user or os.getenv("SMTP_FROM")
    from_name = from_name or os.getenv("SMTP_FROM_NAME", "TEQSmartSubmit")
    
    if not smtp_user or not smtp_password:
        return {
            "success": False,
            "error": "SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD environment variables.",
        }
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email
        
        # Add text and HTML parts
        if text_content:
            text_part = MIMEText(text_content, "plain")
            msg.attach(text_part)
        
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)
        
        # Add attachments
        if attachment_paths:
            for attachment_path in attachment_paths:
                if Path(attachment_path).exists():
                    with open(attachment_path, "rb") as f:
                        img = MIMEImage(f.read())
                        img.add_header("Content-Disposition", f"attachment; filename={Path(attachment_path).name}")
                        msg.attach(img)
        
        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return {
            "success": True,
            "message": "Email sent successfully",
            "to": to_email,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "to": to_email,
        }


def generate_client_email_html(
    business_name: str,
    preview_url: str,
    screenshot_url: Optional[str] = None,
    personalized_message: Optional[str] = None,
) -> str:
    """Generate HTML email template for client outreach."""
    message = personalized_message or f"Hi! We've created a beautiful website preview for {business_name}. Check it out!"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Website Preview for {business_name}</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">Website Preview</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">{business_name}</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="font-size: 16px; margin-bottom: 20px;">{message}</p>
            
            {f'<img src="{screenshot_url}" alt="Website Preview" style="width: 100%; border-radius: 8px; margin: 20px 0;" />' if screenshot_url else ''}
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{preview_url}" 
                   style="display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    View Live Preview
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
                This is a preview of your new website. Click the button above to see it live!
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px;">
            <p>This email was sent by TEQSmartSubmit</p>
        </div>
    </body>
    </html>
    """
    return html


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Send client outreach email")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--business-name", required=True, help="Business name")
    parser.add_argument("--preview-url", required=True, help="Website preview URL")
    parser.add_argument("--screenshot-url", help="Screenshot image URL")
    parser.add_argument("--message", help="Personalized message")
    parser.add_argument("--subject", help="Email subject (default: auto-generated)")
    
    args = parser.parse_args()
    
    subject = args.subject or f"Website Preview for {args.business_name}"
    
    html_content = generate_client_email_html(
        args.business_name,
        args.preview_url,
        args.screenshot_url,
        args.message,
    )
    
    result = send_email(
        args.to,
        subject,
        html_content,
        text_content=f"Hi! Check out your website preview: {args.preview_url}",
    )
    
    print(json.dumps(result, indent=2))
    
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()

