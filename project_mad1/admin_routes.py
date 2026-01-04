from model import db, Admin, User, Section, Books, Requests, Issued, Review
from flask import render_template, Blueprint, redirect, request, flash, session
from werkzeug.security import check_password_hash,generate_password_hash
from functools import wraps
from datetime import datetime
from auxiliary_functions import today, get_returndate, allowed_file, allowed_img
import os
from sqlalchemy import desc
import matplotlib.pyplot as plt
plt.switch_backend('agg')

admin=Blueprint('admin',__name__)

#decorator for session management
def auth(func):
    @wraps(func)
    def admin_auth(*args,**kwargs):
        if 'admin_id' in session:
            return func(*args,**kwargs)
        else:
            flash('Login is required.')
            return redirect('/admin_login')
    return admin_auth

#admin login
@admin.route('/admin_login',methods=['GET','POST'])
def login_admin():
    if request.method=='POST':
        admin= request.form.get('admin')
        password= request.form.get('password')
        existing_admin=Admin.query.filter(admin==Admin.admin_name).first()
        if admin=='' or password=='':
            flash("* marked fields can't be empty")
            return redirect('/admin_login')
        elif not existing_admin:
            flash('Admin does not exist.')
            return redirect('/admin_login')
        else:
            if not check_password_hash(existing_admin.passhash,password):
                flash('Incorrect Password')
                return redirect('/admin_login')
            else:
                session['admin_id']=existing_admin.admin_id
                return redirect('/admin_page')
    return render_template('admin_login.html')

#admin functionalities
@admin.route('/admin_page')
@auth
def admin_home():
    admin=Admin.query.get(session['admin_id'])
    sections=Section.query.all()
    books=Books.query.all()
    comments=Review.query.order_by(desc(Review.rating)).limit(5)
    d={}
    for x in books:
        book=Review.query.filter(x.book_id==Review.book_id).all()
        sum=0
        count=0
        for y in book:
            sum+=y.rating
            count+=1
        if count>0:
            d[x.name]=sum/(count)
        else:
            d[x.name]=0
    l1=list(d.keys())
    l2=list(d.values())
    plt.barh(l1,l2)
    plt.xlabel('Rating')
    plt.ylabel('books')
    plt.title('Book Ratings')
    plt.savefig('static/ratings.png')
    plt.close()
    return render_template('admin_index.html',sections=sections,d=d,comments=comments,admin=admin.name)

@admin.route('/admin_profile')
@auth
def admin_profile():
    admin_id=session['admin_id']
    admin=Admin.query.get(admin_id)
    return render_template('admin_profile.html',admin=admin)

@admin.route('/edit_admin_profile',methods=['GET','POST'])
@auth
def edit_admin():
    to_edit=Admin.query.get(session['admin_id'])
    if request.method=='POST':
        password=request.form['password']
        name=request.form['name']
        email=request.form['email']
        if password=='' or name=='':
            flash("*marked fields can't be empty.")
            return redirect('/edit_admin_profile')
        elif len(password)<8 or len(password)>24:
            flash('Password length should be between 8 to 24 characters.')
            return redirect('/edit_admin_profile')
        else:
            to_edit.passhash=generate_password_hash(password)
            to_edit.name=name
            to_edit.email=email
            db.session.commit()
            return redirect('/admin_page')
    return render_template('edit_admin.html',to_edit=to_edit)

#Sections
@admin.route('/section',methods=['GET','POST'])
@auth
def sections():
    sec=Section.query.all()
    return render_template('admin_sections.html',genre=sec)

@admin.route('/section/<int:section_id>')
@auth
def get_section(section_id):
    section=Section.query.get(section_id)
    db.session.commit()
    return render_template('section_details.html',section=section)

@admin.route('/section/add',methods=['GET','POST'])
@auth
def add_sections():
    if request.method=='POST':
        name=request.form['name']
        date_created_str=request.form['date_created']
        description=request.form['description']
        date_created=datetime.strptime(date_created_str,'%Y-%m-%d').date()
        existing_genre=Section.query.filter(name==Section.name).first()
        if name=='':
            flash("*marked fields can't be empty.")
            return redirect('/section/add')
        if existing_genre:
            flash('Genre already exists.')
            return redirect('/section/add')
        new_genre=Section(name=name,date_created=date_created,description=description)
        db.session.add(new_genre)
        db.session.commit()
        return redirect('/section')
    return render_template('add_sections.html')

@admin.route('/section/<int:section_id>/edit',methods=['GET','POST'])
@auth
def edit_section(section_id):
    to_edit=Section.query.get(section_id)
    date=str(to_edit.date_created)
    if request.method=='POST':
        to_edit.name=to_edit.name
        date_str=request.form['date_created']
        to_edit.date_created=datetime.strptime(date_str,'%Y-%m-%d').date()
        to_edit.description=request.form['description']
        db.session.commit()
        return redirect('/section')
    return render_template('edit_section.html',to_edit=to_edit,date=date)

@admin.route('/section/<int:section_id>/delete')
@auth
def delete_section(section_id):
    to_delete=Section.query.get(section_id)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/section')

#Books
@admin.route('/books')
@auth
def books():
    books=Books.query.all()
    for x in books:
        book_issued=Issued.query.filter(x.book_id==Issued.book_id).first()
        if not book_issued:
            x.available=True
    db.session.commit()
    return render_template('admin_books.html',books=books)

@admin.route('/book/<int:book_id>')
@auth
def get_book(book_id):
    book=Books.query.get(book_id)
    db.session.commit()
    return render_template('book_details.html',book=book)


@admin.route('/book/add',methods=['GET','POST'])
@auth
def add_book():
    section=Section.query.all()
    if request.method=='POST':
        name=request.form['name']
        img=request.files['img']
        author=request.form['author']
        content=request.form['content']
        genre_id=request.form['genre_id']
        price=request.form['price']
        file=request.files['book']
        existing_book=Books.query.filter(name==Books.name).first()
        if name=='':
            flash("*marked fields can't be empty.")
            return redirect('/book/add')
        if existing_book:
            flash('Book already exists.')
            return redirect('/book/add')
        if 'book' not in request.files:
            flash('Please upload the book.')
            return redirect('/book/add')
        if file.filename=='':
            flash('Please select a file.')
            return redirect('/book/add')
        if 'img' not in request.files:
            flash('Please upload the image.')
            return redirect('/book/add')
        if img.filename=='':
            flash('Please select a image.')
            return redirect('/book/add')
        if not allowed_img(img.filename):
            flash('.png,.jpg,.jpeg images are allowed only.')
            return redirect('/book/add')
        if not allowed_file(file.filename):
            flash('Only .pdf files are allowed.')
            return redirect('/book/add')
        filepath='static/'+file.filename
        imgpath='static/'+img.filename
        file.save(filepath)
        img.save(imgpath)
        new_book=Books(name=name,imgname=img.filename,author=author,content=content,genre_id=genre_id,price=price,filename=file.filename)
        db.session.add(new_book)
        db.session.commit()
        return redirect('/books')
    return render_template('add_book.html',genre=section)

@admin.route('/book/<int:book_id>/edit',methods=['GET','POST'])
@auth
def edit_book(book_id):
    to_edit=Books.query.get(book_id)
    section=Section.query.all()
    if request.method=='POST':
        to_edit.name=to_edit.name
        to_edit.author=request.form['author']
        to_edit.content=request.form['content']
        to_edit.genre_id=request.form['genre_id']
        to_edit.price=request.form['price']
        db.session.commit()
        return redirect('/books')
    return render_template('edit_book.html',to_edit=to_edit,genre=section)

@admin.route('/book/<int:book_id>/delete')
@auth
def delete_book(book_id):
    to_delete=Books.query.get(book_id)
    file=os.path.join('static/',to_delete.filename)
    img=os.path.join('static/'+to_delete.imgname)
    os.remove(file)
    os.remove(img)
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/books')

@admin.route('/users')
@auth
def get_all_users():
    users=User.query.all()
    return render_template('all_users.html',users=users)

@admin.route('/user/<int:user_id>')
@auth
def get_user(user_id):
    user=User.query.get(user_id)
    db.session.commit()
    return render_template('user_details.html',user=user)

@admin.route('/user/<int:user_id>/delete')
@auth
def ban_user(user_id):
    to_ban=User.query.get(user_id)
    db.session.delete(to_ban)
    db.session.commit()
    return redirect('/user')

@admin.route('/request')
@auth
def all_requests():
    req=db.session.query(Books,Requests).join(Requests).all()
    db.session.commit()
    return render_template('request.html', req=req)


@admin.route('/request/<int:user_id>/<int:book_id>/issue',methods=['GET','POST'])
@auth
def issue_book(book_id,user_id):
    if request.method=='POST':
        book=Issued.query.filter(user_id==Issued.user_id, book_id==Issued.book_id).first()
        requested=Requests.query.filter(user_id==Requests.user_id, book_id==Requests.book_id).first()
        availablity=Books.query.get(book_id)
        if book:
            flash('This book is already issued to this user.')
            return redirect('/request')
        date_str=request.form.get('issue_date')
        issue_date=datetime.strptime(date_str,'%Y-%m-%d').date()
        return_date=get_returndate(issue_date)
        paid=False
        new_issue=Issued(book_id=book_id, user_id=user_id, issue_date=issue_date, return_date=return_date, paid=paid)
        availablity.available=False
        db.session.add(new_issue)
        db.session.delete(requested)
        db.session.commit()
        return redirect('/issued_books')
    return render_template('issue_form.html',user=user_id,book=book_id)

@admin.route('/request/<int:request_id>/reject')
@auth
def reject_request(request_id):
    to_reject=Requests.query.get(request_id)
    db.session.delete(to_reject)
    db.session.commit()
    return redirect('/request')

@admin.route('/issued_books')
@auth
def issued_books():
    books=Issued.query.filter(today>=Issued.return_date).delete()
    db.session.commit()
    final=db.session.query(Books,Issued).join(Issued).all()
    return render_template('issued_books.html',L=final)

@admin.route('/issued_books/<int:book_id>/revoke')
@auth
def revoke_book(book_id):
    to_revoke=Issued.query.get(book_id)
    db.session.delete(to_revoke)
    revoked_book=Books.query.get(book_id)
    revoked_book.available=True
    db.session.commit()
    return redirect('/issued_books')

@admin.route('/test')
@auth
def avg_ratings():
    books=Books.query.all()
    comments=Review.query.order_by(desc(Review.rating)).limit(5)
    d={}
    for x in books:
        book=Review.query.filter(x.book_id==Review.book_id).all()
        sum=0
        count=1
        for y in book:
            sum+=y.rating
            count+=1
        if count>0:
            d[x.name]=(sum/count)
    l1=list(d.keys())
    l2=list(d.values())
    plt.barh(l1,l2)
    plt.xlabel('Rating')
    plt.ylabel('books')
    plt.title('Book Ratings')
    plt.savefig('static/ratings.png')
    return render_template('admin_index.html',avg_ratings=d,comments=comments)

@admin.route('/admin/book/<int:section_id>/genre')
@auth
def section_browse(section_id):
    books=Books.query.filter(section_id==Books.genre_id).all()
    section=Section.query.get(section_id)
    return render_template('admin_section_browse.html',books=books,section=section)

@admin.route('/admin/book/search',methods=['GET','POST'])
@auth
def search_book():
    if request.method=='POST':
        type=request.form['type']
        search=request.form['search']
        if type=='book_name':
            books=Books.query.filter(Books.name.like('%'+search+'%')).all()
        elif type=='author':
            books=Books.query.filter(Books.author.like('%'+search+'%')).all()
        return render_template('admin_search_results.html',type=type,search=search,books=books)

@admin.route('/admin_logout')
@auth
def logout_admin():
    session.pop('admin_id',None)
    return redirect('/admin_login')