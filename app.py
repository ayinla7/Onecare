# importing flask module fro
from flask import (Flask, render_template, request, redirect,send_file, session, jsonify, json, flash)
from flaskext.mysql import MySQL
from flask_qrcode import QRcode
from flask_bcrypt import Bcrypt
import requests # for API example
import datetime

bcrypt = Bcrypt()
mysql = MySQL()

# initializing a variable of Flask
app = Flask(__name__)

#Initializing QRCode
qrcode = QRcode(app)
app.secret_key = 'CouldbeAnything'     #you can set any secret key but remember it should be secret

url_covid='https://api.covid19api.com/summary/' #NHS Covid api link


 # MySQL configurations
 # USing SQL WORKBENCH
 app.config['MYSQL_DATABASE_USER'] = 'root'
 app.config['MYSQL_DATABASE_PASSWORD'] = ''
 app.config['MYSQL_DATABASE_DB'] = 'OneCare'
 app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

# Accessing the landing page and updating datebase and Current date
@app.route('/', methods=["GET"])
def home():
    date()
    update()
    return render_template('index.html')

#Generate BARCODE
@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    # please get /qrcode?data=<qrcode_data>
    data = request.args.get("data", "")
    return send_file(qrcode(data, mode="raw"), mimetype="image/png")
#################################################

# Open Staff profile
@app.route('/profilest')
def profilestaff():
    if 'staffuser' in session: # here we are checking whether the user is logged in or not
        return render_template("profilestaff.html", gpd=gpds(),
                           getassignments=getassignmentsbasic2(session['staffId']),
                           countassignments=countassignmentsbasic2(session['staffId']),
                               title="Care-giver Profile", command="/profilest")

    return render_template("page-404.html")  # if the user is not in the session

#View Staff profile
@app.route('/loginstaff', methods=['POST', 'GET'])
def loginstaff():
    clearSession() #Clear previous sessions
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM staffsdetails WHERE username=%s AND status="ACTIVE"',
                    (username)) #count all with same username and Actice status
        count = cur.fetchall()

        con.commit()

        if count[-1][-1] > 0:
            cur.execute('SELECT password FROM staffsdetails WHERE username=%s AND status="ACTIVE"',
                        (username)) #Select password with same username and Actice status
            hash = cur.fetchall()

            authpass = bcrypt.check_password_hash(hash[-1][-1], password)  #Compare Hashed password to newly inputed password
            con.commit()
            if authpass:
                cur.execute('select staffId,gpId,email from staffsdetails WHERE username=%s AND status="ACTIVE"',
                        (username)) #Select staffId,gpId,email with same username and Actice status

                gp = cur.fetchall()
                con.commit()

                session['email'] = gp[-1][2]
                session['staffId'] = gp[-1][0]
                session['gpId'] = gp[-1][1]
                session['staffuser'] = username
                session['logged'] = "staff"

                msg = "<h1>You are signed In as Staff</h1>"
                return profilestaff() #Call Function to open staff profile
            else:
                msg = "Incorrect password or username. Try Again!"
                flash(msg, "error")
                return loginpages("loginstaffpage", "","Care-giver Sign in") # Wrong password entered
        else:
            #print("Failed!")
            msg = "Incorrect password or username. Try Again!"
            flash(msg, "error")
            return loginpages("loginstaffpage", "","Care-giver Sign in") # Wrong password entered

        con.close()


#View Patients profile
@app.route('/profile', methods=['POST', 'GET'])
def profile():
    clearSession() #Clear previous sessions
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM patientsdetails WHERE username=%s AND status="ACTIVE"',
                    (username)) #count all with same username and Actice status
        count = cur.fetchall()

        con.commit()

        if count[-1][-1] > 0:
            cur.execute('SELECT password FROM patientsdetails WHERE username=%s AND status="ACTIVE"',
                        (username)) #Select password with same username and Actice status
            hash = cur.fetchall()

            authpass = bcrypt.check_password_hash(hash[-1][-1], password) #Compare Hashed password to newly inputed password
            con.commit()
            if authpass:
                session['patientuser'] = username
                cur.execute('SELECT gpid,nhsid FROM patientsdetails WHERE username=%s AND status="ACTIVE"',
                            (username)) #Select gpId,nhsId with same username and Actice status
                result = cur.fetchall()
                session['gpId'] = result[0][0]
                session['nhsId'] = result[0][1]
                session['logged'] = "patient"


                return profilepatient() #Call Function to open patient profile
            else:
                msg = "Incorrect password or username. Try Again!"
                flash(msg, "error")
                return loginpages("loginPage", "","Patient Sign in")  # Wrong password entered

        else:
            msg = "Incorrect password or username. Try Again!"
            flash(msg, "error")
            return loginpages("loginPage", "", "Patient Sign in")  # Wrong password entered
        con.close()
    return render_template("page-404.html")

#Method to open Patient Profile
@app.route('/profile')
def profilepatient():
    if 'patientuser' in session:         # here we are checking whether the user is logged in or not

        return render_template("profilepatient.html", gpd=gpd(),
                           getassignments=getassignmentsbasic(session['nhsId']),
                           countassignments=countassignmentsbasic(session['nhsId']),
                               title="Patient Profile", command="/profile")
    return render_template("page-404.html")  # if the user is not in the session





def loginpages(page,msg,title):
    return render_template('/'+ page + '.html', msg=msg, title=title)

@app.route('/loginstaffpage')
def loginstaffpage():
    return loginpages("loginstaffpage", "", "Care-giver Sign in")

@app.route('/loginPage')
def loginPage():
    return loginpages("loginPage", "", "Patients Sign in")

@app.route('/logingppage')
def logingppage():
    return loginpages("logingp", "", "Admin Sign in")
##############################

@app.route('/registergp')
def registergp():
    return render_template('/registergp.html')

@app.route('/registerpatient')
def registerpatient():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM gpdetails WHERE status="ACTIVE"')
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute('select gpId,gpName from gpdetails WHERE status="ACTIVE"')

        gpnames = cur.fetchall()
        con.commit()

        #print(gpnames)
        return render_template('registerpatient.html', gpnames=gpnames, title="Patient Registration")
    else:
        return "<h1>GPs do not exist yet, Try later.</h1>"
    con.close()

@app.route('/register')
def register():
    return render_template('/register.html')

@app.route('/registerstaff')
def registerstaff():
    if 'user' in session:
        if 'gpname' in session:
            return render_template('home/registerstaff.html', user=session['user'], gpname=session['gpname'])
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        countcovid()
        return render_template("home/dashboard.html", user=session['user'],
                               gpname=session['gpname'], countpatients=countpatients(),
                               countstaffs=countstaffs(), countcovid=countcovid())

        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

@app.route('/staffview')
def staffview():
    if 'user' in session:
        return render_template("home/staffview.html", user=session['user'],
                               gpname=session['gpname'], getstaffs=getstaffs(), countstaffs=countstaffs() )
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

@app.route('/patientview')
def patientview():
    if 'user' in session:
        return render_template("home/patientview.html", getpatients=getpatients(), countpatients=countpatients() )
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session


#Method to open Patient Profile
@app.route('/profile')
def profilepatient():
    if 'patientuser' in session:         # here we are checking whether the user is logged in or not

        return render_template("profilepatient.html", gpd=gpd(),
                           getassignments=getassignmentsbasic(session['nhsId']),
                           countassignments=countassignmentsbasic(session['nhsId']),
                               title="Patient Profile", command="/profile")
    return render_template("page-404.html")  # if the user is not in the session


@app.route('/records')
def records():
    if 'patientuser' in session:
        return render_template('records.html', getmedpatients=getmedpatients(session['nhsId']),
                               countmedpatients=countmedpatients(session['nhsId']),
                            title="Medical Records", command="/profile")

        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session


@app.route('/view', methods=['POST', 'GET'])
def view():
    if 'staffuser' in session:
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM assignstaff WHERE dateassigned=%s AND status=%s AND staffid=%s',
                    (date(), "ASSIGNED", session['staffId']))
        count = cur.fetchall()
        con.commit()
        if count[0][0] > 0:
            cur.execute('SELECT nhsid FROM assignstaff WHERE dateassigned=%s AND status=%s AND staffid=%s',
                        (date(), "ASSIGNED",session['staffId']))
            result = cur.fetchall()
            con.commit()
            session['nhsId'] =  result[0][0]
            # #print("View")

            # #print("staff is " + session['staffId'])
            # #print("patient is " + session['nhsId'])

            return render_template('viewassignment.html', getmedpatients=getmedpatients(session['nhsId']),
                                   countmedpatients=countmedpatients(session['nhsId']),
                                   title="Medication", command="/profilest")
        else:
            msg = "No Assignments available!"
            flash(msg, "error")
            return redirect("/profilest")

    return render_template("page-404.html")  # if the user is not in the session


@app.route('/settings')
def settings():
    if 'user' in session:
        return render_template("home/settings.html", gpnames=gpnames(),
                               staffId=unassignedstaffs(),nhsId=unassignedpatients(),
                               getassignments=getassignments(), countassignments=countassignments())
        # here we are checking whether the user is logged in or not
    return render_template("page-404.html")  # if the user is not in the session

@app.route('/index')
def index():
    return render_template('/index.html')

#creating route for logging out
@app.route('/logout')
def logout():
    clearSession()
    # here we are checking whether the user is logged in or not
    return redirect('/')  # if the user is not in the session

#Add NEW GP
@app.route('/addgp', methods=['POST', 'GET'])
def addgp():
    date_time = ""
    if request.method == 'POST':
        con = mysql.connect()

        gpId = request.form['gpId']
        gpname = request.form['gpname']
        address = request.form['address']
        city = request.form['city']
        postcode = request.form['postcode']
        phone = request.form['phone']
        username = request.form['username']
        email = request.form['email']
        password = request.form['pass']
        dateadded = date()
        status = "ACTIVE"

        # #print(date())
        cur = con.cursor()

        cur.execute('SELECT count(*) FROM gpdetails WHERE gpId=%s ',
                    (gpId))
        count = cur.fetchall()

        con.commit()
        #print(count[-1][-1])
        if count[-1][-1] == 0:
            cur.execute(
                'INSERT INTO gpdetails (gpId, gpname, address, city, postcode, phone, username, email, password, dateadded, status)VALUES( %s, %s,  %s, %s, %s,  %s, %s , %s, %s,  %s, %s)',
                (gpId, gpname, address, city, postcode, phone, username, email, password, dateadded, status))

            con.commit()
            msg = "<h1>You have signed up today</h1>"
            return msg
        else:
            msg = "GP/Hospital with same ID already exist!"
            return render_template("registergp.html", msg=msg, user=session['user'], date_time=date_time)


#Add Staff
@app.route('/addstaff', methods=['POST', 'GET'])
def addstaff():
    date_time = ""
    if request.method == 'POST':
        con = mysql.connect()

        cur = con.cursor()
        cur.execute('select count(*) from staffsdetails')

        count = cur.fetchall()
        con.commit()
        if count[-1][-1] == 0:
            idkey = 0
        else:
            cur.execute('select id from staffsdetails')

            key = cur.fetchall()
            con.commit()
            idkey = key[-1][-1]

        #print(idkey)
        staffId = session['gpId'] +"-"+ str(int(idkey)+1)
        fname = request.form['fname']
        lname = request.form['lname']
        address = request.form['address']
        city = request.form['city']
        postcode = request.form['postcode']
        phone = request.form['phone']
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['pass'])
        gender = request.form['gender']
        idtype = request.form['idtype']
        idnumber = request.form['idnumber']
        gpid = session['gpId']
        dob = request.form['dob']
        dateadded = date()
        status = "ACTIVE"

        #print(date())


        #print("email " + session['email'])
        #print("name " + session['gpname'])
        #print("Id " + session['gpId'])

        cur.execute('INSERT INTO staffsdetails (staffId, fname, lname, address, city, postcode, phone, username, email, password, gender, idtype, idnumber, gpid, dob, dateadded, status)VALUES( %s, %s,  %s, %s, %s,  %s, %s , %s, %s,  %s, %s , %s,  %s, %s, %s,  %s, %s)',
                    (staffId, fname, lname, address, city, postcode, phone, username, email, password, gender, idtype, idnumber, gpid, dob, dateadded, status))

        con.commit()
        msg = "Staff has been Sucessfully Added!"
        flash(msg, "success")
        return redirect("/staffview")
        con.close()

#Add Patient
@app.route('/addpatient', methods=['POST', 'GET'])
def addpatient():
    date_time = ""
    if request.method == 'POST':
        con = mysql.connect()
        nhsId = request.form['nhsId']
        gpId = request.form['gpId']
        username = request.form['username']

        cur = con.cursor()
        cur.execute('select count(*) from patientsdetails where nhsId=%s AND gpId=%s', (nhsId,gpId))

        count = cur.fetchall()
        con.commit()
        if count[-1][-1] == 0:
            cur = con.cursor()
            cur.execute('select count(*) from patientsdetails where nhsId=%s AND gpId=%s AND username=%s ', (nhsId,gpId, username))

            count2 = cur.fetchall()
            con.commit()

            if count2[-1][-1] == 0:
                cur = con.cursor()
                cur.execute('select count(*) from patientsdetails WHERE username=%s ',
                            (username))

                count3 = cur.fetchall()
                con.commit()
                if count3[-1][-1] == 0:

                    fname = request.form['fname']
                    lname = request.form['lname']
                    address = request.form['address']
                    city = request.form['city']
                    postcode = request.form['postcode']
                    phone = request.form['phone']
                    username = request.form['username']
                    email = request.form['email']
                    password = bcrypt.generate_password_hash(request.form['pass'])
                    gender = request.form['gender']
                    gpid = request.form['gpId']
                    dob = request.form['dob']

                    bloodgroup = request.form['bloodgroup']
                    genotype = request.form['genotype']
                    disabilities = request.form['disabilities']
                    issues = request.form['issues']
                    Vaccination = request.form['Vaccination']

                    dateadded = date()
                    status = "ACTIVE"

                    #print(date())

                    cur.execute('INSERT INTO patientsdetails (nhsId, fname, lname, address, city, postcode, phone, username, email, password, gender, bloodgroup, genotype, disabilities, issues, gpid, dob, dateadded, status,Vaccination)VALUES( %s, %s,  %s, %s, %s,  %s, %s , %s, %s,  %s, %s , %s,  %s, %s, %s,  %s, %s,  %s, %s, %s)',
                                (nhsId, fname, lname, address, city, postcode, phone, username, email, password, gender, bloodgroup, genotype, disabilities, issues, gpid, dob, dateadded, status, Vaccination))

                    con.commit()
                    msg = "You have signed up Successfully... Kindly return to Homepage to Sign in!"
                    flash(msg, "success")
                    return redirect("/registerpatient")
                    con.close()
                else:
                    msg = "Username is not available"
                    flash(msg, "error")
                    return redirect("/registerpatient")
            else:
                msg = "Username is not available"
                flash(msg, "error")
                return redirect("/registerpatient")
        else:
            msg = "Patient with this NHS Number is aleady Exists"
            flash(msg, "error")
            return redirect("/registerpatient")

#login GP Admin
###################################################################################
@app.route('/logingp', methods=['POST', 'GET'])
def logingp():
    clearSession()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM gpdetails WHERE username=%s AND password=%s AND status="ACTIVE"',
                    (username, password))
        count = cur.fetchall()

        con.commit()
        #print(count[-1][-1])

        if count[-1][-1] > 0:
            #print("Successful!")

            cur.execute('select gpname,gpId,email from gpdetails WHERE username=%s AND password=%s AND status="ACTIVE"',
                    (username, password))

            gp = cur.fetchall()
            con.commit()

            #print("email " + gp[-1][2])
            #print("name " + gp[-1][0])
            #print("Id " + gp[-1][1])

            session['email'] = gp[-1][2]
            session['gpname'] = gp[-1][0]
            session['gpId'] = gp[-1][1]
            session['user'] = username
            session['logged'] = "admin"

            # #print("email " + session['email'])
            # #print("name " + session['gpname'])
            # #print("Id " + session['gpId'])
            getstaffs()
            before_request()
            return dashboard()
        else:
            #print("Failed!")
            msg = "Incorrect password or username. Try Again!"
            flash(msg, "error")
            return loginpages("logingp", "","Admin Sign in")
        con.close()


#View Staff profile
@app.route('/loginstaff', methods=['POST', 'GET'])
def loginstaff():
    clearSession() #Clear previous sessions
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM staffsdetails WHERE username=%s AND status="ACTIVE"',
                    (username)) #count all with same username and Actice status
        count = cur.fetchall()

        con.commit()

        if count[-1][-1] > 0:
            cur.execute('SELECT password FROM staffsdetails WHERE username=%s AND status="ACTIVE"',
                        (username)) #Select password with same username and Actice status
            hash = cur.fetchall()

            authpass = bcrypt.check_password_hash(hash[-1][-1], password)  #Compare Hashed password to newly inputed password
            con.commit()
            if authpass:
                cur.execute('select staffId,gpId,email from staffsdetails WHERE username=%s AND status="ACTIVE"',
                        (username)) #Select staffId,gpId,email with same username and Actice status

                gp = cur.fetchall()
                con.commit()

                session['email'] = gp[-1][2]
                session['staffId'] = gp[-1][0]
                session['gpId'] = gp[-1][1]
                session['staffuser'] = username
                session['logged'] = "staff"

                msg = "<h1>You are signed In as Staff</h1>"
                return profilestaff() #Call Function to open staff profile
            else:
                msg = "Incorrect password or username. Try Again!"
                flash(msg, "error")
                return loginpages("loginstaffpage", "","Care-giver Sign in") # Wrong password entered
        else:
            #print("Failed!")
            msg = "Incorrect password or username. Try Again!"
            flash(msg, "error")
            return loginpages("loginstaffpage", "","Care-giver Sign in") # Wrong password entered

        con.close()


#View Patients profile
@app.route('/profile', methods=['POST', 'GET'])
def profile():
    clearSession() #Clear previous sessions
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM patientsdetails WHERE username=%s AND status="ACTIVE"',
                    (username)) #count all with same username and Actice status
        count = cur.fetchall()

        con.commit()

        if count[-1][-1] > 0:
            cur.execute('SELECT password FROM patientsdetails WHERE username=%s AND status="ACTIVE"',
                        (username)) #Select password with same username and Actice status
            hash = cur.fetchall()

            authpass = bcrypt.check_password_hash(hash[-1][-1], password) #Compare Hashed password to newly inputed password
            con.commit()
            if authpass:
                session['patientuser'] = username
                cur.execute('SELECT gpid,nhsid FROM patientsdetails WHERE username=%s AND status="ACTIVE"',
                            (username)) #Select gpId,nhsId with same username and Actice status
                result = cur.fetchall()
                session['gpId'] = result[0][0]
                session['nhsId'] = result[0][1]
                session['logged'] = "patient"


                return profilepatient() #Call Function to open patient profile
            else:
                msg = "Incorrect password or username. Try Again!"
                flash(msg, "error")
                return loginpages("loginPage", "","Patient Sign in")  # Wrong password entered

        else:
            msg = "Incorrect password or username. Try Again!"
            flash(msg, "error")
            return loginpages("loginPage", "", "Patient Sign in")  # Wrong password entered
        con.close()
    return render_template("page-404.html")

# #Add Client
# ###################################################################################
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        con = mysql.connect()
        username = request.form['username']
        email = request.form['email']
        Password = request.form['pass']

        if username and email and Password != "":
            cur = con.cursor()

            cur.execute('INSERT INTO User (username, email, password)VALUES( %s,  %s, %s)',
                        (username, email, Password))

            con.commit()
            return "<h1>Successfully Added</h1>"
            #render_template("dashboard.html", msg=msg, date_time=date(), user=session['user'], gpname=session['gpname'])""
        else:
            return render_template("register.html", msg="Fill all credentials.")
        con.close()

#Staff Assignment
@app.route('/assign', methods=['POST', 'GET'])
def assign():
    if request.method == 'POST':
        con = mysql.connect()
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM assignstaff')
        count = cur.fetchall()

        con.commit()
        assignId = session['gpId'] + "assign" + str(count[0][0]+1)
        gpId = session['gpId']
        staffId = request.form['staffId']
        dateassigned = request.form['dateassigned']
        nhsId = request.form['nhsId']

        cur = con.cursor()
        cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s AND staffid=%s AND dateassigned=%s AND status=%s',
                    (gpId,staffId,dateassigned,"ASSIGNED"))
        count = cur.fetchall()

        if count[0][0] == 0:
            cur = con.cursor()
            cur.execute(
                'SELECT count(*) FROM assignstaff WHERE gpid=%s AND nhsid=%s AND dateassigned=%s AND status=%s',
                (gpId, nhsId, dateassigned, "ASSIGNED"))
            count2 = cur.fetchall()

            if count2[0][0] == 0:
                cur = con.cursor()
                #print("Successful!")

                cur.execute('INSERT INTO assignstaff (assignId,gpId,staffId,nhsId,dateassigned,status) VALUES (%s, %s,  %s,%s, %s,  %s)',
                            (assignId,gpId,staffId,nhsId,dateassigned,"ASSIGNED"))
                con.commit()
                msg = "Successfully assigned Care-giver to Patient!"
                flash(msg, "success")
                return redirect('/settings')
                con.close()
            else:
                msg = "Patient already assigned Caregiver for  "+ dateassigned +" !"
                flash(msg, "error")
                return redirect('/settings')
        else:
            msg = "Caregiver already booked for "+ dateassigned +" !"
            flash(msg, "error")
            return redirect('/settings')
#############################

#Open Patients Profile page on dashboard
###################################################################################
@app.route('/med', methods=['POST', 'GET'])
def med():
    if request.method == 'POST':
        date()
        session['medpatientId'] = request.form['medpatientId']
        medpatientId = request.form['medpatientId']
        return render_template('medication.html',gpd=gpdbasic(medpatientId),
                               getassignments=getassignmentsbasic(medpatientId),
                               countassignments=countassignmentsbasic(medpatientId))

#Open Staff Profile page on dashboard
###################################################################################
@app.route('/meds', methods=['POST', 'GET'])
def meds():
    if request.method == 'POST':
        date()
        session['medpatientId'] = request.form['medpatientId']
        medpatientId = request.form['medpatientId']
        #print(medpatientId)
        return render_template('medication2.html',gpd=gpdbasic2(medpatientId),
                               getassignments=getassignmentsbasic2(medpatientId),
                               countassignments=countassignmentsbasic2(medpatientId))


#Action - Update Assignment
###################################################################################
@app.route('/action', methods=['POST', 'GET'])
def action():
    if request.method == 'POST':
        newstatus = request.form['newstatus']
        medpatientId = request.form['medpatientId']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute('UPDATE assignstaff SET status=%s WHERE assignId=%s',
                    (newstatus,medpatientId))
        con.commit()
        con.close()
        return redirect("/settings")

#UpdateVaccination
###################################################################################
@app.route('/updatevaccination', methods=['POST', 'GET'])
def updatevaccination():
    if request.method == 'POST':
        Vaccination = request.form['Vaccination']

        con = mysql.connect()
        cur = con.cursor()
        cur.execute('UPDATE patientsdetails SET Vaccination=%s WHERE nhsId=%s',
                    (Vaccination,session['medpatientId']))
        con.commit()
        con.close()
        msg = "Vaccination Status Updated!"
        flash(msg, "success")
        medpatientId = session['medpatientId']
        return render_template('medication.html', gpd=gpdbasic(medpatientId),
                               getassignments=getassignmentsbasic(medpatientId),
                               countassignments=countassignmentsbasic(medpatientId))

# medication Prescription
###################################################################################
@app.route('/addmedication', methods=['POST', 'GET'])
def addmedication():
    if request.method == 'POST':
        startdate = request.form['startdate']
        enddate = request.form['enddate']
        if enddate >= startdate:
            con = mysql.connect()
            cur = con.cursor()
            cur.execute('SELECT count(*) FROM medication')
            count = cur.fetchall()

            medId = "medication" + str(count[0][0]+1)
            nhsId = session['medpatientId']
            gpId = session['gpId']
            medname = request.form['medname']
            startdate = request.form['startdate']
            enddate = request.form['enddate']
            pres = request.form['pres']
            cur.execute('INSERT INTO medication (medId,medname,pres,gpId,nhsId,startdate,enddate,datepres,status) VALUES (%s, %s,  %s,%s, %s,  %s,%s, %s,  %s)',
                        (medId,medname,pres,gpId,nhsId,startdate,enddate,date(),"PRESCRIBED"))
            con.commit()
            msg = "Presccription sucessfully Added!"
            flash(msg, "success")
            medpatientId = session['medpatientId']
            return render_template('medication.html', gpd=gpdbasic(medpatientId),
                                   getassignments=getassignmentsbasic(medpatientId),
                                   countassignments=countassignmentsbasic(medpatientId))
            con.close()
        else:
            msg = "Invalid Start and End Dates"
            flash(msg, "error")
            medpatientId = session['medpatientId']
            return render_template('medication.html', gpd=gpdbasic(medpatientId),
                                   getassignments=getassignmentsbasic(medpatientId),
                                   countassignments=countassignmentsbasic(medpatientId))


#Medication usage
###################################################################################
@app.route('/usage', methods=['POST', 'GET'])
def usage():
    if 'staffuser' in session:
        if request.method == 'POST':
            con = mysql.connect()
            cur = con.cursor()

            note= request.form['note']
            medid = request.form['medid']
            nhsId = session['nhsId']
            staffId = session['staffId']

            cur.execute('INSERT INTO medusage (medid,nhsId,staffId,date,time,status,note) VALUES (%s, %s,  %s,%s, %s, %s, %s)',
                        (medid,nhsId,staffId,date(),time(),"ADMINISTERED",note))
            con.commit()

            msg = "Sucessfully Administered Medication!"
            flash(msg, "success")

            return redirect("/view")
    return render_template("page-404.html")  # if the user is not in the session

#############################


#Fucntions
# API for date ---------------------------------------------------------------------------
def date():
    url = "http://worldtimeapi.org/api/timezone/Europe/London"
    response = requests.get(url).json()
    ##print("" + str(response))  # response details
    date_time = response["datetime"]
    #print(date_time)
    #print(date_time[11:16])
    session['date'] = date_time[0:10]# retrieve response details form the attribute, datetime
    return date_time[0:10]  # response details

#Fucntions
# API for time ---------------------------------------------------------------------------
def time():
    url = "http://worldtimeapi.org/api/timezone/Europe/London"
    response = requests.get(url).json()
    ##print("" + str(response))  # response details
    date_time = response["datetime"]
    #print(date_time)
    #print(date_time[11:16])
    session['time'] = date_time[11:16]# retrieve response details form the attribute, datetime
    return date_time[11:16]  # response details

# -------------------------------------------------------------------------------------------------
def gpd():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM patientsdetails WHERE username=%s', (session['patientuser']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select nhsid,gpId,fname,lname,phone,dob,email, gender,address, city, postcode, bloodgroup, genotype, disabilities, issues,  dateadded, status,Vaccination from patientsdetails WHERE username=%s',
            (session['patientuser']))
        #
        gpd = cur.fetchall()
        con.commit()

        return gpd
    con.close()

# -------------------------------------------------------------------------------------------------

def gpds():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM staffsdetails WHERE username=%s', (session['staffuser']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select staffid,gpId,fname,lname,phone,dob,email, gender,address, city, postcode,idtype,idnumber,dateadded, status from staffsdetails WHERE username=%s',
            (session['staffuser']))
        #
        gpd = cur.fetchall()
        con.commit()

        return gpd
    con.close()

# -------------------------------------------------------------------------------------------------

def gpdbasic(patientid):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM patientsdetails WHERE nhsid=%s AND gpid=%s ', (patientid,session['gpId']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select nhsid,gpId,fname,lname,phone,dob,email, gender,address, city, postcode, bloodgroup, genotype, disabilities, issues,  dateadded, status,Vaccination from patientsdetails WHERE nhsid=%s AND gpid=%s ',
            (patientid,session['gpId']))
        #
        gpd = cur.fetchall()
        con.commit()

        return gpd
    con.close()

# -------------------------------------------------------------------------------------------------

def gpdbasic2(patientid):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM staffsdetails WHERE staffId=%s', (patientid))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select staffid,gpId,fname,lname,phone,dob,email, gender,address, city, postcode,idtype,idnumber,dateadded, status from staffsdetails WHERE staffId=%s',
            (patientid))
        #
        gpd = cur.fetchall()
        con.commit()

        return gpd
    con.close()

# -------------------------------------------------------------------------------------------------

def getstaffs():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM staffsdetails WHERE gpid=%s',
                (session['gpId']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select staffid, fname,lname,email, gender, dateadded, status from staffsdetails WHERE gpid=%s',
            (session['gpId']))
        #
        getstaffs = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getstaffs)
        return getstaffs
    else:
        getstaffs = " "
        return getstaffs
    con.close()

def countstaffs():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM staffsdetails WHERE gpid=%s',
                (session['gpId']))
    countstaffs = cur.fetchall()

    con.commit()
    #print(countstaffs[-1][-1])
    return countstaffs[-1][-1]
    con.close()

def getpatients():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM patientsdetails WHERE gpid=%s',
                (session['gpId']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select NHSid, fname,lname,email, gender,Vaccination, dateadded, status from patientsdetails WHERE gpid=%s',
            (session['gpId']))
        #
        getpatients = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getpatients)
        return getpatients
    else:
        getpatients = " "
        return getpatients
    con.close()

def countpatients():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM patientsdetails WHERE gpid=%s',
                (session['gpId']))
    countpatients = cur.fetchall()

    con.commit()
    #print(countpatients[-1][-1])
    return countpatients[-1][-1]
    con.close()

def getassignments():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s',
                (session['gpId']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select assignid, staffid, nhsid, dateassigned, status from assignstaff WHERE gpid=%s',
            (session['gpId']))
        #
        getpatients = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getpatients)
    else:
        getpatients = " "
    return getpatients
    con.close()

def countassignments():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s',
                (session['gpId']))
    countpatients = cur.fetchall()

    con.commit()
    #print(countpatients[-1][-1])
    return countpatients[-1][-1]
    con.close()

def getassignmentsbasic(mid):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s AND nhsid=%s',
                (session['gpId'],mid))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute('select assignid, staffid, dateassigned, status from assignstaff WHERE gpid=%s AND nhsid=%s',
            (session['gpId'],mid))
        #
        getpatients = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getpatients)
    else:
        getpatients = " "
    return getpatients
    con.close()

def countassignmentsbasic(mid):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s AND nhsid=%s',
                (session['gpId'],mid))
    countpatients = cur.fetchall()

    con.commit()
    #print(countpatients[-1][-1])
    return countpatients[-1][-1]
    con.close()

def getassignmentsbasic2(mid):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s AND staffid=%s',
                (session['gpId'],mid))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute('select assignid, nhsid, dateassigned, status from assignstaff WHERE gpid=%s AND staffid=%s',
            (session['gpId'],mid))
        #
        getpatients = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getpatients)
    else:
        getpatients = " "
    return getpatients
    con.close()

def countassignmentsbasic2(mid):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s AND staffid=%s',
                (session['gpId'],mid))
    countpatients = cur.fetchall()

    con.commit()
    #print(countpatients[-1][-1])
    return countpatients[-1][-1]
    con.close()


def getassignmentssort(colname, colvalue):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE gpid=%s',
                (session['gpId']))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select assignid, staffid, nhsid, dateassigned, status from assignstaff WHERE gpid=%s and "'+ colname +'"=%s',
            (session['gpId'], colvalue))
        #
        getpatients = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getpatients)
    else:
        getpatients = " "
    return getpatients
    con.close()

def countassignmentssort(colname, colvalue):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM assignstaff WHERE("'+colname+'"="'+colvalue+'" AND gpId="'+ session['gpId'] +'")')
    countpatients = cur.fetchall()

    con.commit()

    #print(session['gpId'])
    #print(colname)
    #print(colvalue)
    #print("countpatients" + str(countpatients[-1][-1]))
    return countpatients[-1][-1]
    con.close()


def clearSession():
    for key in list(session.keys()):
        session.pop(key)

def gpnames():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM gpdetails WHERE status="ACTIVE"')
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute('select gpId,gpName from gpdetails WHERE status="ACTIVE"')

        gpnames = cur.fetchall()
        con.commit()

        return gpnames
    else:
        return ""
    con.close()

def unassignedstaffs():
    array1 = []
    con = mysql.connect()
    cur = con.cursor()

    #print("Successful!")
    cur.execute('select count(*) from staffsdetails WHERE gpId="'+ session['gpId'] +'" AND status="ACTIVE"')

    count = cur.fetchall()
    con.commit()

    if count[0][0] > 0:
        cur.execute('select staffId from staffsdetails WHERE gpId="' + session['gpId'] + '" AND status="ACTIVE"')

        staffIds = cur.fetchall()
        con.commit()

        for staffId in staffIds:
            array1.append(staffId[0])
    #print(array1)
    return array1
    con.close()

def unassignedpatients():
    array1 = []
    con = mysql.connect()
    cur = con.cursor()

    #print("Successful!")
    #print(session['gpId'])
    cur.execute('select count(nhsId) from patientsdetails WHERE status="ACTIVE" AND gpid="'+ session['gpId'] +'"')

    count = cur.fetchall()
    con.commit()
    #print(count[0][0])

    if count[0][0] > 0:
        cur.execute('select nhsId from patientsdetails WHERE status="ACTIVE" AND gpid="' + session['gpId'] + '"')
        staffIds = cur.fetchall()
        con.commit()

        for staffId in staffIds:
            array1.append(staffId[0])
        #print(array1)
    return array1
    con.close()

def updatemed():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('UPDATE medication SET status=%s WHERE "'+ date() +'" > enddate',
        ("COMPLETED"))
    con.commit()
    con.close()

def updateassign():
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('UPDATE assignstaff SET status=%s WHERE "'+ date() +'" > dateassigned AND status="ASSIGNED"',
        ("FINISHED"))
    con.commit()
    con.close()

def update():
    updateassign()
    updatemed()

def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=6)
    session.modified = True


def getmedpatients(pat):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM medication WHERE gpid=%s AND nhsid=%s',
                (session['gpId'],pat))
    count = cur.fetchall()

    con.commit()
    #print(count[-1][-1])

    if count[-1][-1] > 0:
        #print("Successful!")
        cur.execute(
            'select medid, medname,pres,startdate, enddate, status from medication WHERE gpid=%s AND nhsid=%s ORDER BY medid DESC',
            (session['gpId'],pat))
        #
        getpatients = cur.fetchall()
        con.commit()

        #print(session['gpId'])
        #print(getpatients)
        return getpatients
    else:
        getpatients = " "
        return getpatients
    con.close()

def countmedpatients(pat):
    con = mysql.connect()
    cur = con.cursor()
    cur.execute('SELECT count(*) FROM medication WHERE gpid=%s AND nhsid=%s',
                (session['gpId'],pat))
    countpatients = cur.fetchall()

    con.commit()
    #print(countpatients[-1][-1])
    return countpatients[-1][-1]
    con.close()

def countcovid():
    con = mysql.connect()
    cur = con.cursor()

    cur.execute('SELECT count(*) FROM patientsdetails WHERE gpid=%s AND Vaccination=%s',
                (session['gpId'], "None"))
    count = cur.fetchall()

    cur.execute('SELECT count(*) FROM patientsdetails WHERE gpid=%s AND Vaccination=%s',
                (session['gpId'],"Partially Vaccinated (First Shot)"))
    count1 = cur.fetchall()

    cur.execute('SELECT count(*) FROM patientsdetails WHERE gpid=%s AND Vaccination=%s',
                (session['gpId'], "Vaccinated (Second Shot)"))
    count2 = cur.fetchall()

    cur.execute('SELECT count(*) FROM patientsdetails WHERE gpid=%s AND Vaccination=%s',
                (session['gpId'], "Fully Vaccinated (Booster Shot)"))
    count3 = cur.fetchall()
    con.commit()

    total = count[-1][-1]+count1[-1][-1]+count2[-1][-1]+count3[-1][-1]
    #print("Partially Vaccinated (First Shot) : "+ str(count[-1][-1]))
    #print("Partially Vaccinated (First Shot) : "+ str(count1[-1][-1]))
    #print("Partially Vaccinated (First Shot) : "+ str(count2[-1][-1]))
    #print("Partially Vaccinated (First Shot) : "+ str(count3[-1][-1]))
    #print("Partially Vaccinated (First Shot) : " + str(total))

    # float("{:.2f}".format())
    per = ("{:.1f}".format((count[-1][-1]/total) * 100))
    per1 = ("{:.1f}".format((count1[-1][-1] / total) * 100))
    per2 = ("{:.1f}".format((count2[-1][-1]/total) * 100))
    per3 = ("{:.1f}".format((count3[-1][-1] / total) * 100))

    array1 = [per,per1,per2,per3,count[-1][-1],count1[-1][-1],count2[-1][-1],count3[-1][-1]]
    #print(array1)

    return array1
    con.close()

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port, debug=True)

