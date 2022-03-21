from .models import Student_Info
from os import system
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import studform
import re
import base64
from django.contrib import messages
import pandas as pd
import os
import cv2
import threading
import multiprocessing
from django.core.mail import send_mail
import face_recognition

def indexview(request):
    return render(request, 'index.html')


def signinview(request):
    if request.method=='POST':
        if request.POST['username'] == 'admin' and request.POST['password']=='password':
            request.session['user'] = 'LogedIn'
            return render(request, 'welcome.html')
        else:
            messages.error(request, "Invalid Username or Password")
    elif 'user' in request.session:
        return render(request, 'welcome.html')
    return render(request, 'signin.html')


def logoutview(request):
    try:
        request.session['user']
    except KeyError :
        return redirect('http://127.0.0.1:8000/signin/')

    del request.session['user']
    return redirect('http://127.0.0.1:8000/')


def registerview(request):
    if request.method == 'POST':
        form_obj = studform(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            request.session['regno'] = request.POST['Registration_No']

            return render(request, 'take_image.html')
        else:
            messages.error(request, 'Registration number already exist...')
            form = studform()
            return render(request, 'signup.html', {'form': form})
    else:
        form = studform()
        return render(request, 'signup.html', {'form':form})


def saveimageview(request):
    if request.method != 'POST':
        return redirect('http://127.0.0.1:8000/')
    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    image_data = request.POST['imagedata']
    image_data = dataUrlPattern.match(image_data).group(2)
    image_data = image_data.encode()
    image_data = base64.b64decode(image_data)

    with open(f"images/train/{request.session['regno']}.jpg", 'wb') as f:
        f.write(image_data)

    if face_validation(f"images/train/{request.session['regno']}.jpg"):
        request.session['regno'] = None
        return render(request, 'index.html', {'mess':'success'})
    else:
        system(f"del images\\train\\{request.session['regno']}.jpg")
        messages.error(request, "We cann't not recognise your face")
        messages.error(request, "Please take a another pic having your face only...")
        return render(request, 'take_image.html')


def face_validation(image):
    train_image = face_recognition.load_image_file(image)
    l = face_recognition.face_encodings(train_image)
    if len(l) == 1:
        return True
    return False


def takeattendanceview(request):
    try:
        request.session['user']
    except KeyError :
        return redirect('http://127.0.0.1:8000/signin/')

    detect_face()
    return redirect('http://127.0.0.1:8000/signin/')


def viewattendanceview(request):
    try:
        request.session['user']
    except KeyError :
        return redirect('http://127.0.0.1:8000/signin/')

    df = pd.read_csv('data.csv')
    regnos = df.Regno
    fname = df.First_Name
    lname = df.Last_Name
    branch = df.Branch
    email = df.Email
    status = df.Status
    data = zip(regnos, fname, lname, branch, email, status)
    return render(request, 'view_attendance.html', {'data': data })


def detect_face():
    known_face_names = []
    Last_Name = []
    Regnos = []
    Branch = []
    Email = []
    known_face_encodings = []

    data = Student_Info.objects.values('First_Name', 'Last_Name', 'Registration_No', 'Branch', 'Email')
    for student in data:
        if os.path.exists(f"images/train/{student['Registration_No']}.jpg"):
            img = f"images/train/{student['Registration_No']}.jpg"
            image = face_recognition.load_image_file(img)
            known_face_encodings.append(face_recognition.face_encodings(image)[0])
            known_face_names.append(student['First_Name'])
            Last_Name.append(student['Last_Name'])
            Regnos.append(student['Registration_No'])
            Branch.append(student['Branch'])
            Email.append(student['Email'])
        else:
            Student_Info.objects.get(pk=student['Registration_No']).delete()

    df = pd.read_csv('format.csv')
    df.Regno = Regnos
    df.First_Name = known_face_names
    df.Last_Name = Last_Name
    df.Branch = Branch
    df.Email = Email

    face_locations = []
    face_names = []
    process_this_frame = True
    video_capture = cv2.VideoCapture(0)
    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

    while True:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if matches.count(True) == 1:
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]
                        df.loc[first_match_index, 'Status'] = 'Present'

                    face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    video_capture.open(0)
    cv2.destroyAllWindows()
    df.fillna('Absent', inplace=True)
    df.to_csv('data.csv', index=False)

    t = threading.Thread(target=send_Email, args=(df,))
    t.start()


def send_Email(df):
    to_mail = [df.loc[index, 'Email'] for index in range(len(df)) if df.loc[index, 'Status'] == 'Absent']
    total_student = len(df)
    absent = len(to_mail)
    present = total_student - absent
    admin_mail = ['purnachandramansingh135@gmail.com']
    from_mail = 'gr.project04@gmail.com'
    mail_subject = 'Attendance Report'
    message = '''
        Dear Parents,

        I am writing to regard of your son/daughter attendance at College.

        Your son/daughter is absent on today.
        The college has not received any letter or contact from you.
        You are asked to contact the college as soon as.

        Thank you for your co-operation in this matter.

        Yours sincerely,
        Admin, GCEK Bhawanipatna
    '''
    admin_message = f'Total number of students present today is {present} out of {total_student} students.'


    send_mail(mail_subject, message, from_mail, to_mail, fail_silently=False,)
    send_mail(mail_subject, admin_message, from_mail, admin_mail, fail_silently=False)
