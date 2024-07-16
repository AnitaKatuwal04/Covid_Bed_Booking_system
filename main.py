from ast import Param
from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user

#from flask_mail import Mail
import json
import MySQLdb

# mydatabase connection
local_server=True
app=Flask(__name__)
app.secret_key="anzu"


# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databsename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/covid'
db=SQLAlchemy(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(2000),unique=True)
    email=db.Column(db.String(2000))
    dob=db.Column(db.String(2000))


class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    code=db.Column(db.String(2000))
    email=db.Column(db.String(2000))
    password=db.Column(db.String(2000))


class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    code=db.Column(db.String(2000),unique=True)
    hname=db.Column(db.String(2000))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)

class Trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    code=db.Column(db.String(2000))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    querys=db.Column(db.String(2000))
    date=db.Column(db.String(2000))

class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(2000),unique=True)
    bedtype=db.Column(db.String(2000))
    code=db.Column(db.String(2000))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(2000))
    pphone=db.Column(db.String(2000))
    paddress=db.Column(db.String(2000))


@app.route("/")
def home():
   
    return render_template("index.html")

@app.route("/trigers")
def trigers():
    query=Trig.query.all() 
    return render_template("trigers.html",query=query)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        srfid=request.form.get('srf')
        email=request.form.get('email')
        dob=request.form.get('dob')
        # print(srfid,email,dob)
        encpassword=generate_password_hash(dob)
        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srif is already taken","warning")
            return render_template("usersignup.html")
        # new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{encpassword}') ")
        new_user=User(srfid=srfid,email=email,dob=encpassword)
        db.session.add(new_user)
        db.session.commit()
                
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob=request.form.get('dob')
        user=User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")

@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")


    return render_template("hospitallogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
 
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username=="admin" and password=="admin"):
            session['user']=username
            flash("login success","info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Sucessful","warning")
    return redirect(url_for('login'))

@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
   
    if('user' in session and session['user']=="admin"):
      
        if request.method=="POST":
            code=request.form.get('code')
            email=request.form.get('email')
            password=request.form.get('password')        
            encpassword=generate_password_hash(password)  
            code=code.upper()      
            emailUser=Hospitaluser.query.filter_by(email=email).first()
            if  emailUser:
                flash("Email is already taken","warning")
         
            new_user=Hospitaluser(code=code,email=email,password=encpassword)
            db.session.add(new_user)
            db.session.commit()

            flash("Data Sent and Inserted Successfully","warning")
            return render_template("addHosUser.html")

    else:
        flash("Login and try Again","warning")
        return render_template("addHosUser.html")
  
    if __name__ == '__main__':
        app.run(debug=True)
    


@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')


def updatess(code):
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()
    return render_template("hospitaldata.html",postsdata=postsdata)

@app.route("/addhospitalinfo",methods=['POST','GET'])
def addhospitalinfo():
    email=current_user.email
    posts=Hospitaluser.query.filter_by(email=email).first()
    code=posts.code
    postsdata=Hospitaldata.query.filter_by(code=code).first()

    if request.method=="POST":
        hcode=request.form.get('code')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        huser=Hospitaluser.query.filter_by(code=code).first()
        hduser=Hospitaldata.query.filter_by(code=code).first()
        if hduser:
            flash("Data is already Present you can update it..","primary")
            return render_template("hospitaldata.html")
        if huser:            
            # db.engine.execute(f"INSERT INTO `hospitaldata` (`code`,`hname`,`normalbed`,`hicubed`,`icubed`,`vbed`) VALUES ('{hcode}','{hname}','{nbed}','{hbed}','{ibed}','{vbed}')")
            query=Hospitaldata(code=code,hname=hname,normalbed=nbed,hicubed=hbed,icubed=ibed,vbed=vbed)
            db.session.add(query)
            db.session.commit()
            flash("Data Is Added","primary")
            return redirect('/addhospitalinfo.html')
            

        else:
            flash("Hospital Code not Exist","warning")
            return redirect('/addhospitalinfo')




    return render_template("hospitaldata.html",postsdata=postsdata)


@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
  
    if request.method=="POST":
        code=request.form.get('code')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        code=code.upper()
        # db.engine.execute(f"UPDATE `hospitaldata` SET `code` ='{code}',`hname`='{hname}',`normalbed`='{nbed}',`hicubed`='{hbed}',`icubed`='{ibed}',`vbed`='{vbed}' WHERE `hospitaldata`.`id`={id}")
        post=Hospitaldata.query.filter_by(id=id).first()
        post.code=code
        post.hname=hname
        post.normalbed=nbed
        post.hicubed=hbed
        post.icubed=ibed
        post.vbed=vbed
        db.session.commit()
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    # posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html",posts=posts)


@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    # db.engine.execute(f"DELETE FROM `hospitaldata` WHERE `hospitaldata`.`id`={id}")
    post=Hospitaldata.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Date Deleted","danger")
    return redirect("/addhospitalinfo")


@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.srfid
    print(code)
    data=Bookingpatient.query.filter_by(srfid=code).first()
    return render_template("detials.html",data=data)


@app.route("/slotbooking",methods=['POST','GET'])
@login_required
def slotbooking():
    # query1=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    # query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    query1=Hospitaldata.query.all()
    query=Hospitaldata.query.all()
    if request.method=="POST":
        
        srfid=request.form.get('srfid')
        bedtype=request.form.get('bedtype')
        code=request.form.get('code')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress')  
        check2=Hospitaldata.query.filter_by(code=code).first()
        checkpatient=Bookingpatient.query.filter_by(srfid=srfid).first()
        if checkpatient:
            flash("already srd id is registered ","warning")
            return render_template("booking.html",query=query,query1=query1)
        
        if not check2:
            flash("Hospital Code not exist","warning")
            return render_template("booking.html",query=query,query1=query1)

        code=code
        # dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`code`='{code}' ")  
        dbb=Hospitaldata.query.filter_by(code=code).first()      
        bedtype=bedtype
        if bedtype=="NormalBed":       
                seat=dbb.normalbed
                print(seat)
                ar=Hospitaldata.query.filter_by(code=code).first()
                ar.normalbed=seat-1
                db.session.commit()
                
            
        elif bedtype=="HICUBed":      
                seat=dbb.hicubed
                print(seat)
                ar=Hospitaldata.query.filter_by(code=code).first()
                ar.hicubed=seat-1
                db.session.commit()

        elif bedtype=="ICUBed":     
                seat=dbb.icubed
                print(seat)
                ar=Hospitaldata.query.filter_by(code=code).first()
                ar.icubed=seat-1
                db.session.commit()

        elif bedtype=="VENTILATORBed": 
                seat=dbb.vbed
                ar=Hospitaldata.query.filter_by(code=code).first()
                ar.vbed=seat-1
                db.session.commit()
        else:
            pass

        check=Hospitaldata.query.filter_by(code=code).first()
        if check!=None:
            if(seat>0 and check):
                res=Bookingpatient(srfid=srfid,bedtype=bedtype,code=code,spo2=spo2,pname=pname,pphone=pphone,paddress=paddress)
                db.session.add(res)
                db.session.commit()
                flash("Slot is Booked kindly Visit Hospital for Further Procedure","success")
                return render_template("booking.html",query=query,query1=query1)
            else:
                flash("Something Went Wrong","danger")
                return render_template("booking.html",query=query,query1=query1)
        else:
            flash("Give the proper hospital Code","info")
            return render_template("booking.html",query=query,query1=query1)
            
    
    return render_template("booking.html",query=query,query1=query1)




app.run(debug=True)