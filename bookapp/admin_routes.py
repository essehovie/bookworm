import random,os,string
from flask import render_template,request,abort,redirect,flash,make_response,session,url_for

#local import will follow
from bookapp import app,csrf
#removed post and put registration
from bookapp.models import db,Admin,Book,Category
from bookapp.forms import *



@app.route('/admin/books/')
def all_book():
            
            if session.get('adminuser')==None or session.get('role')!= 'admin':
                 return redirect(url_for('admin_login'))
            else:
                books =db.session.query(Book).all()
                return render_template("admin/allbooks.html",books=books)
            
def generate_string(howmany): #call this function as a generate_string
            x= random.sample(string.ascii_lowercase,howmany)
            return ''.join(x)
            

@app.route('/admin/delete/<id>/')
def book_delete(id):
       book=db.session.query(Book).get_or_404(id)
       #lets get the name of thee file attached to this book
       filename = book.book_cover
       #first delete the file before deleting the book
       if filename != None and filename != 'default.png':
            os.remove("bookapp/static/uploads/"+filename)#import os at the top
       db.session.delete(book)
       db.session.commit()
       flash('Book has been Sucessfully deleted..')
       return redirect(url_for('all_book'))      


@app.route('/admin/addbook/', methods=["GET","POST"])
def addbook():
    if session.get('adminuser')==None or session.get('role')!= 'admin':
        return redirect(url_for('admin_login'))
    else:
        if request.method=="GET":
            cat = db.session.query(Category).all()
            book = db.session.query(Book).all()
            return render_template('admin/addbook.html',book=book,cat=cat)
          
        else:
            allowed=['png','jpeg','jpg']
            filesobj=request.files['cover']
            filename=filesobj.filename
            newname="default.png"   #default cover
          
            if filename=='': #no file was uploaded
                flash('Book cover not included', category='error')
            else:
                pieces =filename.split('.')
                ext= pieces[-1].lower
                if ext in allowed:
                    newname=str(int(random.random()*10000000))+filename #to mke sure it is random
                    filesobj.save("bookapp/static/uploads/"+newname)
                else:
                    flash('This Extension is not supported, File was not uploaded',category='error')
                    
            title= request.form.get('title')
            category = request.form.get('category')
            status = request.form.get('status')
            description = request.form.get('description')
            yearpub = request.form.get('yearpub')
            #insert into db
            bk = Book(book_title=title,book_desc=description,book_publication=yearpub, book_catid=category,book_status=status,book_cover=newname)
            db.session.add(bk)
            db.session.commit()
            if bk.book_id:
                flash('Book has been added')
            else:
                flash('Please try again')
            return redirect(url_for('all_book'))


@app.after_request
def after_request(response):
    # To Solve The problem of logged out users details being cache in the brower
    response.headers["Cache-control"]="no-cache, no-store, must-revalidate"
    return response

@app.route("/admin/login/",methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/login.html')
    else:
        #retrieve from  data
        username = request.form.get('username')
        pwd= request.form.get('pwd')
        #check if it is a database
        check = db.session.query(Admin).filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first()
        #if it is in db, save in session and redirect to dashboard
        if check:#it is in db,save session
            session["adminuser"]=check.admin_id
            session['role']='admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('invalid Login', category='error')
            return redirect(url_for('admin_login'))
        #if not, save message in flash, redirect login page

@app.route("/admin/logout/")
def admin_logout():
    if session.get("adminuser")!=None:#he is still logged in
        session.pop("adminuser",None)
        session.pop("role",None)
        flash("You have Logged out", category='info')
        return redirect(url_for('admin_login'))
    else:#she is logged out already
        return render_template(url_for('admin_login'))

@app.route("/admin/")
def admin_page():
    if session.get("adminuser")== None:
        return render_template("admin/login.html")
    else:
        return redirect(url_for("admin_dashboard"))



    
@app.route("/admin/dashboard/")
def admin_dashboard():
    if session.get('adminuser')==None or session.get('role')!= 'admin':#means ge is not logged in
        return redirect(url_for('admin_login'))
    else:
        return render_template("admin/dashboard.html")
    
@app.route("/admin/edit/book/<id>", methods=['POST','GET'])
def edit_book(id):
    if session.get("adminuser")== None or session.get('role')!='admin':
         return redirect(url_for('admin_login'))
    else:
         if request.method=='GET':
            # books=db.session.query(Book).get_or_404(id)
              deets=db.session.query(Book).filter(Book.book_id==id).first_or_404(id)
              cats=db.session.query(Category).all()
              return render_template("admin/editbook.html",deets=deets, cats=cats)
         else: # retreive data here..
              #in order to update the book details
              books_2update= Book.query.get(id)
              current_filename=books_2update.book_cover
              books_2update.book_title = request.form.get('title')
              books_2update.book_category=  request.form.get('category')
              books_2update.book_status=  request.form.get('status')
              books_2update.book_cover =  request.form.get('cover')
              books_2update.book_description =  request.form.get('description')
              books_2update.book_yearpub =  request.form.get('yearpub')
              cover = request.files.get('cover')
              #check if the file was selected for upload
              if cover.filename =='':
                    name,ext = os.path.splitext(cover.filename)
                    if ext.lower() in ['.jpg','.png','.jpeg']:
                         
                    #upload the file, its allowed
                    #let the filename remain the same on the db
                        newfilename = generate_string(10) + "."+ext
                        cover.save('bookapp/static/uploads/'+newfilename)
                        books_2update.book_cover=newfilename
                    else:
                        flash('The extension of the book cover was not included')
              db.session.commit()
              flash('Book details was updated')
              return redirect('/admin/books/')
              
                        
    
    
