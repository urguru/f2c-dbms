from flask_mail import Message
from app import mail,app
from flask import render_template
from threading import Thread
import jwt
from time import time


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_email_verify_OTP_message(otp,name,email):
    send_email('[Farmer to Consumer]', sender=app.config['ADMINS'][0], recipients=[email], text_body=render_template('emails/otp_verification.txt',name=name, otp=otp), html_body=render_template('emails/otp_verification.html', otp=otp, name=name))


def send_password_reset_email(id,email,name,expires_in=600):
    token = jwt.encode({'reset_password': id, 'expires_in': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    send_email('[Farmer2Consumer] Reset Your Password', sender=app.config['ADMINS'][0], recipients=[email], text_body=render_template('emails/reset_password.txt', name=name, token=token), html_body=render_template('emails/reset_password.html', name=name, token=token))
