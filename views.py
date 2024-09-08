from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
from django.core.files.storage import FileSystemStorage
import pymysql
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from sklearn import svm

import pandas as pd
from sklearn.model_selection import train_test_split
from string import punctuation
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from numpy import dot
from numpy.linalg import norm


global uname
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def cleanNews(doc):
    tokens = doc.split()
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w in stop_words]
    tokens = [word for word in tokens if len(word) > 1]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens

X = np.load("model/X.npy")
Y = np.load("model/Y.npy")
URLS = np.load("model/URLS.npy")

tfidf_vectorizer = TfidfVectorizer(stop_words=stop_words, use_idf=True, smooth_idf=False, norm=None, decode_error='replace', max_features=3000)
tfidf = tfidf_vectorizer.fit_transform(X).toarray()        
df = pd.DataFrame(tfidf, columns=tfidf_vectorizer.get_feature_names())
print(str(df))
print(df.shape)
X = df.values
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

def Train(request):
    if request.method == 'GET':
        output = ''
        font = '<font size='' color=black>'
        arr = ['Algorithm Name','Accuracy','Precision','Recall','FSCORE']
        output += '<table border="1" align="center"><tr>'
        for i in range(len(arr)):
            output += '<th><font size="" color="black">'+arr[i]+'</th>'
        output += "</tr>"
    
        svm_cls = svm.SVC()
        svm_cls.fit(X, Y)
        predict = svm_cls.predict(X_test)
        p = precision_score(y_test, predict,average='macro') * 100
        r = recall_score(y_test, predict,average='macro') * 100
        f = f1_score(y_test, predict,average='macro') * 100
        a = accuracy_score(y_test,predict)*100
        output += '<tr><td><font size="" color="black">SVM</td><td><font size="" color="black">'+str(a)+'</td><td><font size="" color="black">'+str(p)+'</td><td><font size="" color="black">'+str(r)+'</td><td><font size="" color="black">'+str(f)+'</td></tr>'

        xgb_cls = XGBClassifier()
        xgb_cls.fit(X, Y)
        predict = xgb_cls.predict(X_test)
        p = precision_score(y_test, predict,average='macro') * 100
        r = recall_score(y_test, predict,average='macro') * 100
        f = f1_score(y_test, predict,average='macro') * 100
        a = accuracy_score(y_test,predict)*100
        output += '<tr><td><font size="" color="black">XGBoost</td><td><font size="" color="black">'+str(a)+'</td><td><font size="" color="black">'+str(p)+'</td><td><font size="" color="black">'+str(r)+'</td><td><font size="" color="black">'+str(f)+'</td></tr>'
        context= {'data':output}        
        return render(request, 'ViewUsers.html', context)
    

def VerifyUser(request):
    if request.method == 'GET':
        global uname
        username = request.GET['t1']
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'searchengine',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update signup set status='Accepted' where username='"+username+"'" 
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            output = username+" account activated"
        context= {'data':output}
        return render(request, 'AdminScreen.html', context)

def SearchQueryAction(request):
    if request.method == 'POST':
        query = request.POST.get('t1', False)
        qry = query
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Query','Search URL','Rating']
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        query = query.strip().lower()
        query = cleanNews(query)
        vector = tfidf_vectorizer.transform([query]).toarray()
        vector = vector.ravel()
        for i in range(len(X)):
            score = dot(X[i], vector)/(norm(X[i])*norm(vector))
            if score > 0.2:
                output += "<tr><td>"+font+qry+"</td>"
                output += '<td><a href="'+URLS[i]+'" target="_blank">'+font+URLS[i]+"</td>"
                output += "<td>"+font+str(score)+"</td>"
        context= {'data':output}        
        return render(request, 'ViewOutput.html', context)        
    

def ViewUsers(request):
    if request.method == 'GET':
        global uname
        output = '<table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Username','Password','Contact No','Gender','Email Address','Address','Status']
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'searchengine',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM signup")
            rows = cur.fetchall()
            for row in rows:
                username = row[0]
                password = row[1]
                contact = row[2]
                gender = row[3]
                email = row[4]
                address = row[5]
                status = row[6]
                output += "<tr><td>"+font+str(username)+"</td>"
                output += "<td>"+font+password+"</td>"
                output += "<td>"+font+contact+"</td>"
                output += "<td>"+font+gender+"</td>"
                output += "<td>"+font+email+"</td>"
                output += "<td>"+font+address+"</td>"
                if status == 'Pending':
                    output += '<td><a href="VerifyUser?t1='+username+'">Click Here</a></td>'
                else:
                    output += "<td>"+font+status+"</td>"
        context= {'data':output}        
        return render(request, 'ViewUsers.html', context)


def UploadDatasetAction(request):
    if request.method == 'POST':
        global uname
        dataset = request.FILES['t1']
        dataset_name = request.FILES['t1'].name
        fs = FileSystemStorage()
        fs.save('SearchEngineApp/static/files/'+dataset_name, dataset)
        output = dataset_name+' saved in database'
        context= {'data':output}
        return render(request, 'UploadDataset.html', context)

def UploadDataset(request):
    if request.method == 'GET':
       return render(request, 'UploadDataset.html', {})  

def SearchQuery(request):
    if request.method == 'GET':
       return render(request, 'SearchQuery.html', {})  

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})  

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def ManagerLogin(request):
    if request.method == 'GET':
       return render(request, 'ManagerLogin.html', {})    

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def AdminLoginAction(request):
    global uname
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if username == 'admin' and password == 'admin':
            uname = username
            context= {'data':'welcome '+username}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'AdminLogin.html', context)
        
def ManagerLoginAction(request):
    global uname
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if username == 'Manager' and password == 'Manager':
            uname = username
            context= {'data':'welcome '+uname}
            return render(request, 'ManagerScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'ManagerLogin.html', context)

def UserLoginAction(request):
    global uname
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'searchengine',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,password, status FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and password == row[1] and row[2] == "Accepted":
                    uname = username
                    index = 1
                    break		
        if index == 1:
            context= {'data':'welcome '+uname}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed or account not activated by admin'}
            return render(request, 'UserLogin.html', context)        

def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        gender = request.POST.get('t4', False)
        email = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        output = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'searchengine',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = username+" Username already exists"
                    break
        if output == 'none':
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'searchengine',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO signup(username,password,contact_no,gender,email,address,status) VALUES('"+username+"','"+password+"','"+contact+"','"+gender+"','"+email+"','"+address+"','Pending')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                output = 'Signup Process Completed'
        context= {'data':output}
        return render(request, 'Signup.html', context)
      


