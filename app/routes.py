from flask import render_template, request, redirect, url_for, session
from app import app, mysql
from app.forms import FarmerRegistrationForm, FarmerLoginForm, FarmerOrConsumer, ConsumerLoginForm, ConsumerRegistrationForm, OTPForm,ResetPasswordRequestForm
from app.cities import cities
from app.password_check import set_password
from app.email import send_email_verify_OTP_message
from random import randint


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    name = 'User'
    id = session.get('id', None)
    type = session.get('consumer', None)
    if id:
        curr = mysql.connection.cursor()
        if type:
            query = ''' SELECT firstname FROM consumer WHERE idConsumer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if data[0][0]:
                name = data[0][0]
        else:
            query = ''' SELECT firstname FROM farmer WHERE idfarmer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if data[0][0]:
                name = data[0][0]
    session['login'] = session.get('login', False)
    return render_template('index.html', login=session['login'], name=name)


@app.route('/farmer_register', methods=['GET', 'POST'])
def farmer_register():
    if session['login']:
        return redirect(url_for('dashboard'))
    form = FarmerRegistrationForm()
    if form.validate_on_submit():
        idFarmer = generate_farmer_id()
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        mobile = form.mobile.data
        city = request.form.get('cities')
        password_hash = set_password(form.password.data)
        OTP = generate_otp()
        session['id'] = idFarmer
        curr = mysql.connection.cursor()
        query = ''' INSERT INTO FARMER(idfarmer,firstname,lastname,emailid,mobileno,password_hash,city,verifiedemail,OTP) VALUES('{}','{}','{}','{}','{}','{}','{}',0, {}) '''.format(
            idFarmer, firstname, lastname, email, mobile, password_hash, city, OTP)
        print(query)
        curr.execute(query)
        mysql.connection.commit()
        return redirect(url_for('otp_form', id=idFarmer))
    return render_template('farmer_register.html', form=form, cities=sorted(cities))


@app.route('/consumer_register', methods=['GET', 'POST'])
def consumer_register():
    if session['login']:
        return redirect(url_for('dashboard'))
    form = ConsumerRegistrationForm()
    if form.validate_on_submit():
        idConsumer = generate_consumer_id()
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        mobile = form.mobile.data
        city = request.form.get('cities')
        password_hash = set_password(form.password.data)
        OTP = generate_otp()
        session['id'] = idConsumer
        session['consumer']=True
        curr = mysql.connection.cursor()
        query = ''' INSERT INTO CONSUMER (idconsumer,firstname,lastname,emailid,mobileno,password_hash,city,verifiedemail,OTP) VALUES('{}','{}','{}','{}','{}','{}','{}',0,{})'''.format(
            idConsumer, firstname, lastname, email, mobile, password_hash, city, OTP)
        print(query)
        curr.execute(query)
        mysql.connection.commit()
        curr.close()
        print(idConsumer)
        return redirect(url_for('otp_form',id=idConsumer))
    return render_template('consumer_register.html', form=form, cities=sorted(cities))


@app.route('/farmer_login', methods=['GET', 'POST'])
def farmer_login():
    if session['login']:
        return redirect(url_for('dashboard'))
    form = FarmerLoginForm()
    print(form.password.data)
    if form.validate_on_submit():
        session['login'] = True
        email = form.email.data
        curr = mysql.connection.cursor()
        query = ''' SELECT idfarmer FROM FARMER WHERE emailid='{}' '''.format(
            email)
        curr.execute(query)
        data = curr.fetchall()
        session['id'] = data[0][0]
        return redirect(url_for('dashboard'))
    return render_template('farmer_login.html', form=form)


@app.route('/consumer_login', methods=['GET', 'POST'])
def consumer_login():
    if session['login']:
        return redirect(url_for('dashboard'))
    form = ConsumerLoginForm()
    print(form.password.data)
    if form.validate_on_submit():
        session['login'] = True
        email = form.email.data
        curr = mysql.connection.cursor()
        query = ''' SELECT idconsumer FROM consumer WHERE emailid='{}' '''.format(
            email)
        curr.execute(query)
        data = curr.fetchall()
        session['id'] = data[0][0]
        return redirect(url_for('dashboard'))
    return render_template('consumer_login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session['login']:
        return redirect(url_for('login'))
    id = session.get('id', None)
    type = session.get('consumer', None)
    name = 'User'

    if id:
        curr = mysql.connection.cursor()
        if type:
            query = ''' SELECT firstname,verifiedemail FROM consumer WHERE idConsumer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1])==0:
                return redirect(url_for('otp_form',id=session['id']))
            if data[0][0]:
                name = data[0][0]
        else:
            query = ''' SELECT firstname,verifiedemail FROM farmer WHERE idfarmer={} '''.format(id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1])==0:
                return redirect(url_for('otp_form',id=session[id]))
            if data[0][0]:
                name = data[0][0]
    return render_template('dashboard.html', login=session['login'], name=name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session['login']:
        return redirect(url_for('dashboard'))
    form = FarmerOrConsumer()
    if form.validate_on_submit():
        if form.choice.data == True:
            return redirect(url_for('consumer_login'))
        else:
            return redirect(url_for('farmer_login'))
    return render_template('farmer_or_consumer.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session['login']:
        return redirect(url_for('dashboard'))
    form = FarmerOrConsumer()
    if form.validate_on_submit():
        if form.choice.data == True:
            session['consumer'] = True
            return redirect(url_for('consumer_register'))
        else:
            session['consumer'] = False
            return redirect(url_for('farmer_register'))
    return render_template('farmer_or_consumer.html', form=form)


@app.route('/otp_form/<id>', methods=['GET', 'POST'])
def otp_form(id):
    name=''
    email=''
    curr = mysql.connection.cursor()
    print(session['consumer'],'Session')
    if session['consumer']:
        query = ''' SELECT firstname,otp,emailid FROM consumer WHERE idconsumer='{}' '''.format(
            id)
        curr.execute(query)
        data = curr.fetchall()
        name = data[0][0]
        otp = data[0][1]
        email = data[0][2]
        send_email_verify_OTP_message(otp, name, email)
    else:
        query = ''' SELECT firstname,otp,emailid FROM farmer WHERE idfarmer={} '''.format(
            id)
        curr.execute(query)
        data = curr.fetchall()
        print(data)
        name = data[0][0]
        otp = data[0][1]
        email = data[0][2]
        send_email_verify_OTP_message(otp, name, email)
    form = OTPForm()
    if form.validate_on_submit():
        if session['consumer']:
            curr = mysql.connection.cursor()
            query = ''' UPDATE CONSUMER SET verifiedemail='1' WHERE idconsumer='{}' '''.format(
                session['id'])
            curr.execute(query)
            mysql.connection.commit()
            curr.close()
            session['id'] = None
            return redirect(url_for('consumer_login'))
        else:
            curr = mysql.connection.cursor()
            query = ''' UPDATE FARMER SET verifiedemail='1' WHERE idfarmer='{}' '''.format(
                session['id'])
            curr.execute(query)
            mysql.connection.commit()
            curr.close()
            session['id'] = None
            return redirect(url_for('farmer_login'))
    return render_template('otp-form.html', form=form,name=name,email=email)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['login'] = False
    session['id'] = None
    print('Hello World')
    return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if session['login']:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email=form.email.data
    return render_template('reset_password_request.html', form=form)

def generate_farmer_id():
    curr = mysql.connection.cursor()
    id = randint(0, 99999)
    curr.execute('SELECT * FROM FARMER WHERE idFarmer= {}'.format(id))
    data = curr.fetchall()
    while data:
        id = randint(0, 99999)
        curr.execute('SELECT * FROM FARMER WHERE idFarmer= {}'.format(id))
        data = curr.fetchall()
    curr.close()
    return id


def generate_consumer_id():
    curr = mysql.connection.cursor()
    id = randint(0, 99999)
    curr.execute('SELECT * FROM CONSUMER WHERE idConsumer= {}'.format(id))
    data = curr.fetchall()
    while data:
        id = randint(100000, 199999)
        curr.execute('SELECT * FROM CONSUMER WHERE idConsumer= {}'.format(id))
        data = curr.fetchall()
    curr.close()
    return id


def generate_otp():
    return randint(10000, 999999)
