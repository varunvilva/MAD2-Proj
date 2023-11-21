
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders

# SMTP_SERVER_HOST= "localhost"
# SMTP_SERVER__PORT= 1025
# SENDER_ADDRESS= "22f1000553@ds.study.iitm.ac.in"
# SENDER_PASSWORD= "villy1208#"

# def send_email(to_address,subject,message,content='text',attachment_file=None):
#     msg=MIMEMultipart()
#     msg['From'] = SENDER_ADDRESS
#     msg['To'] = to_address
#     msg['Subject']=subject
#     if content=='html':
#         msg.attach(MIMEText(message,"html"))
#     else:
#         msg.attach(MIMEText(message,"plain"))
#     if attachment_file:
#         with open(attachment_file, 'rb') as attachment:
#             part=MIMEBase("application","octet-stream")
#             part.set_payload(attachment.read())
#         encoders.encode_base64(part)
#         part.add_header("Content-Disposition", f"attachment; filename={attachment_file}",)
#         msg.attach(part)

#     try:
#         s= smtplib.SMTP(host=SMTP_SERVER_HOST,
#                         port=SMTP_SERVER__PORT)
#         s.login(SENDER_ADDRESS,SENDER_PASSWORD)
#         s.send_message(msg)
#         s.quit()
#     except:
#         return False
#     return True

# send_email("varunvilva1208@gmail.com","Test","This is a test email",'html',None)
# from api_application import mail

# from flask_mail import Message, Mail
# from flask import render_template

# def send_email(email):
#     msg_title = 'Title'
#     sender = 'noreply@app.com'
#     msg = Message(msg_title, sender = sender, recipients = [email])
#     msg_body='This is a test email'
#     msg.body="" 
#     data = {
#         'app_name':"MAD2 - Grocerify",
#         "title":"grocerify",
#         "body":"This is a test email"
#     }
#     msg.html = render_template('email.html',data=data)
#     try:
#         mail.send(msg)
#         return "Email sent ..."
#     except Exception as e:
#         return(str(e))