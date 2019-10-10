from flask import render_template, request, redirect, url_for
from app import app, mysql
from app.forms import FarmerRegistrationForm, FarmerLoginForm,FarmerOrConsumer,ConsumerLoginForm,ConsumerRegistrationForm,OTPForm
from app.cities import cities
from app.password_check import set_password
from random import randint


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    print('Hello World')
    return render_template('index.html')


@app.route('/farmer_register', methods=['GET', 'POST'])
def farmer_register():
    form = FarmerRegistrationForm()
    if form.validate_on_submit():
        idFarmer = generate_farmer_id()
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        mobile = form.mobile.data
        city = request.form.get('cities')
        password_hash = set_password(form.password.data)
        curr = mysql.connection.cursor()
        query = ''' INSERT INTO FARMER(idfarmer,firstname,lastname,emailid,mobileno,password_hash,city,verifiedemail) VALUES('{}','{}','{}','{}','{}','{}','{}',0)'''.format(
            idFarmer, firstname, lastname, email, mobile, password_hash, city)
        print(query)
        curr.execute(query)
        mysql.connection.commit()
        curr.close()
    return render_template('farmer_register.html', form=form, cities=sorted(cities))


@app.route('/consumer_register', methods=['GET', 'POST'])
def consumer_register():
    form = ConsumerRegistrationForm()
    if form.validate_on_submit():
        idConsumer = generate_consumer_id()
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        mobile = form.mobile.data
        city = request.form.get('cities')
        password_hash = set_password(form.password.data)
        curr = mysql.connection.cursor()
        query = ''' INSERT INTO CONSUMER (idconsumer,firstname,lastname,emailid,mobileno,password_hash,city,verifiedemail) VALUES('{}','{}','{}','{}','{}','{}','{}',0)'''.format(
            idConsumer, firstname, lastname, email, mobile, password_hash, city)
        print(query)
        curr.execute(query)
        mysql.connection.commit()
        curr.close()
    return render_template('consumer_register.html', form=form, cities=sorted(cities))


@app.route('/farmer_login', methods=['GET', 'POST'])
def farmer_login():
    form = FarmerLoginForm()
    print(form.password.data)
    if form.validate_on_submit():
        return redirect(url_for('dashboard'))
    return render_template('farmer_login.html', form=form)


@app.route('/consumer_login', methods=['GET', 'POST'])
def consumer_login():
    form = ConsumerLoginForm()
    print(form.password.data)
    if form.validate_on_submit():
        return redirect(url_for('dashboard'))
    return render_template('consumer_login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/login',methods=['GET','POST'])
def login():
    form=FarmerOrConsumer()
    if form.validate_on_submit():
        if form.choice.data==True:
            return redirect(url_for('consumer_login'))
        else:
            return redirect(url_for('farmer_login'))
    return render_template('farmer_or_consumer.html',form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = FarmerOrConsumer()
    if form.validate_on_submit():
        if form.choice.data == True:
            return redirect(url_for('consumer_register'))
        else:
            return redirect(url_for('farmer_register'))
    return render_template('farmer_or_consumer.html', form=form)

@app.route('/otp_form',methods=['GET','POST'])
def otp_form():
    form=OTPForm()
    if form.validate_on_submit():
        print(form.a.data, form.b.data, form.c.data,
              form.d.data, form.e.data, form.f.data,)
    return render_template('otp-form.html',form=form)




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
    curr.execute('SELECT * FROM CONSUMER WHERE idFarmer= {}'.format(id))
    data = curr.fetchall()
    while data:
        id = randint(0, 99999)
        curr.execute('SELECT * FROM CONSUMER WHERE idFarmer= {}'.format(id))
        data = curr.fetchall()
    curr.close()
    return id
