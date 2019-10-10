from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Regexp
from app import mysql
from app.cities import cities
from app.password_check import check_password


class FarmerRegistrationForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('firstname', validators=[DataRequired()])
    email = StringField('Email-Id', validators=[DataRequired(), Email()])
    mobile = StringField('Mobile No', validators=[DataRequired(), Length(
        min=10, max=10, message='Mobile Number should be 10 digits only'), Regexp(regex='^[0-9]+$', message='Only numbers allowed')])
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=8, message='Password should be atleast 8 characters long')])
    password2 = PasswordField('Re-Enter the Password', validators=[
                              DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        curr = mysql.connection.cursor()
        curr.execute(
            '''SELECT EMAILID FROM FARMER WHERE EMAILID='{}' '''.format(email.data))
        records = curr.fetchall()
        if records:
            raise ValidationError('Please use a different Email-ID')
        curr.close()

    def validate_mobile(self, mobile):
        curr = mysql.connection.cursor()
        curr.execute(
            '''SELECT MOBILENO FROM FARMER WHERE MOBILENO='{}' '''.format(mobile.data))
        records = curr.fetchall()
        if records:
            raise ValidationError('Please use a different Mobile No')
        curr.close()


class ConsumerRegistrationForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('firstname', validators=[DataRequired()])
    email = StringField('Email-Id', validators=[DataRequired(), Email()])
    mobile = StringField('Mobile No', validators=[DataRequired(), Length(
        min=10, max=10, message='Mobile Number should be 10 digits only'), Regexp(regex='^[0-9]+$', message='Only numbers allowed')])
    password = PasswordField('Password', validators=[DataRequired(), Length(
        min=8, message='Password should be atleast 8 characters long')])
    password2 = PasswordField('Re-Enter the Password', validators=[
                              DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        curr = mysql.connection.cursor()
        curr.execute(
            '''SELECT EMAILID FROM CONSUMER WHERE EMAILID='{}' '''.format(email.data))
        records = curr.fetchall()
        if records:
            raise ValidationError('Please use a different Email-ID')
        curr.close()

    def validate_mobile(self, mobile):
        curr = mysql.connection.cursor()
        curr.execute(
            '''SELECT MOBILENO FROM CONSUMER WHERE MOBILENO='{}' '''.format(mobile.data))
        records = curr.fetchall()
        if records:
            raise ValidationError('Please use a different Mobile No')
        curr.close()


class FarmerLoginForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_password(self, password):
        curr = mysql.connection.cursor()
        query = '''SELECT password_hash FROM farmer WHERE emailid='{}' '''.format(
            self.email.data)
        curr.execute(query)
        data = curr.fetchall()
        print(data)
        if not data or not check_password(data[0][0], password.data):
            raise ValidationError('Email-Id or Password is Incorrect')
        curr.close()


class ConsumerLoginForm(FlaskForm):
    email = StringField('Username', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_password(self, password):
        curr = mysql.connection.cursor()
        query = '''SELECT password_hash FROM CONSUMER WHERE emailid='{}' '''.format(
            self.email.data)
        curr.execute(query)
        data = curr.fetchall()
        print(data)
        if not data or not check_password(data[0][0], password.data):
            raise ValidationError('Email-Id or Password is Incorrect')
        curr.close()


class FarmerOrConsumer(FlaskForm):
    choice = BooleanField('Farmer or Consumer')
    submit = SubmitField('Select')


class OTPForm(FlaskForm):
    a = StringField('1', validators=[DataRequired(), Length(
        max=1), Regexp(regex='[0-9]', message='Only numbers allowed')])
    b= StringField('2', validators=[DataRequired(), Length(
        max=1), Regexp(regex='[0-9]', message='Only numbers allowed')])
    c = StringField('3', validators=[DataRequired(), Length(
        max=1), Regexp(regex='[0-9]', message='Only numbers allowed')])
    d = StringField('4', validators=[DataRequired(), Length(
        max=1), Regexp(regex='[0-9]', message='Only numbers allowed')])
    e = StringField('5', validators=[DataRequired(), Length(
        max=1), Regexp(regex='[0-9]', message='Only numbers allowed')])
    f = StringField('6', validators=[DataRequired(), Length(
        max=1), Regexp(regex='[0-9]', message='Only numbers allowed')])
    submit = SubmitField()
