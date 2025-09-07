import asyncio
import os
from typing import Any

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailService:
    def __init__(self):
        self.from_email = "do_not_reply@parkplace.com"

    async def send_email(self, to_email: str, subject: str, body: str, html_body: str | None = None):
        """Send an email by printing to console (hackathon mode)"""
        print("\n" + "="*60)
        print("📧 EMAIL SENT")
        print("="*60)
        print(f"From: {self.from_email}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print("-"*60)
        print("Content:")
        print(body)
        if html_body:
            print("\nHTML Version:")
            print(html_body)
        print("="*60 + "\n")
        return True

    async def send_verification_approved_email(self, to_email: str, name: str = ""):
        """Send verification approved email"""
        subject = "Park Place - Identity Verification Approved! 🎉"
        
        body = f"""Hi {name or 'there'},

Congratulations! Your identity verification has been approved.

You now have access to:
• Premium parking spaces reserved for verified users
• Enhanced security features
• Priority customer support

You can now book verified-only parking spaces in the Park Place app.

Thank you for completing the verification process!

Best regards,
The Park Place Team
"""

        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2E7D32;">🎉 Identity Verification Approved!</h2>
        
        <p>Hi {name or 'there'},</p>
        
        <p><strong>Congratulations! Your identity verification has been approved.</strong></p>
        
        <div style="background-color: #E8F5E8; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #2E7D32; margin-top: 0;">You now have access to:</h3>
            <ul style="margin: 0;">
                <li>Premium parking spaces reserved for verified users</li>
                <li>Enhanced security features</li>
                <li>Priority customer support</li>
            </ul>
        </div>
        
        <p>You can now book verified-only parking spaces in the Park Place app.</p>
        
        <p>Thank you for completing the verification process!</p>
        
        <p>Best regards,<br>
        <strong>The Park Place Team</strong></p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="font-size: 12px; color: #666;">
            This email was sent by Park Place. If you have any questions, please contact our support team.
        </p>
    </div>
</body>
</html>
"""

        return await self.send_email(to_email, subject, body, html_body)

    async def send_verification_rejected_email(self, to_email: str, name: str = "", reason: str = ""):
        """Send verification rejected email"""
        subject = "Park Place - Identity Verification Update Required"
        
        body = f"""Hi {name or 'there'},

We were unable to verify your identity with the documents you provided.

{f"Reason: {reason}" if reason else ""}

To complete verification, please:
1. Ensure all documents are clear and readable
2. Make sure your driver's license is valid and not expired
3. Verify that the license plate on your registration matches what you entered
4. Ensure your profile photo clearly shows your face

You can resubmit your verification documents through the Park Place app.

If you have questions, please contact our support team.

Best regards,
The Park Place Team
"""

        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #D32F2F;">Identity Verification Update Required</h2>
        
        <p>Hi {name or 'there'},</p>
        
        <p>We were unable to verify your identity with the documents you provided.</p>
        
        {f'<div style="background-color: #FFEBEE; padding: 15px; border-radius: 8px; margin: 20px 0;"><p style="margin: 0;"><strong>Reason:</strong> {reason}</p></div>' if reason else ''}
        
        <div style="background-color: #FFF3E0; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #F57C00; margin-top: 0;">To complete verification, please:</h3>
            <ol style="margin: 0;">
                <li>Ensure all documents are clear and readable</li>
                <li>Make sure your driver's license is valid and not expired</li>
                <li>Verify that the license plate on your registration matches what you entered</li>
                <li>Ensure your profile photo clearly shows your face</li>
            </ol>
        </div>
        
        <p>You can resubmit your verification documents through the Park Place app.</p>
        
        <p>If you have questions, please contact our support team.</p>
        
        <p>Best regards,<br>
        <strong>The Park Place Team</strong></p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        <p style="font-size: 12px; color: #666;">
            This email was sent by Park Place. If you have any questions, please contact our support team.
        </p>
    </div>
</body>
</html>
"""

        return await self.send_email(to_email, subject, body, html_body)