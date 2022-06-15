from datetime import date
import datetime
print('processing..')
from recog import *
from recog import predictorr
from flask_wtf import FlaskForm
from wtforms import SelectField,validators
from wtforms import IntegerField,TextField,SubmitField,ValidationError ,BooleanField,MultipleFileField
from wtforms.validators import  DataRequired , Length ,Email
from flask import Flask , url_for, render_template , redirect,flash,session ,Response,request,make_response,send_file
from werkzeug.utils import secure_filename
from tensorflow.keras import  backend as k
from flask_mail import Mail,Message
import cv2 as cv
import numpy as np
import pandas as pd
import zipfile
import os
import pickle
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin
from email_validator import EmailNotValidError
print('processing....')
app = Flask(__name__,template_folder='templates',static_folder='static')
app.config['SECRET_KEY'] = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
#app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yourmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'password'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join('tempimgs')
db = SQLAlchemy(app)
mil =Mail(app)
login_manager = LoginManager(app)
#login_manager.init_app(app)
#login_manager.login_view = 'login'
from tensorflow.keras.models import load_model
import mtcnn
import numpy as np
mod = load_model('modelll')
dec = mtcnn.MTCNN()
rot1 = np.random.randint(1000,10000)
rot2 = np.random.randint(10000,100000)
print('processing.......')
subjcts = {'8':['AI','NN','EDM','DMW'] ,'7': ['CG','NSAG','CD','Elective1','Elective2'],'6':['TOC','SE','MicroP','UNIX','CN']}

def resz3(h, w, img):
    hz = np.zeros((h, w, 3))
    for i in range(3):
        hz[:, :, i] = cv.resize(img[:, :, i], (w, h))

    return hz

@login_manager.user_loader
def load_user(user_id):
    User.query.get(user_id)
class User(db.Model,UserMixin):
    id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"user('{self.username}','{self.email}') "

#db.create_all()
class rform(FlaskForm):
    user_name = TextField("Username:", validators=[DataRequired(), Length(min=3, max=20)])
    email = TextField("Email:", validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(f'That email is already taken')
    
    

class lgform(FlaskForm):
    email = TextField("Registered Email:*", validators=[DataRequired(), Email()])
    clas = IntegerField('Semester *',validators=[DataRequired()])

    submit = SubmitField('Login')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(f'Account doesnot exist')

class otpform(FlaskForm):
    otp = IntegerField('OTP',validators=[DataRequired()])
    submit = SubmitField('verify')

class upldimgs(FlaskForm):


    sem = TextField('semster *',validators=[DataRequired()])
    section = SelectField(label = 'Section *',choices=[('a','Section A'),('b','Section B')],validators = [DataRequired()])
    subb = SelectField(label='Subject *',choices=[('ai', 'Artificial Intelligence'), ('edm', 'Entrepreneurship Dev'),
                                                   ('NN', 'Neural Networks'), ('DMW', 'Data Mining')],validators=[DataRequired()])
    quan = SelectField(label='Weightage *',choices=[('1','1P'),('2','2P'),('3','3P')],validators=[DataRequired()])
    filu = MultipleFileField('upload photos',render_kw={'multiple': True},validators=[DataRequired()])
    submit = SubmitField('Predict')
    remembr = BooleanField('Download Faces Recognised by OSA')

class dwnlform(FlaskForm):
    semd = TextField(label='Semester *',validators=[DataRequired()])
    sectiond = SelectField(label='Section *', choices=[('a', 'Section A'), ('b', 'Section B')],
                          validators=[DataRequired()])
    subbd = SelectField(label='Subject *', choices=[('ai', 'Artificial Intelligence'), ('edm', 'Entrepreneurship Dev'),
                                                   ('NN', 'Neural Networks'), ('DMW', 'Data Mining')],
                       validators=[DataRequired()])
    downloaddd = SubmitField('Download')

class updform(FlaskForm):

    sem = SelectField(label = 'Semester *',choices=[('8','8th semster'),('7','7th semster'),('6','6th semster')],validators = [DataRequired()])
    section = SelectField(label='Section *',choices=[('a','Section A'),('b','Section B')],validators = [DataRequired()])
    enrol = IntegerField('4 digit no.',validators=[DataRequired()])
    filu = MultipleFileField('upload photos',render_kw={'multiple': True},validators=[DataRequired()])
    submit = SubmitField('Upload')

@app.route('/register',methods= ['GET','POST'])
def register():
    formm = rform()
    if formm.validate_on_submit():
        user = User(username=formm.user_name.data, email=formm.email.data)
        db.session.add(user)
        db.session.commit()
        print(User.query.all())
        return redirect(url_for('login'))

    return render_template('reg.html', form=formm)

@app.route('/',methods = ['GET','POST'])
def login():
    fform = lgform()
    if fform.validate_on_submit():
        session['clas'] = fform.clas.data
        otp = np.random.randint(10000,99999)
        session['email'] = fform.email.data
        user = User.query.filter_by(email=fform.email.data).first()
        #uname = User.query(User.username).filter(User.email == user.email).first()
        if not user:
            raise ValidationError(f'{user.email} is not registered on OSA')
        else:
            session['otp'] = otp
            msg = Message(f'OTP for using OSA', sender="reshiaafaq5@gmail.com", recipients=[user.email])
            msg.body = f'Hi! enter this {otp} OTP to continue'
            mil.send(msg)
            return redirect(url_for('vryfyotp'))
    return render_template('index.html',form = fform)

@app.route('/otp',methods = ['GET','POST'])
def vryfyotp():
    form = otpform()
    if form.validate_on_submit():
        ootp = session['otp']
        if ootp == form.otp.data:
            session['loggedin'] = True
            return redirect(url_for('upload'))
        else:
            return render_template('accessDenied.html')

    return render_template('emailre.html',form = form)

@app.route(f'/predimges{rot1}', methods=['GET', 'POST'])
def upload():
    if session['loggedin'] == False:
        return redirect(url_for('login'))
    
    else:
        form = upldimgs(sem = session['clas'])
        form.subb.choices = [(i,i) for i in subjcts[str(session['clas'])]]
        flash(f'Logged into {session["clas"]}th semester sucessfully','info')
        if form.validate_on_submit():
            names=[]
            for ff in form.filu.data:
                filename = secure_filename(ff.filename)
                names.append(filename)
                ff.save(f'institutes/{filename}')
            semstr = form.sem.data
            section = form.section.data
            subname = form.subb.data
            qun = form.quan.data
            pathh = f'picklefiles/ssm/{str(semstr).lower()}/{str(section).lower()}'
            if os.path.exists(pathh):
                rpath = f'registr/ssm/{str(semstr).lower()}/{str(section).lower()}/{str(subname).lower()}/atn.csv'
                rrpath = f'registr/ssm/{str(semstr).lower()}/{str(section).lower()}/{str(subname).lower()}'
                cols = [colss for colss in os.listdir(pathh)]
                pklpth = pathh
                dics = []
                prlst = []
                for name in names:
                    dic = predictorr(f'institutes/{name}',mod,dec,pklpth)
                    os.remove(f'institutes/{name}')
                    k.clear_session()

                    dics.append(dic['image'])
                    for ls in dic['present']:
                        prlst.append((ls))

                nmlst = []
                for col in cols:
                    if col in prlst:
                        nmlst.append(f'{str(qun)}P')
                    else:
                        nmlst.append('A')
                time = datetime.datetime.now().strftime('%I:%M')
                df1 = pd.DataFrame([nmlst],columns=cols, index=[f"{qun}P {date.today().strftime('%d %B,%Y')} {time}"])
                if os.path.exists(rpath):
                    df2 = pd.read_csv(rpath,index_col=0)
                    df3 = pd.concat([df2,df1],ignore_index=False)
                    df3.to_csv(rpath)
                elif os.path.exists(rrpath):
                    df1.to_csv(rpath)
                else:
                    os.makedirs(rrpath)
                    df1.to_csv(rpath)

                if form.remembr.data:
                    for i,im in enumerate(dics):
                        cv.imwrite(f'institutes/tempimgs/{names[i]}',im)
                    nm = np.random.randint(1000,1000000)
                    zipf = zipfile.ZipFile(f'predimges/images{nm}.zip','w',zipfile.ZIP_DEFLATED)
                    for fil in os.listdir('institutes/tempimgs'):
                        zipf.write(f'institutes/tempimgs/{fil}')
                        os.remove(f'institutes/tempimgs/{fil}')
                    zipf.close()

                    return send_file(f'predimges/images{nm}.zip',mimetype='zip',as_attachment=True)
            else:
                return redirect(url_for('updatee'))

        return render_template('sendu.html', form = form)

@app.route(f'/dwn{rot1}',methods = ['GET','POST'])
def dwnld():
    fform = dwnlform(semd=session['clas'])
    fform.subbd.choices = [(i,i) for i in subjcts[str(session['clas'])]]
    if session['loggedin'] == False:
        return redirect(url_for('login'))
    else:
        if fform.validate_on_submit():
            semstr = str(fform.semd.data).lower()
            section = str(fform.sectiond.data).lower()
            subname = str(fform.subbd.data).lower()

            df = pd.read_csv(f'registr/ssm/{semstr}/{section}/{subname}/atn.csv',index_col=0)
            cols = df.columns
            dp = df.copy()
            dp = dp.replace({'1P':1,'2P':2,'3P':3,'A':0})
            data=dp.sum(axis=0)
            d1 = pd.DataFrame([data],index=['Total Presents'],columns=cols)
            d2 = pd.concat([df,d1],ignore_index=False)
            resp = make_response(d2.to_csv())
            resp.headers["Content-Disposition"] = f"attachment; filename={semstr}th_{section.upper()}_{subname}.csv"
            resp.headers["Content-Type"] = "text/csv"
            return resp

        #return send_file(rrpat,mimetype='text/csv',as_attachment=True)
        return render_template('templ.html',form = fform)

@app.route(f'/updatee{rot2}',methods = ['GET','POST'])
def updatee():
    form = updform()
    if session['loggedin'] == False:
        return redirect(url_for('login'))
    else:
        if form.validate_on_submit():
            sems = str(form.sem.data)
            sect = str(form.section.data).lower()
            rolll = str(form.enrol.data).lower()
            namess = []
            for ff in form.filu.data:
                filename = secure_filename(ff.filename)
                print(filename)
                namess.append(filename)
                ff.save(f'institutes/{filename}')
            pkl = []
            for nam in namess:
                xx = cv.imread(f'institutes/{nam}')
                faces = dec.detect_faces(xx)
                for fac in faces:
                    x,y,w,h = fac['box']

                    con = fac['confidence']
                    if con>0.9:
                        nimg = xx[y:y + h, x:x + w, :]
                        nimg = resz3(224, 224, nimg)
                        nimg = nimg.reshape(-1,224,224,3,1)
                        pkl.append(mod.predict(nimg))
                        os.remove(f'institutes/{nam}')
            pkld= np.array(pkl)
            if  os.path.exists(f'picklefiles/ssm/{sems}/{sect}'):

                pkfl = open(f'picklefiles/ssm/{sems}/{sect}/{rolll}', 'wb')
            else:
                os.makedirs(f'picklefiles/ssm/{sems}/{sect}')
                print('success')
                pkfl = open(f'picklefiles/ssm/{sems}/{sect}/{rolll}', 'wb')
            pickle.dump(pkld,pkfl)
            pkfl.close()

            return redirect(url_for('upload'))
        return render_template('upkl.html',form = form)

@app.route(f'/logout{rot2}',methods = ['GET','POST'])
def logout():
    session['loggedin'] = False
    session.pop('otp')
    session.pop('clas')
    session.pop('loggedin')
    return redirect(url_for('login'))

if __name__ == "__main__" :
    app.run(debug=True,use_reloader = False)
