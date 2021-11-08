import smtplib
from email.message import EmailMessage
import update_diary
import secret


# smtp_domain_name = 'smtp.mail.yahoo.com' 
# smtp_domain_name = "smtp.live.com"
# smtp_domain_name = 'smtp-mail.outlook.com'
smtp_domain_name = 'smtp.gmail.com'
sender = secret.email_id
receiver = secret.receiver
receivers = secret.toAddresses
subject = secret.subject
content = secret.content


def create_msg(time):
	msg = EmailMessage()
	msg_txt = content%time
	msg.set_content(msg_txt)
	msg['Subject'] = subject 
	msg['From'] = sender
	msg['To'] = receiver
	return msg


def create_mail(time):
	body = content%time
	email_text = """\
	From: %s
	To: %s
	Subject: %s

	%s
	""" % (sender, ", ".join(receivers), subject, body)
	print(email_text)
	return email_text


def send_message(msg):
	try :
		conn = smtplib.SMTP(smtp_domain_name,587)  
		type(conn)  
		conn.ehlo()  
		conn.starttls()  
		conn.login(secret.email_id,secret.password)  
		conn.send_message(msg, sender, receiver)
		conn.quit() 
	except smtplib.SMTPAuthenticationError:
		print("Could not authenticate to SMTP server")
	except smtplib.SMTPDataError:
		print("Error in the message, sender not matching sender")


def send_email(msg):
	try :
		conn = smtplib.SMTP(smtp_domain_name,587)  
		type(conn)  
		conn.ehlo()  
		conn.starttls()  
		conn.login(secret.email_id,secret.password)  
		conn.sendmail(sender, receivers, msg)
		conn.quit() 
	except smtplib.SMTPAuthenticationError:
		print("Could not authenticate to SMTP server")
	except smtplib.SMTPDataError:
		print("Error in the message, sender not matching sender")


def send_secure_email(msg):
	try :
		conn = smtplib.SMTP_SSL(smtp_domain_name, 465) # For Yahoo or Gmail
		conn.login(secret.email_id,secret.password)  
		conn.sendmail(sender, receivers, msg)
		conn.send_message(msg=msg)
		conn.quit() 
	except smtplib.SMTPAuthenticationError:
		print("Could not authenticate to SMTP server")
	except smtplib.SMTPServerDisconnected:
		print("Could not login and was disconnected")


def create_send_message(filename):
	date, time = update_diary.get_date_time(filename)
	# We remove the seconds of the time 14:41:52 
	msg = create_msg(time[3:])
	send_message(msg)


def main():
	filename = "20211029_192753_1.mp4"
	time = update_diary.get_date_time(filename)
	msg = create_msg(time)
	send_message(msg)



if __name__ == "__main__" : 
	main()