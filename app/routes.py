from flask import render_template, request, redirect, url_for, session, flash,jsonify
from app import app, mysql
from app.forms import FarmerRegistrationForm, FarmerLoginForm, FarmerOrConsumer, ConsumerLoginForm, ConsumerRegistrationForm, OTPForm, ResetPasswordRequestForm, ResetPasswordForm,PurchaseItem,BrowseItems,OngoingPurchases,SendItem,ItemReceived,SendMessage
from app.cities import cities
from app.password_check import set_password
from app.email import send_email_verify_OTP_message, send_password_reset_email
from random import randint
import jwt
from werkzeug.utils import secure_filename
import os


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
        session['consumer'] = True
        curr = mysql.connection.cursor()
        query = ''' INSERT INTO CONSUMER (idconsumer,firstname,lastname,emailid,mobileno,password_hash,city,verifiedemail,OTP) VALUES('{}','{}','{}','{}','{}','{}','{}',0,{})'''.format(
            idConsumer, firstname, lastname, email, mobile, password_hash, city, OTP)
        print(query)
        curr.execute(query)
        mysql.connection.commit()
        curr.close()
        print(idConsumer)
        return redirect(url_for('otp_form', id=idConsumer))
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
    email=''
    mobileno=''
    word=""
    city=''
    profile_url=''
    if id:
        curr = mysql.connection.cursor()
        if type:
            query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM consumer WHERE idConsumer={} '''.format(id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1]) == 0:
                return redirect(url_for('otp_form', id=session['id']))
            if data[0][0]:
                name = data[0][0]+" "+data[0][2]
                email=data[0][3]
                mobileno=data[0][4]
                city=data[0][5]
                profile_url=data[0][6]
        else:
            query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM farmer WHERE idfarmer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1]) == 0:
                return redirect(url_for('otp_form', id=session['id']))
            if data[0][0]:
                name = data[0][0]+" "+data[0][2]
                email = data[0][3]
                mobileno = data[0][4]
                city = data[0][5]
                profile_url = data[0][6]
        if session['consumer']:
            word="Consumer"
        else:
            word="Farmer"
    return render_template('dashboard.html', login=session['login'], name=name,email=email,mobileno=mobileno,city=city,profile_url=profile_url,cus_type=word)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session['login']:
        return redirect(url_for('dashboard'))
    form = FarmerOrConsumer()
    if form.validate_on_submit():
        if form.choice.data == True:
            session['consumer'] = True
            return redirect(url_for('consumer_login'))
        else:
            session['consumer'] = False
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
    name = ''
    email = ''
    curr = mysql.connection.cursor()
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
            flash(
                "You are successfully registered as a consumer now.You can login with your credentials")
            return redirect(url_for('consumer_login'))
        else:
            curr = mysql.connection.cursor()
            query = ''' UPDATE FARMER SET verifiedemail='1' WHERE idfarmer='{}' '''.format(
                session['id'])
            curr.execute(query)
            mysql.connection.commit()
            curr.close()
            session['id'] = None
            flash(
                "You are successfully registered as a farmer now.You can login with your credentials")
            return redirect(url_for('farmer_login'))
    return render_template('otp-form.html', form=form, name=name, email=email)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['login'] = False
    session['id'] = None
    flash('Successfully Logged Out of Your Account')
    return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if session['login']:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        curr = mysql.connection.cursor()
        if session['consumer']:
            query = '''SELECT idconsumer,firstname FROM consumer WHERE EMAILID='{}' '''.format(
                email)
            curr.execute(query)
            data = curr.fetchall()
            if data:
                id = data[0][0]
                name = data[0][1]
                send_password_reset_email(id, email, name)
                return redirect(url_for('consumer_login'))
        else:
            query = '''SELECT idfarmer,firstname FROM farmer WHERE EMAILID='{}' '''.format(
                email)
            curr.execute(query)
            data = curr.fetchall()
            if data:
                id = data[0][0]
                name = data[0][1]
                send_password_reset_email(id, email, name)
                return redirect(url_for('farmer_login'))
        flash("Check your email for the further instructions")
    return render_template('reset_password_request.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if session['login']:
        return redirect(url_for('index'))
    try:
        id = jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')[
            'reset_password']
    except:
        print('')
    curr = mysql.connection.cursor()
    query = ''' SELECT firstname FROM farmer WHERE idfarmer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if not data:
        session['consumer'] = True
        query = ''' SELECT firstname FROM consumer WHERE idconsumer={} '''.format(
            id)
        curr.execute(query)
        data = curr.fetchall()
        if not data:
            return redirect(url_for(index))
        name = data[0][0]
    name = data[0][0]
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        password_hash = set_password(password)
        if session['consumer']:
            query = '''UPDATE consumer SET password_hash='{}' WHERE idconsumer={} '''.format(
                password_hash, id)
            curr.execute(query)
            mysql.connection.commit()
        else:
            query = '''UPDATE farmer SET password_hash='{}' WHERE idfarmer={} '''.format(
                password_hash, id)
            curr.execute(query)
            mysql.connection.commit()
        return redirect(url_for('login'))
        flash("Your password has been reset successfully")
    return render_template('reset_password.html', name=name, form=form)


# Profile Pic Upload
@app.route('/upload_pp', methods=['POST', 'GET'])
def upload_pp():
    print("Hello World")
    if request.method == 'POST':
        file=request.files['img-file']
        if file.filename=='':
            return
        filename=secure_filename(file.filename).split('.')
        filename = '{}_pp.{}'.format(session['id'],filename[-1])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        curr=mysql.connection.cursor()
        if session['consumer']:
            query='''UPDATE consumer SET profile_pic='{}' WHERE idconsumer={}'''.format(filename,session['id'])
            curr.execute(query)
            mysql.connection.commit()
        else:
            query = '''UPDATE farmer SET profile_pic='{}' WHERE idfarmer={}'''.format(filename, session['id'])
            curr.execute(query)
            mysql.connection.commit()
        return redirect(url_for('dashboard'))


@app.route('/purchase_items',methods=['POST','GET'])
def purchase_items():
    if not session['login']:
        return redirect(url_for('login'))
    if not ['consumer']:
        flash("Farmers cannot purchase items")
        return redirect(url_for('index'))
    id = session.get('id', None)
    form=PurchaseItem()
    if form.validate_on_submit():
        qty=form.quantity.data
        item=request.form['item']
        date=request.form['date']
        flash("Successfully placed an order for {} kgs of {} by {}".format(qty,item,date))
        curr=mysql.connection.cursor()
        query=''' call get_item_id('{}') '''.format(item)
        curr.execute(query)
        data=curr.fetchall()
        item_id=data[0][0]
        query=''' INSERT INTO c_req(c_id,i_id,qty,date) values({},{},{},'{}') '''.format(id,item_id,qty,date)
        curr.execute(query)
        mysql.connection.commit()
        return redirect(url_for('dashboard'))
    curr=mysql.connection.cursor()
    query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM consumer WHERE idConsumer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if int(data[0][1]) == 0:
        return redirect(url_for('otp_form', id=session['id']))
    name=""
    email=""
    mobileno=""
    city=""
    profile_url=""
    if data[0][0]:
        name = data[0][0]+" "+data[0][2]
        email = data[0][3]
        mobileno = data[0][4]
        city = data[0][5]
        profile_url = data[0][6]
    query=''' CALL get_items() '''
    curr.execute(query)
    data = curr.fetchall()
    items=[]
    for row in data:
        for column in row:
            items.append(column)
    return render_template('purchase_items.html', login=session['login'],form=form, name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url,cus_type="Consumer",items=items)

@app.route('/browse_orders',methods=['POST','GET'])
def browse_orders():
    if not session['login']:
        return redirect(url_for('login'))
    if session['consumer']:
        flash("Consumers cannot browse Orders")
        return redirect(url_for('index'))
    id = session.get('id', None)
    curr = mysql.connection.cursor()
    form=BrowseItems()
    if form.validate_on_submit():
        bid_price=int(form.price.data)
        r_id=request.form['r_id']
        query='''SELECT i_id,qty from c_req WHERE r_id={}'''.format(r_id)
        curr.execute(query)
        data=curr.fetchall()
        query = ''' CALL get_price({},{})'''.format(data[0][0], data[0][1])
        curr.execute(query)
        data = curr.fetchall()
        if bid_price<data[0][0]:
            flash("You cannot bid for a price lower than the minumum mentioned price")
            return redirect(url_for('browse_orders'))
        query='''INSERT into f_bid(f_id,r_id,cost_bid) VALUES({},{},{}) '''.format(id,r_id,bid_price)
        curr.execute(query)
        mysql.connection.commit()
        flash("The consumer has been informed about your bidding.Stay tuned!!!")
        return redirect(url_for('dashboard'))
    query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM farmer WHERE idFarmer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if int(data[0][1]) == 0:
        return redirect(url_for('otp_form', id=session['id']))
    name = ""
    email = ""
    mobileno = ""
    city = ""
    profile_url = ""
    if data[0][0]:
        name = data[0][0]+" "+data[0][2]
        email = data[0][3]
        mobileno = data[0][4]
        city = data[0][5]
        profile_url = data[0][6]
    query='''CALL browse_orders({})'''.format(id)
    curr.execute(query)
    data=curr.fetchall()
    orders=[]
    cost=[]
    for row in data:
        item=[]
        for col in row:
            item.append(col)
        query=''' CALL get_price({},{})'''.format(item[1],item[5])
        curr.execute(query)
        data = curr.fetchall()
        item.append(data[0][0])
        orders.append(item)
    print(orders)
    return render_template('browse_orders.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type="Farmer",orders=orders,form=form)

@app.route('/ongoing_purchases',methods=['GET','POST'])
def ongoing_purchases():
    if not session['login']:
        return redirect(url_for('login'))
    if not session['consumer']:
        flash("Farmers cannot browse through On going Purchases")
        return redirect(url_for('index'))
    id = session.get('id', None)
    curr = mysql.connection.cursor()
    form = OngoingPurchases()
    if form.validate_on_submit():
        bid_id = form.bid_id.data
        query='''CALL get_f_bid_details({})'''.format(bid_id)
        curr.execute(query)
        data=curr.fetchall()
        query='''INSERT INTO acc_req(bid_id,req_id,f_id,cost_bid) VALUES({},{},{},{})'''.format(bid_id,data[0][1],data[0][0],data[0][2])
        curr.execute(query)
        mysql.connection.commit()
        flash("You will be connected to the farmer in a while!!!\nThanks for using Farmer2Consumer")
        return redirect(url_for('dashboard'))
    query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM consumer WHERE idConsumer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if int(data[0][1]) == 0:
        return redirect(url_for('otp_form', id=session['id']))
    name = ""
    email = ""
    mobileno = ""
    city = ""
    profile_url = ""
    if data[0][0]:
        name = data[0][0]+" "+data[0][2]
        email = data[0][3]
        mobileno = data[0][4]
        city = data[0][5]
        profile_url = data[0][6]
    query='''CALL get_cons_req({})'''.format(id)
    curr.execute(query)
    data=curr.fetchall()
    print(data)
    cons_reqs=[]
    for row in data:
        for col in row:
            cons_reqs.append(col)
    req_details=[]
    for req in cons_reqs:
        item_details=[]
        query='''CALL get_req_details({})'''.format(req)
        curr.execute(query)
        print(query)
        data=curr.fetchall()
        print(data)
        item_details.append(data[0][0])
        item_details.append(data[0][1])
        item_details.append(data[0][2])
        query ='''CALL farmer_count_min_req_id({},{})'''.format(id,req)
        curr.execute(query)
        data=curr.fetchall()
        item_details.append(data[0][0])
        item_details.append(data[0][1])
        req_details.append(item_details)
    req_farmer_details=[]
    for req in cons_reqs:
        single_req=[]
        query='''CALL ongoing_purchases({},{})'''.format(id,req)
        curr.execute(query)
        data=curr.fetchall()
        for row in data:
            row_item=[]
            for col in row:
                row_item.append(col)
            single_req.append(row_item)
        req_farmer_details.append(single_req)
    return render_template('ongoing_purchases.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type="Consumer",cons_reqs=cons_reqs,req_details=req_details,req_farmer_details=req_farmer_details,form=form)


@app.route('/accepted_orders',methods=['GET','POST'])
def accepted_orders():
    if not session['login']:
        return redirect(url_for('login'))
    if session['consumer']:
        flash("Consumers cannot browse through accepted orders")
        return redirect(url_for('index'))
    id = session.get('id', None)
    curr = mysql.connection.cursor()
    form=SendItem()
    if form.validate_on_submit():
        bid_id=form.bid_id.data
        query='''UPDATE acc_req SET sent=1 WHERE bid_id={}'''.format(bid_id)
        curr.execute(query)
        mysql.connection.commit() 
        flash("You have to send the items to the consumer.Once the consumer receives the items.The transaction will be completed")
        return redirect(url_for('dashboard'))
    query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM farmer WHERE idfarmer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if int(data[0][1]) == 0:
        return redirect(url_for('otp_form', id=session['id']))
    name = ""
    email = ""
    mobileno = ""
    city = ""
    profile_url = ""
    if data[0][0]:
        name = data[0][0]+" "+data[0][2]
        email = data[0][3]
        mobileno = data[0][4]
        city = data[0][5]
        profile_url = data[0][6]
    query ='''CALL get_accepted_request_details({})'''.format(id)
    curr.execute(query)
    data=curr.fetchall()
    accepts=[]
    for row in data:
        item=[]
        for col in row:
            item.append(col)
        accepts.append(item)
    print(accepts)
    return render_template('accepted_orders.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type="Farmer",accepts=accepts,form=form)

@app.route('/finalize_purchases',methods=['GET','POST'])
def finalize_purchases():
    if not session['login']:
        return redirect(url_for('login'))
    if not session['consumer']:
        flash("Farmers cannot finalize the purchases")
        return redirect(url_for('index'))
    id = session.get('id', None)
    curr = mysql.connection.cursor()
    form=ItemReceived()
    if form.validate_on_submit():
        print("Hello")
        bid_id=form.bid_id.data
        print(bid_id)
        query='''UPDATE acc_req SET received=1 WHERE bid_id={}'''.format(bid_id)
        curr.execute(query)
        mysql.connection.commit()
        flash("The transaction has been completed")
        return redirect(url_for('dashboard'))
    query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM consumer WHERE idconsumer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if int(data[0][1]) == 0:
        return redirect(url_for('otp_form', id=session['id']))
    name = ""
    email = ""
    mobileno = ""
    city = ""
    profile_url = ""
    if data[0][0]:
        name = data[0][0]+" "+data[0][2]
        email = data[0][3]
        mobileno = data[0][4]
        city = data[0][5]
        profile_url = data[0][6]
    query ='''CALL finalize_purchase({})'''.format(id)
    curr.execute(query)
    data=curr.fetchall()
    orders=[]
    for row in data:
        item=[]
        for col in row:
            item.append(col)
        orders.append(item)
        print(item[6])
    return render_template('finalize_purchases.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type="Consumer",orders=orders,form=form)


@app.route('/chatbox/<id>',methods=['GET','POST'])
def chatbox(id):
    if not session['login']:
        return redirect(url_for('login'))
    bid_id=id
    login_id=session['id']
    curr=mysql.connection.cursor()
    query='''CALL get_c_f_id({})'''.format(bid_id)
    print(query)
    curr.execute(query)
    data=curr.fetchall()
    name=''
    if login_id!=data[0][0] and  login_id!=data[0][1]:
        flash("You are trying to access an unathorised page")
        return redirect(url_for('dashboard'))
    if session['consumer']:
        query='''SELECT firstname from farmer where idfarmer={}'''.format(data[0][0])
        print(query)
        curr.execute(query)
        data=curr.fetchall()
        name=data[0][0]
        query='''CALL delete_consumer_notification({})'''.format(bid_id)
        print(query)
        curr.execute(query)
        mysql.connection.commit()
    else:
        query = '''SELECT firstname from consumer where idconsumer={}'''.format(data[0][1])
        print(query)
        curr.execute(query)
        data = curr.fetchall()
        name = data[0][0]
        query = '''CALL delete_farmer_notification({})'''.format(bid_id)
        print(query)
        curr.execute(query)
    mysql.connection.commit()
    query='''CALL get_messages({})'''.format(bid_id)
    print(query)
    curr.execute(query)
    data=curr.fetchall()
    details=[]
    for row in data:
        text_details=[]
        text_details.append(row[0])
        if(session['consumer']):
            if(row[1]):
                text_details.append(0)
            else:
                text_details.append(1)
        else:
            if(row[1]):
                text_details.append(1)
            else:
                text_details.append(0)
        details.append(text_details)
    order_details=[]
    query='''CALL get_order_details({})'''.format(bid_id)
    print(query)
    curr.execute(query)
    data=curr.fetchall()
    for row in data:
        for col in row:
            order_details.append(col)
    form=SendMessage()
    if form.validate_on_submit():
        text=form.text.data
        f_or_c=1 if session['consumer'] else 0
        query ='''INSERT INTO chats(bid_id,text,f_or_c,date) values({},"{}",{},current_timestamp())'''.format(bid_id,text,f_or_c)
        curr.execute(query)
        mysql.connection.commit()
        return redirect(url_for('chatbox',id=bid_id))
    
    return render_template('chatbox.html',text_details=details,order_details=order_details,form=form,name=name)

@app.route('/past_purchases',methods=['GET','POST'])
def past_purchases():
    if not session['login']:
        return redirect(url_for('login'))
    if not session['consumer']:
        flash("You are not a consumer")
        return redirect(url_for('index'))
    id = session.get('id', None)
    curr = mysql.connection.cursor()
    query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM consumer WHERE idconsumer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if int(data[0][1]) == 0:
        return redirect(url_for('otp_form', id=session['id']))
    name = ""
    email = ""
    mobileno = ""
    city = ""
    profile_url = ""
    if data[0][0]:
        name = data[0][0]+" "+data[0][2]
        email = data[0][3]
        mobileno = data[0][4]
        city = data[0][5]
        profile_url = data[0][6]
    query = '''CALL past_purchases({})'''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    orders = []
    for row in data:
        item = []
        for col in row:
            item.append(col)
        orders.append(item)
        print(item[6])
    return render_template('past_purchases.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type="Consumer",orders=orders)


@app.route('/past_orders', methods=['GET', 'POST'])
def past_orders():
    if not session['login']:
        return redirect(url_for('login'))
    if session['consumer']:
        flash("You are not a farmer")
        return redirect(url_for('index'))
    id = session.get('id', None)
    curr = mysql.connection.cursor()
    query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM farmer WHERE idfarmer={} '''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    if int(data[0][1]) == 0:
        return redirect(url_for('otp_form', id=session['id']))
    name = ""
    email = ""
    mobileno = ""
    city = ""
    profile_url = ""
    if data[0][0]:
        name = data[0][0]+" "+data[0][2]
        email = data[0][3]
        mobileno = data[0][4]
        city = data[0][5]
        profile_url = data[0][6]
    query = '''CALL past_orders({})'''.format(id)
    curr.execute(query)
    data = curr.fetchall()
    orders = []
    for row in data:
        item = []
        for col in row:
            item.append(col)
        orders.append(item)
        print(item[6])
    return render_template('past_orders.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type="Farmer", orders=orders)


@app.route('/market_prices',methods=['GET','POST'])
def market_prices():
    if not session['login']:
        return redirect(url_for('login'))
    id = session.get('id', None)
    type = session.get('consumer', None)
    name = 'User'
    email = ''
    mobileno = ''
    word = ""
    city = ''
    profile_url = ''
    if id:
        curr = mysql.connection.cursor()
        if type:
            query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM consumer WHERE idConsumer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1]) == 0:
                return redirect(url_for('otp_form', id=session['id']))
            if data[0][0]:
                name = data[0][0]+" "+data[0][2]
                email = data[0][3]
                mobileno = data[0][4]
                city = data[0][5]
                profile_url = data[0][6]
        else:
            query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM farmer WHERE idfarmer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1]) == 0:
                return redirect(url_for('otp_form', id=session['id']))
            if data[0][0]:
                name = data[0][0]+" "+data[0][2]
                email = data[0][3]
                mobileno = data[0][4]
                city = data[0][5]
                profile_url = data[0][6]
        if session['consumer']:
            word = "Consumer"
        else:
            word = "Farmer"
        query='''call market_prices()'''
        curr.execute(query)
        data=curr.fetchall()
        market=[]
        for row in data:
            item=[]
            for col in row:
                item.append(col)
            market.append(item)
    return render_template('market_prices.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type=word,market=market)

@app.route('/about',methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/contact',methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/products',methods=['GET'])
def products():
    return render_template('products.html')

@app.route('/get_notification_count',methods=['GET'])
def get_notification_count():
    curr=mysql.connection.cursor()
    res={}
    if session['login']:
        if session['consumer']:
            query='''CALL get_consumer_n_count({})'''.format(session['id'])
            curr.execute(query)
            data=curr.fetchall()
            print("consumer")
        else:
            query='''CALL get_farmer_n_count({})'''.format(session['id'])
            curr.execute(query)
            data=curr.fetchall()
            print("farmer")
        res['count']=data[0][0] if data[0][0] else ""
        print(res['count'])
        return jsonify(res)
    res['count']=""
    return jsonify(res)

@app.route('/notifications',methods=['GET','POST'])
def notifications():
    if not session['login']:
        return redirect(url_for('login'))
    id = session.get('id', None)
    type = session.get('consumer', None)
    name = 'User'
    email = ''
    mobileno = ''
    word = ""
    city = ''
    profile_url = ''
    notify=[]
    if session['login']:
        curr = mysql.connection.cursor()
        if type:
            query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM consumer WHERE idConsumer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1]) == 0:
                return redirect(url_for('otp_form', id=session['id']))
            if data[0][0]:
                name = data[0][0]+" "+data[0][2]
                email = data[0][3]
                mobileno = data[0][4]
                city = data[0][5]
                profile_url = data[0][6]
        else:
            query = ''' SELECT firstname,verifiedemail,lastname,emailid,mobileno,city,profile_pic FROM farmer WHERE idfarmer={} '''.format(
                id)
            curr.execute(query)
            data = curr.fetchall()
            if int(data[0][1]) == 0:
                return redirect(url_for('otp_form', id=session['id']))
            if data[0][0]:
                name = data[0][0]+" "+data[0][2]
                email = data[0][3]
                mobileno = data[0][4]
                city = data[0][5]
                profile_url = data[0][6]
        if session['consumer']:
            word = "Consumer"
            query='''CALL get_consumer_notifications({})'''.format(id)
            print(query)
            curr.execute(query)
            data=curr.fetchall()
            for row in data:
                val=[]
                for col in row:
                    val.append(col)
                notify.append(val)
        else:
            word = "Farmer"
            query='''CALL get_farmer_notifications({})'''.format(id)
            curr.execute(query)
            print(query)
            data = curr.fetchall()
            print(data)
            for row in data:
                val = []
                for col in row:
                    val.append(col)
                notify.append(val)  
    return render_template('notifications.html', login=session['login'], name=name, email=email, mobileno=mobileno, city=city, profile_url=profile_url, cus_type=word,notify=notify)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
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
    return randint(100000, 999999)
