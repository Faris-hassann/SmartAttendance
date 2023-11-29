from flask import Flask, g, render_template, request, redirect, Response, jsonify, url_for, send_file, session
import win32security
import os
import requests
import mysql.connector
import datetime
import cv2
import cmake
import dlib
import face_recognition
import numpy as np
import pandas as pd
import csv
import json
import win32security
import base64
import re
import win32con
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import threading
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = "your_secret_key"

db_uri = 'mysql+mysqlconnector://root:faris2003@localhost/xceedAttendanceSystem'
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)

# connect to database 
db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "faris2003",
    database = "xceedAttendanceSystem"
)

def check_required(employee_data):
    error_messages = {}

    role = employee_data.get('role')
    if role == 'others':
        error_messages['role'] = 'Role is Required'
    
    if role == "Admin":
        username = employee_data.get('username')
        if not username:
            error_messages['username'] = 'Username is Required'
        
        password = employee_data.get('password')
        if not password:
            error_messages['firstname'] = 'Password is Required'
    
    else:
        username = employee_data.get('username')
        if not username:
            error_messages['username'] = 'Username is Required'
        
        password = employee_data.get('password')
        if not password:
            error_messages['firstname'] = 'Password is Required'

        employeeID = employee_data.get('employeeID')
        if not employeeID:
            error_messages['employeeID'] = 'employeeID is Required'
        
        firstname = employee_data.get('firstname')
        if not firstname:
            error_messages['firstname'] = 'First Name is Required'

        lastname = employee_data.get('lastname')
        if not lastname:
            error_messages['lastname'] = 'Last Name is Required'
        
        phone_number = employee_data.get('phone_number')
        if not phone_number:
            error_messages['Phone_number'] = 'Phone number is Required'
        
        email = employee_data.get('email')
        if not email:
            error_messages['email'] = 'E-mail is Required'
        
        gender = employee_data.get('gender')
        if gender != "male" or gender != "female":
            error_messages['gender'] = 'Gender is Required'
        
        Address = employee_data.get('Address')
        if not Address:
            error_messages['Address'] = 'Address is Required'
        
        department = employee_data.get('department')
        if not department:
            error_messages['Department'] = 'Department is Required'
        
        room = employee_data.get('room')
        if not room:
            error_messages['room'] = 'Room is Required'
        
        image = employee_data.get('image')
        if not image:
            error_messages['image'] = 'Image File is Required.'

    return error_messages
        
# validation check
def validate_employee_data(employee_data):
    errors = []

    role = employee_data.get('role')
    if role != 'Admin' and role != 'User':
        errors.append("Role is required")

    username = employee_data.get('username')
    if not username:
        errors.append("username is required")
    
    # check password validation
    password = employee_data.get('password')
    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
        errors.append("Password must contain at least one capital letter, one small letter, one number, and one special character.")

    # Checks if the employee id is digit or not
    employee_id = employee_data.get('EmployeeID')
    if not employee_id or not employee_id.isdigit():
        errors.append('Employee ID is required and must be a number.')

    # checks if the first name has special character or doesn't have a value
    first_name = employee_data.get('firstName')
    if isinstance(first_name, str) and len(first_name) > 0:
        if re.search(r'[^\w\s]+', first_name):
            errors.append('Special Character in First Name is not allowed.')
    else:
        errors.append('First Name is missing.')
    
    # checks if the last name has special character or doesn't have a value
    last_name = employee_data.get('lastName')
    if isinstance(last_name, str) and len(last_name) > 0:
        if re.search(r'[^\w\s]+', last_name):
            errors.append('Special Character in Last Name is not allowed.')
    else:
        errors.append('Last Name is missing')

    # checks the phone number has 11 digit or not
    phone_number = employee_data.get('phoneNumber')
    if not phone_number or not phone_number.isdigit() or len(phone_number) != 11:
        errors.append('Phone number is required and must be a 11-digit number.')

    # check the validation of email address
    email = employee_data.get('email')
    if not email or '@' not in email:
        errors.append('Valid E-mail Address is required.')

    # checks the role if it is admin or user
    gender = employee_data.get('gender')
    if gender != 'male' and gender != 'female':
        errors.append('Please Select Gender.')

    # checks if the address has special character or doesn't have a value
    address = employee_data.get('Address')
    if isinstance(address, str) and len(address) > 0:
        if re.search(r'[^\w\s]+', address):
            errors.append('Special Character in Address is not allowed.')
    else:
        errors.append('Address is missing.')

    # checks if the department has special character or doesn't have a value
    department = employee_data.get('department')
    if isinstance(department, str) and len(department) > 0:
        if re.search(r'[^\w\s]+', department):
            errors.append('Special Character in Department is not allowed.')
    else:
        errors.append('Department is missing.')

    # checks the room if it is digit
    room = employee_data.get('room')
    if not room or not room.isdigit():
        errors.append('Room is Required and must be a Number.')

    # checks the file of the image
    image = employee_data.get('image')
    if not image:
        errors.append('Image File is Required.')

    # exceeds the number of letters in each attribute
    username =  employee_data.get('username')
    if username is not None and len(username) > 50:
        errors.append('Username exceeds 50 characters.')
    
    password =  employee_data.get('password')
    if password is not None and len(password) > 255:
        errors.append('Password exceeds 255 characters.')
    
    first_name =  employee_data.get('firstName')
    if first_name is not None and len(first_name) > 255:
        errors.append('First Name exceeds 255 characters.')

    last_name =  employee_data.get('lastName')
    if last_name is not None and len(last_name) > 255:
        errors.append('Last Name exceeds 255 characters.')

    email =  employee_data.get('email')
    if email is not None and len(email) > 255:
        errors.append('E-mail exceeds 255 characters.')

    Address =  employee_data.get('Address')
    if Address is not None and len(Address) > 255:
        errors.append('Address exceeds 255 characters.')

    department =  employee_data.get('department')
    if department is not None and len(department) > 255:
        errors.append('Department exceeds 255 characters.')

    room =  employee_data.get('room')
    if room is not None and len(room) > 10:
        errors.append('Room exceeds 10 characters.')
    
    duplicate = check_for_duplicates(employee_id, email)
    if duplicate:
        errors.append('Employee ID or Email Already Exist.')
    # print(errors)

    username_duplicate = check_for_duplicates_users(username)
    if username_duplicate:
        errors.append('Username already Exists')

    return errors

def check_for_duplicates(employee_id, email):
    mycursor = db.cursor()
    sql = "SELECT * FROM Employee WHERE EmployeeID = %s OR Email = %s"
    val = (employee_id, email)
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    mycursor.close()
    return result

def check_for_duplicates_users(username):
    mycursor = db.cursor()
    sql = "SELECT * FROM Users WHERE username = %s"
    val = (username,)  # Add a comma to create a tuple with a single element
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    mycursor.close()
    return result

@app.route('/submit', methods=['POST'])
def submit():
    createdbywho = session.get('username')

    role = request.form['role']
    username = request.form['username']
    password = request.form['password']
    EmployeeID = request.form['EmployeeID']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    phoneNumber = request.form['phoneNumber']
    Email = request.form['email']
    gender = request.form['gender']
    Address = request.form['Address']
    department = request.form['department']
    room = request.form['room']
    image = request.files['image'].read()
    createdby = createdbywho
    createdon = datetime.datetime.now()

    # Create a dictionary containing the form data
    employee_data = {
        'role' : role,
        'username' : username,
        'password' : password,
        'EmployeeID': EmployeeID,
        'firstName': firstName,
        'lastName': lastName,
        'phoneNumber': phoneNumber,
        'email': Email,
        'gender': gender,
        'Address': Address,
        'department': department,
        'room': room,
        'image': image,
        'createdby': username,
        'createdon': createdon,
    }

    # check that all section is requried
    # required = check_required(employee_data)
    # Validate the form data
    errors = validate_employee_data(employee_data)
    # if not required:
    if not errors:
        if role == "Admin":
            sql = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            val = (username, password, "Admin")
            mycursor.execute(sql, val)
            # Commit the transaction
            db.commit()
            # Return a success message as a
            response_data = {'status': 'success', 'title': 'Data saved successfully!'}
            return json.dumps(response_data), 200
        elif role == "User":
            # insert new user
            user_sql = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
            val_sql = (username, password, "User")
            mycursor.execute(user_sql, val_sql)

            # Insert new employee record into Employee table
            sql = "INSERT INTO Employee (EmployeeID, firstName, lastName, phoneNumber, Email, gender, Address, department, room, image, createdby, createdon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (EmployeeID, firstName, lastName, phoneNumber, Email, gender, Address, department, room, image, createdby, createdon)
            mycursor.execute(sql, val)
            # Commit the transaction
            db.commit()

            # Return a success message as a
            response_data = {'status': 'success', 'title': 'Data saved successfully!'}
            return json.dumps(response_data), 200
    else:
        # Return the validation errors as a JSON response
        response_data = {'status': 'error', 'errors': errors}
        return json.dumps(response_data), 400
    
# update signout in database
def update_signin_database(student_id):
    mycursor = db.cursor()

    # Get the current date and time
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()

    # Check if the user has already signed out today
    check_query = 'SELECT * FROM Employee WHERE EmployeeID = %s AND DATE(signintime) = %s'
    check_values = (student_id, current_date)

    mycursor.execute(check_query, check_values)
    existing_record = mycursor.fetchone()

    if not existing_record:
        # SQL command to update the signout attribute
        sql_update_query = """
        UPDATE Employee
        SET signintime = %s
        WHERE EmployeeID = %s
        """
        
        # Execute the SQL command with the current datetime and student_id
        mycursor.execute(sql_update_query, (current_datetime, student_id))
        db.commit()
    else:
        print("User has already signed out today.")

# update the signin
def update_signout_database(student_id):
    mycursor = db.cursor()

    # Get the current date and time
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()

    # Check if the user has already signed in today
    check_query = 'SELECT * FROM Employee WHERE EmployeeID = %s AND DATE(signouttime) = %s'
    check_values = (student_id, current_date)

    mycursor.execute(check_query, check_values)
    existing_record = mycursor.fetchone()

    if not existing_record:
        # SQL command to update the signin attribute
        sql_update_query = """
        UPDATE Employee
        SET signouttime = %s
        WHERE EmployeeID = %s
        """
        
        # Execute the SQL command with the current datetime and student_id
        mycursor.execute(sql_update_query, (current_datetime, student_id))
        db.commit()
    else:
        print("User has already signed in today.")

# select all the attributes from my database
mycursor = db.cursor()
mycursor.execute("SELECT EmployeeID, firstName, lastName, phoneNumber, Email, gender, Address, department, room, image FROM employee")
results = mycursor.fetchall()

# Create a list of dictionaries to store the student data
students = []

for result in results:
    student = {
        'EmployeeID': result[0], 
        'firstName': result[1], 
        'lastName': result[2], 
        'phoneNumber': result[3], 
        'Email': result[4],
        'gender': result[5],
        'Address': result[6], 
        'department': result[7],
        'room': result[8],
        'image': result[9],
    }
    students.append(student)

# print(result[1])
# cv2.imshow(result[9])
# print(students)

# Attendance System Function
images = []
classID = []
classNames = []
classEmail = []

# adding names in Id into classNames
for cl in students:
    classID.append(result[0])
    classNames.append(result[1]+ " " + result[2])
    classEmail.append(result[3])

for result in results:
    # Decode the image data into an array of bytes
    img_data = np.frombuffer(result[9], np.uint8)

    # Read the image data into an image file using cv2.imread()
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

    # put them in a list
    images.append(img)

# print(images)
# print(len(images))

# find Encodes 
def findEncodes(images):
    encodeList = []
    for imm in images:
        imm = cv2.cvtColor(imm, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(imm)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodes(images)
# print(len(encodeListKnown))

def update_sign_in_out_history(student_id):
    mycursor = db.cursor()

    current_date = datetime.date.today()

    check_query = 'SELECT * FROM UserHistory WHERE EmployeeID = %s AND createdOn = %s'
    check_values = (student_id, current_date)

    mycursor.execute(check_query, check_values)
    existing_record = mycursor.fetchone()

    if not existing_record:
        # SQL command to select signintime and signouttime from the Employee table
        select_times_query = """
        SELECT signintime, signouttime
        FROM Employee
        WHERE EmployeeID = %s
        """

        mycursor.execute(select_times_query, (student_id,))
        times = mycursor.fetchone()

        if times:
            sign_in_time = times[0]
            sign_out_time = times[1]

            insert_query = 'INSERT INTO UserHistory (EmployeeID, signInTime, signOutTime, createdOn) VALUES (%s, %s, %s, %s)'
            insert_values = (student_id, sign_in_time, sign_out_time, current_date)

            insert_cursor = db.cursor()
            insert_cursor.execute(insert_query, insert_values)
            db.commit()
        else:
            print('No sign-in or sign-out time found for the student.')
    else:
        print('User already exists')

# setting up the camera
cap = cv2.VideoCapture(0)

name = None
StudentID = None

def sign_in():
    global name, StudentID
    while True:
        success, frame = cap.read()
        if not success:
            break

        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        if len(facesCurFrame) == 1:
            faceLoc = facesCurFrame[0]
            encodeFace = encodesCurFrame[0]

            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex]
                student_id = classID[matchIndex]
                student_email = classEmail[matchIndex]
                
                update_signin_database(student_id)

            y1, y2, x1, x2 = faceLoc
            y1, y2, x1, x2 = y1 * 4, y2 * 4, x1 * 4, x2 * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)

        elif len(facesCurFrame) > 1:
            print('There is more than one person in the frame.')

        # Step 15: Convert the modified frame to JPEG format and yield it
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def sign_out():
    global name, StudentID
    while True:
        success, frame = cap.read()
        if not success:
            break

        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        if len(facesCurFrame) == 1:
            faceLoc = facesCurFrame[0]
            encodeFace = encodesCurFrame[0]

            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex]
                student_id = classID[matchIndex]
                student_email = classEmail[matchIndex]

                update_signout_database(student_id)
                update_sign_in_out_history(student_id)

            y1, y2, x1, x2 = faceLoc
            y1, y2, x1, x2 = y1 * 4, y2 * 4, x1 * 4, x2 * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)

        elif len(facesCurFrame) > 1:
            print('There is more than one person in the frame.')

        # Step 15: Convert the modified frame to JPEG format and yield it
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# pages redirect
@app.route('/')
def index():
    return render_template('login.html', title="Login",custom_css="login")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if user and user[2] == password:
        # Retrieve the role for the username from the users table
        cursor = db.cursor()
        cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
        role = cursor.fetchone()
        cursor.close()

        if role:
            # Store the username and role in the session after successful login
            session['username'] = username
            session['role'] = role[0]
            return redirect('/base')
        else:
            return render_template('login.html', title="Login",custom_css="login" , error_message='Role not found for the user.')

    else:
        return render_template('login.html', custom_css="login", title="login", error_message='Invalid username or password.')

# dashboard
@app.route('/base')
def base():
    username = session.get('username')
    role = session.get('role')
    signintime, signouttime = None, None

    if role == "User" and username:
        # Fetch the signintime and signouttime from the Employee table for the specified user
        cursor = db.cursor()
        query = "SELECT signintime, signouttime FROM Employee e JOIN users u ON e.firstName = u.username WHERE u.username = %s"
        cursor.execute(query, (username,))
        employee_data = cursor.fetchone()

        if employee_data:
            signintime, signouttime = employee_data

    return render_template("home.html", title="Xceed Attendance System", custom_css="home", username=username, role=role, signintime=signintime, signouttime=signouttime)

@app.route('/addUser')
def addUser():
    username = session.get('username')
    role = session.get('role')
    return render_template("addUser.html", title="Add User", custom_css="addUser", username=username,role=role, error_messages=None)

@app.route('/signin')
def signin():
    return Response(sign_in(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/signout')
def signout():
    return Response(sign_out(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/signinpage')
def signinpage():
    username = session.get('username')
    role = session.get('role')
    return render_template('signin.html', title="Signin", username=username, role=role)

@app.route('/signoutpage')
def signoutpage():
    username = session.get('username')
    role = session.get('role')
    return render_template('signout.html', title="Signout", username=username, role=role)

@app.route('/download-attendance')
def download_attendance():
    filename = 'attendance.csv'
    file_path = os.path.join(filename)

    # Serve the Excel file as a downloadable attachment
    return send_file(
        file_path,
        attachment_filename=filename,
        as_attachment=True,
        cache_timeout=0
    )

@app.route('/download-signout')
def download_signout():
    filename = 'signout.csv'
    file_path = os.path.join(os.path.dirname(__file__), filename)

    # Serve the Excel file as a downloadable attachment
    return send_file(
        file_path,
        as_attachment=True,
        attachment_filename=filename,  # Provide the desired filename for download
        cache_timeout=0
    )

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'faris2003',
    'database': 'xceedAttendanceSystem'
}

def get_employees_data():
    try:
        # Connect to the database
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        # Fetch data from the Employee table
        query = "SELECT EmployeeID, firstName, lastName, email, department, signintime, signouttime, image FROM Employee"
        cursor.execute(query)

        employees_data = []
        for row in cursor.fetchall():
            employee_data = {
                "EmployeeID": row[0],
                "firstName": row[1],
                "lastName": row[2],
                "email": row[3],
                "department": row[4],
                "signintime": row[5],
                "signouttime": row[6],
                "image": base64.b64encode(row[7]).decode('utf-8')
            }
            employees_data.append(employee_data)

        # Close the database connection
        cursor.close()
        db.close()

        return employees_data

    except mysql.connector.Error as err:
        print("Error: {}".format(err))
        return []
    
def get_employe_year_data():
    try:
        # Connect to the database
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        # Fetch data from the Employee table
        query = "SELECT HistoryID, EmployeeID, signInTime, signOutTime, createdOn FROM UserHistory"
        cursor.execute(query)

        employees_data = []
        for row in cursor.fetchall():
            employee_data = {
                "HistoryID": row[0],
                "EmployeeID": row[1],
                "signInTime": row[2],
                "signOutTime": row[3],
                "createdOn": row[4]
            }
            employees_data.append(employee_data)

        # Close the database connection
        cursor.close()
        db.close()

        return employees_data

    except mysql.connector.Error as err:
        print("Error: {}".format(err))
        return []

@app.route('/reports')
def report():
    username = session.get('username')
    role = session.get('role')
    return render_template('report.html', title="Reports", custom_css="report", username=username, role=role)

@app.route('/get_employees_data')
def get_employees_data_route():
    employees_data = get_employees_data()
    return jsonify(data=employees_data)

@app.route('/get_employees_year_data')
def get_employees_data_year_route():
    employees_data = get_employe_year_data()
    return jsonify(data=employees_data)

@app.route('/yearReport')
def yearReport():
    username = session.get('username')
    role = session.get('role')
    return render_template('yearReport.html', title="Year Report", custom_css="report", username=username, role=role)

if __name__ == '__main__':
    app.run(debug=True, port=5000)