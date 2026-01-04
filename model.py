from init import db
import datetime

class Admin(db.Model):
    __tablename__='admin'
    admin_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    admin_name=db.Column(db.String(50),nullable=False,unique=True)
    passhash=db.Column(db.String(200),nullable=False)
    name=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(30),nullable=False)

class User(db.Model):
    __tablename__='user'
    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_name=db.Column(db.String(50),nullable=False,unique=True)
    passhash=db.Column(db.String(200),nullable=False)
    name=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(30),nullable=False)
    review=db.relationship('Review',back_populates='user',cascade='all, delete-orphan')
    requests=db.relationship('Requests',back_populates='user',cascade='all, delete-orphan')
    issued=db.relationship('Issued',back_populates='user',cascade='all, delete-orphan')

class Section(db.Model):
    __tablename__='section'
    section_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(20),nullable=False)
    date_created=db.Column(db.Date,default=datetime.date.today())
    description=db.Column(db.String(100))
    books=db.relationship('Books',back_populates='section',passive_deletes='all')

class Books(db.Model):
    __tablename__='books'
    book_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(20),nullable=False)
    imgname=db.Column(db.String)
    author=db.Column(db.String(20))
    content=db.Column(db.String())
    genre_id=db.Column(db.Integer,db.ForeignKey('section.section_id',ondelete='SET NULL'))
    price=db.Column(db.Numeric(precision=10,scale=2),default=0.00)
    available=db.Column(db.Boolean,default=True,nullable=False)
    filename=db.Column(db.String,nullable=False)
    section=db.relationship('Section',back_populates='books')
    review=db.relationship('Review',back_populates='books',cascade='all, delete-orphan')
    requests=db.relationship('Requests',back_populates='books',cascade='all, delete-orphan')
    issued=db.relationship('Issued',back_populates='books',cascade='all, delete-orphan')

class Review(db.Model):
    __tablename__='review'
    review_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    book_id=db.Column(db.Integer,db.ForeignKey('books.book_id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    rating=db.Column(db.Integer,nullable=False)
    comment=db.Column(db.String)
    books=db.relationship('Books',back_populates='review')
    user=db.relationship('User',back_populates='review')

class Requests(db.Model):
    __tablename__='requests'
    request_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    book_id=db.Column(db.Integer,db.ForeignKey('books.book_id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    books=db.relationship('Books',back_populates='requests')
    user=db.relationship('User',back_populates='requests')

class Issued(db.Model):
    __tablename__='issued'
    issue_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    book_id=db.Column(db.Integer,db.ForeignKey('books.book_id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    issue_date=db.Column(db.Date,default=datetime.date.today())
    paid=db.Column(db.Boolean,default=False)
    return_date=db.Column(db.Date)
    books=db.relationship('Books',back_populates='issued')
    user=db.relationship('User',back_populates='issued')