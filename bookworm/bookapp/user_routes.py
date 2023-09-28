import json
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from flask import render_template,request,abort,redirect,flash,make_response,session,url_for

#local import will follow
from bookapp import app,csrf
#removed post and put registration
from bookapp.models import db,Book,User,Category,State,Lga,Reviews
from bookapp.forms import *

def login_required(f):
    @wraps(f)  #this ensures that the details(meta data) about the original function f, that is decorated is still available..
    def login_check(*args, **kwargs):
        if session.get("userloggedin") !=None:
            return f(*args,**kwargs)
        else:
            flash("Access Denied")
            return redirect ('/login/')
    return login_check

@app.route('/favourite')
def favourite_topics():
    bootcamp = {'name':'Olusegun', 'topics':['HTML','Css','Python']}
    # category = []
    # cats= db.session.query(Category).all()
    # for c in cats:
    #     category.append(c.cat_name)
    cats = db.session.query(Category).all()
    category = [c.cat_name for c in cats]
    

    return json.dumps(category)
   

@app.route('/contact/')
def ajax_contact():
    data="I am a String from the Server"
    return render_template('user/ajax_text.html', data=data)


@app.route("/submission/" ,methods=['GET','POST'])
def ajax_submission():
    user=request.args.get('fullname')
    if user != "" and user != None:
        return f'Thank you {user} for completing the form'
    else:
        return 'Please complete the form'
    
@app.route('/checkusername/',methods=['POST','GET'])
def checkusername():
    email = request.args.get('username')
    query = db.session.query(User).filter(User.user_email==email).first()
    if query:
        return "Email is taken"
    else:    
        return "Email is available, Please go Ahead"



@app.route("/dependent/")
def dependent_dropdown():
    states=db.session.query(State).all()
    return render_template("user/show_state.html",states=states)

@app.route("/lga/<stateid>/")
def load_lgas(stateid):
    records = db.session.query(Lga).filter(Lga.state_id==stateid).all()
    str2return= "<select class='form-control'>"
    for r in records:
        optstr = f"<option value='{r.lga_id}'>"+r.lga_name +"</option>"
        str2return = str2return + optstr

    str2return = str2return + "</select>"

    return str2return



@app.route('/profile/',methods=['GET','POST'])
@login_required
def edit_profile():
    id = session.get('userloggedin')
    userdeets = db.session.query(User).get(id)
    pform=Profileform()
    if request.method == 'GET':
        return render_template('user/edit_profile.html', pform=pform,userdeets=userdeets)
    else:
        if pform.validate_on_submit():
            fullname = request.form.get('fullname')
            userdeets.user_fullname = fullname
            db.session.commit()
            flash('Profile Name has Changed Successfully.')
            return redirect(url_for('dashboard'))
        else:
            return render_template('user/edit_profile.html', pform=pform,userdeets=userdeets)
    

@app.route("/changedp/", methods=['GET','POST'])
@login_required
def changedp():
    id =  session.get('userloggedin')
    userdeets=db.session.query(User).get(id)
    dpform = Dpform()
    if request.method == 'GET':
        return render_template("user/changedp.html", dpform=dpform, userdeets=userdeets)
    else:# form is being sumitted
        if dpform.validate_on_submit():
            pix = request.files.get('dp')
            filename = pix.filename
            pix.save(app.config['USER_PROFILE_PATH']+filename)
            userdeets.user_pix=filename
            db.session.commit()
            flash('File has been Uploaded')
            return redirect(url_for('dashboard'))
        else:
            return render_template('user/changedp.html',dpform=dpform, userdeets=userdeets)

@app.route('/viewall/')
def viewall():
    books = db.session.query(Book).filter(Book.book_status=="1").all()
    cat = db.session.query(Category).all()
    return render_template("user/viewall.html" ,books=books,cat=cat)

@app.route('/logout')
def logout():
    if session.get('userloggedin')!=None:
        session.pop('userloggedin',None)
    return redirect('/')

@app.route("/dashboard/")
def dashboard():
    if session.get('userloggedin')!=None:
        id= session.get('userloggedin')
        userdeets=User.query.get(id)
        return render_template('user/dashboard.html',userdeets=userdeets)
    else:
        flash('You need to login to access the page')
        redirect("/login/")


@app.route('/submit_review/', methods=['POST'])
@login_required
def submit_review():
    title= request.form.get('title')
    content= request.form.get('content')
    userid=session.get('userloggedin')
    book=request.form.get('bookid')
    br=Reviews(rev_title=title,rev_text=content, rev_userid=userid,rev_bookid=book)
    db.session.add(br)
    db.session.commit()
   

    retstr=f"""<article class="blog-post">
        <h5 class="blog-post-title">{title}</h5>
        <p class="blog-post-meta">Reviewed just now by <a href="#">{br.reviewby.user_fullname}<a></p>
        </p>
        <p>{content}</p>
        <hr>
        </article>"""
    return retstr

@app.route("/myreviews/")
@login_required
def myreviews():
    id = session['userloggedin']
    userdeets=db.session.query(User).get(id)  
    return render_template ('user/myreviews.html', userdeets=userdeets)

@app.route('/ajaxopt/',methods=['POST','GET'])
def ajax_options():
    cform = Contact()
    if request.method=='GET':
        return render_template('user/ajax_options.html',cform=cform)
    else:
        email =request.form.get('email')
        cont = Contact.query.filter(Contact.contact_email==email).first()
        if cont:
            msg2return = {'mesasge':'Email Exits!','bsclass':'alert alert-danger'}
            





@app.after_request
def after_request(response):
    # To Solve The problem of logged out users details being cache in the brower
    response.headers["Cache-control"]="no-cache, no-store, must-revalidate"
    return response

@app.route("/")
def home_page():
    books = db.session.query(Book).filter(Book.book_status=='1').limit(7).all()
    return render_template('user/home_page.html',books=books)

@app.route('/books/details/<id>')
def book_details(id):
    books=Book.query.get_or_404(id)
    return render_template("user/reviews.html",books=books)

@app.route('/register/', methods=['GET','POST'])
def register():
    regform=RegForm()
    if request.method =='GET':
        return render_template('user/signup.html',regform=regform)
    else:
        if regform.validate_on_submit():
            fullname = request.form.get('fullname')
            email=request.form.get('email')
            pwd= request.form.get('pwd')
            hashed_pwd=generate_password_hash(pwd)
            user=User(user_fullname=fullname,user_email=email,user_pwd=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            flash("An account has been created Succesfully..")
            return redirect('/login')
        else:
            return render_template("user/signup.html",regform=regform)
        

        
        
@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method=="GET":
        return render_template('user/loginpage.html')
    else:
        #retrieve form data
        email = request.form.get('email')
        pwd= request.form.get('pwd')
        deets= db.session.query(User).filter(User.user_email==email).first()
        if deets != None:
            hashed_pwd = deets.user_pwd
            if check_password_hash(hashed_pwd,pwd) ==True:
                session['userloggedin']=deets.user_id
                return redirect('/dashboard')
            else:
                flash("invalid credentials,try again")
                return redirect("/login")
        else:
            flash("invalid credentials, try again")
            return redirect("/login")
                

        