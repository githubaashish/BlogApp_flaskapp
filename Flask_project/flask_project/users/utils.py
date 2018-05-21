import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flask_project import mail

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    output_size = (60, 60)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn 



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender = 'aix4aashish@gmail.com', recipients=['aix4aashish@gmail.com'])
    msg.body = f''' To reset the password Please go to the following link : 
{url_for('users.reset_token', token=token, _external=True)}
    

Please ignore the message if does not belongs to aix4aashish@gmail.com , Testing the Website building 
'''
    mail.send(msg)


