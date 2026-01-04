from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.exceptions import HTTPException
import datetime
from model import db, Section, Books, Issued, Review
from sqlalchemy import desc
import io
import base64
from matplotlib import pyplot as plt
plt.switch_backend('agg')

class NotFoundError(HTTPException):
    def __init__(self,error_message):
        message={
            'error message':error_message
        }
        self.response=make_response(jsonify(message),404)

class ValidationError(HTTPException):
    def __init__(self,error_message):
        message={
            'error message':error_message
        }
        self.response=make_response(jsonify(message),409)

class BadRequestError(HTTPException):
    def __init__(self,error_message):
        message={
            'error message':error_message
        }
        self.response=make_response(jsonify(message),400)

section_parser=reqparse.RequestParser()
section_parser.add_argument('input_name')
section_parser.add_argument('input_description')

class SectionApi(Resource):
    def get(self,section_id=None):
        section=Section.query.get(section_id)
        if section:
            output={
                'id':section.section_id,
                'name':section.name,
                'date_created':section.date_created,
                'description':section.description
            }
            return make_response(jsonify(output),200)
        else:
            raise NotFoundError(error_message='No Genre of id '+str(section_id)+' exists.')
        
    def post(self):
        arglist=section_parser.parse_args()
        input_name=arglist.get('input_name',None)
        input_description=arglist.get('input_description',None)
        if not input_name:
            raise BadRequestError(error_message='Name is required for the genre.')
        elif not input_description:
            raise BadRequestError(error_message='Please give a description for the Genre.')
        genre_exists=Section.query.filter(input_name==Section.name).first()
        if genre_exists:
            raise ValidationError(error_message='Genre already exists.')
        else:
            new_genre=Section(name=input_name,date_created=datetime.date.today(),description=input_description)
            db.session.add(new_genre)
            db.session.commit()
            message={
                'message':'Sucessfully Created.'
            }
            return make_response(jsonify(message),201)
    
    def put(self,section_id):
        genre_exists=Section.query.filter(section_id==Section.section_id).first()
        if not genre_exists:
            raise NotFoundError(error_message='No such Genre exists.')
        arglist=section_parser.parse_args()
        input_name=arglist.get('input_name',None)
        input_description=arglist.get('input_description',None)
        if not input_name:
            raise BadRequestError(error_message='Name is required for the genre.')
        elif not input_description:
            raise BadRequestError(error_message='Please give a description for the Genre.')
        else:
            genre_exists.name=input_name
            genre_exists.date_created=datetime.date.today()
            genre_exists.description=input_description
            db.session.commit()
            message={
                'message':'Sucessfully updated.'
            }
            return make_response(jsonify(message),200)
        
    def delete(self,section_id):
        to_delete=Section.query.get(section_id)
        if not to_delete:
            raise NotFoundError(error_message='Genre to be deleted does not exist.')
        else:
            db.session.delete(to_delete)
            db.session.commit()
            message={
                'message':'Sucessfully deleted.'
            }
            return make_response(jsonify(message),200)

book_parser=reqparse.RequestParser()
book_parser.add_argument('input_name')
book_parser.add_argument('input_author')
book_parser.add_argument('input_content')
book_parser.add_argument('input_genre')
book_parser.add_argument('input_price')

class BookApi(Resource):
    def get(self,book_id=None):
        book=Books.query.get(book_id)
        if book:
            availablity=Issued.query.filter(book_id==book_id).first()
            if not availablity:
                book.avilable=True
            else:
                book.avilable=False
            output={
                'id':book.book_id,
                'name':book.name,
                'author':book.author,
                'content':book.content,
                'genre_id':book.genre_id,
                'price':book.price,
                'available':book.available
            }
            return make_response(jsonify(output),200)
        else:
            raise NotFoundError(error_message='No Book of id '+str(book_id)+' exists.')
    
    def post(self):
        arglist=book_parser.parse_args()
        input_name=arglist.get('input_name',None)
        input_author=arglist.get('input_author',None)
        input_content=arglist.get('input_content',None)
        input_genre=arglist.get('input_genre',None)
        input_price=arglist.get('input_price',None)
        if not input_name:
            raise BadRequestError(error_message='Name is required for the book.')
        elif not input_author:
            raise BadRequestError(error_message='Please give a Author Name for the Book.')
        elif not input_content:
            raise BadRequestError(error_message='Please give some Content for the Book.')
        elif not input_genre:
            raise BadRequestError(error_message='Please put a Genre on the Book.')
        elif not input_price:
            raise BadRequestError(error_message='Please input a Price for the Book.')
        book_exists=Books.query.filter(input_name==Books.name).first()
        genre_list=Section.query.all()
        l=[]
        for x in genre_list:
            l.append(x.section_id)
        if int(input_genre) not in l:
            raise BadRequestError(error_message='This Genre is not available. Available Genre_ids are '+str(l)+'.')
        elif book_exists:
            raise ValidationError(error_message='Book already exists.')
        else:
            new_book=Books(name=input_name,author=input_author,content=input_content,genre_id=int(input_genre),price=float(input_price),available=True)
            db.session.add(new_book)
            db.session.commit()
            message={
                'message':'Sucessfully Added.'
            }
            return make_response(jsonify(message),201)
    
    def put(self,book_id):
        book_exists=Books.query.filter(book_id==Books.book_id).first()
        if not book_exists:
            raise NotFoundError(error_message='No such Book exists.')
        arglist=book_parser.parse_args()
        input_name=arglist.get('input_name',None)
        input_author=arglist.get('input_author',None)
        input_content=arglist.get('input_content',None)
        input_genre=arglist.get('input_genre',None)
        input_price=arglist.get('input_price',None)
        if not input_name:
            raise BadRequestError(error_message='Name is required for the Book.')
        elif not input_author:
            raise BadRequestError(error_message='Please give a Author Name for the Book.')
        elif not input_content:
            raise BadRequestError(error_message='Please give some Content for the Book.')
        elif not input_genre:
            raise BadRequestError(error_message='Please put a Genre on the Book.')
        elif not input_price:
            raise BadRequestError(error_message='Please input a Price for the Book.')
        else:
            book_exists.name=input_name
            book_exists.author=input_author
            book_exists.content=input_content
            book_exists.genre_id=input_genre
            book_exists.price=input_price
            db.session.commit()
            message={
                'message':'Sucessfully updated.'
            }
            return make_response(jsonify(message),200)
    
    def delete(self,book_id):
        to_delete=Books.query.get(book_id)
        if not to_delete:
            raise NotFoundError(error_message='Book to be deleted does not exist.')
        else:
            db.session.delete(to_delete)
            db.session.commit()
            message={
                'message':'Sucessfully deleted.'
            }
            return make_response(jsonify(message),200)

class GetGraph(Resource):
    def get(self):
        books=Books.query.all()
        if not books:
            raise NotFoundError(error_message='No books found.')
        d={}
        for x in books:
            book=Review.query.filter(x.book_id==Review.book_id).all()
            sum=0
            count=0
            for y in book:
                sum+=y.rating
                count+=1
            if count>0:
                d[x.name]=sum/count
            else:
                d[x.name]=0
        a=list(d.keys())
        b=list(d.values())
        plt.plot(a,b)
        plt.xlabel('Rating')
        plt.ylabel('books')
        plt.title('Book Ratings')
        graph=io.BytesIO()
        plt.savefig(graph,format='png')
        graph.seek(0)
        plt.close()
        graph_bytes=base64.b64encode(graph.read()).decode('utf-8')
        return jsonify({'Rating Graph':graph_bytes})

class TopComments(Resource):
    def get(self):
        comments=Review.query.order_by(desc(Review.rating)).limit(5)
        d={}
        if not comments:
            raise NotFoundError(error_message='There are no comments from users.')
        for x in comments:
            d[x.user_id]=x.comment
        return make_response(jsonify(d),200)