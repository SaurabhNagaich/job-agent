import os
import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# Candidate Details
USER_DATA = {
    "name": "Saurabh Nagaich",
    "email": "saurabh.nagaich.in@gmail.com",
    "phone": "9696780704",
    "target_roles": [".NET Developer", "Full Stack Developer", "C# Microservices"],
    "target_locations": ["Bhopal", "Indore", "Noida", "Gurugram"],
    "current_ctc": "8.01 LPA",
    "expected_ctc": "12 LPA"
}

# Gmail App Password (Environment variable ya yahan direct paste karein)
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

@app.get("/", response_class=HTMLResponse)
def home():
    # Direct Job search links generator
    links_html = ""
    for loc in USER_DATA["target_locations"]:
        for role in USER_DATA["target_roles"]:
            naukri_query = f"{role.replace(' ', '-')}-jobs-in-{loc.lower()}?experience=3"
            naukri_url = f"https://www.naukri.com/{naukri_query}"
            linkedin_url = f"https://www.linkedin.com/jobs/search?keywords={urllib.parse.quote(role)}&location={urllib.parse.quote(loc)}"
            
            links_html += f"""
            <div style="background:#1e293b; padding:12px; margin:8px 0; border-radius:8px;">
                <b style="color:#38bdf8;">{role}</b> - <span style="color:#94a3b8;">{loc}</span><br><br>
                <a href="{naukri_url}" target="_blank" style="color:#4ade80; text-decoration:none; margin-right:15px;">👉 Open Naukri</a>
                <a href="{linkedin_url}" target="_blank" style="color:#60a5fa; text-decoration:none;">👉 Open LinkedIn</a>
            </div>
            """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Job Hunter Agent</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f172a; color: #fff; padding: 16px; }}
            input, button {{ width: 100%; padding: 12px; margin: 6px 0; border-radius: 6px; border: 1px solid #334155; box-sizing: border-box; }}
            input {{ background: #1e293b; color: white; }}
            button {{ background: #2563eb; color: white; font-weight: bold; border: none; }}
            .card {{ background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h2>🚀 Auto Job Outreach Agent</h2>
        <p>Target: <b>12+ LPA</b> | Locations: <b>Indore, Bhopal, Noida, Gurugram</b></p>
        
        <div class="card">
            <h3>✉️ Direct HR Cold Emailer</h3>
            <form action="/send-mail" method="post">
                <input type="email" name="hr_email" placeholder="HR / Recruiter Email" required />
                <input type="text" name="company" placeholder="Company Name" required />
                <input type="text" name="role" placeholder="Role (e.g. .NET Developer)" required />
                <button type="submit">Send 1-Click Application Email</button>
            </form>
        </div>

        <h3>🔍 Direct Filtered Job Feeds</h3>
        {links_html}
    </body>
    </html>
    """

@app.post("/send-mail", response_class=HTMLResponse)
def send_mail(hr_email: str = Form(...), company: str = Form(...), role: str = Form(...)):
    if not GMAIL_APP_PASSWORD:
        return "<h3 style='color:red;'>Error: GMAIL_APP_PASSWORD set nahi hai!</h3><a href='/'>Wapas Jayein</a>"

    try:
        msg = MIMEMultipart()
        msg['From'] = USER_DATA["email"]
        msg['To'] = hr_email
        msg['Subject'] = f"Application: {role} | {USER_DATA['name']} (3+ Yrs Exp | ASP.NET Core & Microservices)"

        body = f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {role} opportunity. I bring 3+ years of core experience in ASP.NET Core, C#, Microservices, SQL Server, Kafka/RabbitMQ, and Angular in high-volume enterprise systems.

Key Profile Highlights:
- Tech Stack: ASP.NET Core, C#, Web API, Microservices, SQL Server, Angular
- Notice Period: Standard / Immediate release options
- Expected CTC: {USER_DATA['expected_ctc']}
- Preferred Locations: Bhopal, Indore, Noida, Gurugram

Looking forward to connecting with you.

Best regards,
{USER_DATA['name']}
Phone: {USER_DATA['phone']}
LinkedIn: https://linkedin.com/in/saurabh-nagaich-38b9ab192
"""
        msg.attach(MIMEText(body, 'plain'))

        # Resume attach karein agar directory mein available ho
        resume_name = "resume.pdf"
        if os.path.exists(resume_name):
            with open(resume_name, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={resume_name}")
            msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(USER_DATA["email"], GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"<div style='font-family:sans-serif; padding:20px; text-align:center;'><h2>✅ Email Successfully Sent to {hr_email}!</h2><a href='/'>Wapas Jayein</a></div>"
    except Exception as e:
        return f"<div style='color:red; font-family:sans-serif; padding:20px;'><h2>❌ Failed to send</h2><p>{str(e)}</p><a href='/'>Wapas Jayein</a></div>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
