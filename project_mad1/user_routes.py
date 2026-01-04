from model import db, User,Section, Books, Requests, Issued, Review
from flask import render_template, Blueprint, redirect, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from auxiliary_functions import today, check_upi
from sqlalchemy import desc

user=Blueprint('user',__name__)

#decorator for session management
def auth(func):
    @wraps(func)
    def user_auth(*args,**kwargs):
        if 'user_id' in session:
            return func(*args,**kwargs)
        else:
            flash('Login is required.')
            return redirect('/login')
    return user_auth

#user register
@user.route('/register',methods=['GET','POST'])
def register_user():
    if request.method=='GET':
        return render_template('register.html')
    if request.method=='POST':
        user=request.form.get('user')
        password=request.form.get('password')
        name=request.form.get('name')
        email=request.form.get('email')
        existing_user=User.query.filter(user==User.user_name).first()
        if user=='' or password=='' or name=='':
            flash("* marked fields can't be empty")
            return redirect('/register')
        elif existing_user:
            flash('User already exists.')
            return redirect('/register')
        elif len(password)<8 or len(password)>24:
            flash('Password length must be in between 8 to 24 characters.')
            return redirect('/register')
        else:
            new_user=User(user_name=user, passhash=generate_password_hash(password),name=name,email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')

#user login
@user.route('/login',methods=['GET','POST'])
def login_user():
    if request.method=='POST':
        user= request.form.get('user')
        password= request.form.get('password')
        existing_user=User.query.filter(user==User.user_name).first()
        if user=='' or password=='':
            flash("* marked fields can't be empty")
            return redirect('/login')
        elif not existing_user:
            flash('User does not exist.')
            return redirect('/register')
        else:
            if not check_password_hash(existing_user.passhash,password):
                flash('Incorrect Password')
                return redirect('/login')
            else:
                session['user_id']=existing_user.user_id
                return redirect('/')
    return render_template('login.html')

#user functionalities
@user.route('/')
@auth
def home():
    l=[]
    user=User.query.get(session['user_id'])
    pbooks=Review.query.order_by(desc(Review.rating)).limit(5)
    lbooks=Books.query.order_by(desc(Books.book_id)).limit(5)
    comments=Review.query.order_by(desc(Review.rating)).limit(5)
    sections=Section.query.all()
    for x in pbooks:
        book=Books.query.get(x.book_id)
        if book not in l:
            l.append(book)
        else:
            continue
    return render_template('index.html',user=user.name,pbooks=l,lbooks=lbooks,comments=comments,sections=sections)

@user.route('/my_profile')
@auth
def user_profile():
    user_id=session['user_id']
    user=User.query.get(user_id)
    return render_template('my_profile.html',user=user)

@user.route('/edit_my_profile',methods=['GET','POST'])
@auth
def edit():
    to_edit=User.query.get(session['user_id'])
    if request.method=='POST':
        password=request.form['password']
        name=request.form['name']
        email=request.form['email']
        if password=='' or name=='':
            flash("*marked fields can't be empty.")
            return redirect('/edit_my_profile')
        elif len(password)<8 or len(password)>24:
            flash('Password length should be between 8 to 24 characters.')
            return redirect('/edit_my_profile')
        else:
            to_edit.passhash=generate_password_hash(password)
            to_edit.name=name
            to_edit.email=email
            db.session.commit()
            return redirect('/my_profile')
    return render_template('edit_user.html',to_edit=to_edit)

@user.route('/user_books')
@auth
def user_books():
    books=Books.query.all()
    for x in books:
        book_issued=Issued.query.filter(x.book_id==Issued.book_id).first()
        if not book_issued:
            x.available=True
    db.session.commit()
    return render_template('user_books.html', books=books)

@user.route('/book/<int:book_id>/request')
@auth
def request_book(book_id):
    user=session['user_id']
    availablity=Books.query.filter(book_id==Books.book_id).first()
    already_requested=Requests.query.filter(book_id==Requests.book_id, user==Requests.user_id).first()
    if already_requested:
        flash('Book already requested.')
        return redirect('/user_books')
    if availablity.available==False:
        flash('Book is not available.')
        return redirect('/user_books')
    requested_books=Requests.query.filter(user==Requests.user_id).all()
    issued_books=Issued.query.filter(user==Issued.user_id).all()
    if len(requested_books)+len(issued_books)>=5:
        flash('You can not request mpre than 5 books at a time.')
        return redirect('/user_books')
    requested_book=Requests(book_id=book_id, user_id=user)
    db.session.add(requested_book)
    db.session.commit()
    return redirect('/user_books')

@user.route('/my_books')
@auth
def my_books():
    user=session.get('user_id')
    books=Issued.query.filter(today>=Issued.return_date).delete()
    db.session.commit()
    res=db.session.query(Books,Issued).join(Issued).filter(user==Issued.user_id).all()
    return render_template('my_books.html',result=res)

@user.route('/my_books/<int:book_id>/return')
@auth
def return_book(book_id):
    to_return=Issued.query.filter(book_id==Issued.book_id).first()
    returned_book=Books.query.get(book_id)
    db.session.delete(to_return)
    returned_book.available=True
    db.session.commit()
    return redirect('/my_books')

@user.route('/book/<int:book_id>/rate',methods=['GET','POST'])
@auth
def rate_book(book_id):
    user_id=session.get('user_id')
    book=Books.query.get(book_id)
    if request.method=='POST':
        rating_str=request.form['rating']
        comment=request.form['comment']
        if comment=='':
            flash('Please comment on the book!')
        else:
            existing_review=Review.query.filter(user_id==Review.user_id,book_id==Review.book_id).first()
            if existing_review:
                existing_review.rating=int(rating_str)
                existing_review.comment=comment
                db.session.commit()
                return redirect('/user_books')
            else:
                new_review=Review(user_id=user_id,book_id=book_id,rating=int(rating_str),comment=comment)
                db.session.add(new_review)
                db.session.commit()
                return redirect('/user_books')
    return render_template('rate_form.html',book=book,user_id=user_id,book_id=book_id)

@user.route('/book/<int:section_id>/genre')
@auth
def browse_by_section(section_id):
    books=Books.query.filter(section_id==Books.genre_id).all()
    section=Section.query.get(section_id)
    return render_template('section_browse.html',books=books,section=section)

@user.route('/book/search',methods=['GET','POST'])
@auth
def search():
    if request.method=='POST':
        type=request.form['type']
        search=request.form['search']
        if type=='book_name':
            books=Books.query.filter(Books.name.like('%'+search+'%')).all()
        elif type=='author':
            books=Books.query.filter(Books.author.like('%'+search+'%')).all()
        return render_template('search_results.html',type=type,search=search,books=books)

@user.route('/book/<int:book_id>/<int:issue_id>/read')
@auth
def read_book(book_id,issue_id):
    book=Books.query.get(book_id)
    issue=Issued.query.get(issue_id)
    if issue.paid==True:
        return render_template('book_details_paid.html',book=book)
    else:
        return render_template('user_book_details.html',book=book)

@user.route('/book/<int:book_id>/payment',methods=['GET','POST'])           #dummy payment page.
@auth
def payment(book_id):
    book=Books.query.get(book_id)
    user=User.query.get(session['user_id'])
    issue=Issued.query.filter(book_id==Issued.book_id).first()
    if request.method=='POST':
        upi=request.form['upi_id']
        if not check_upi(upi):
            flash('Enter the correct UPI ID.')
            return redirect('/book/'+str(book_id)+'/payment')
        else:
            issue.paid=True
            db.session.commit()
            return render_template('book_details_paid.html',book=book)
    return render_template('payment_page.html',book=book,user=user)

#user logout
@user.route('/logout')
@auth
def logout():
    session.pop('user_id',None)
    return redirect('/login')