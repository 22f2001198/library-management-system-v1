from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_restful import Resource, Api, fields, reqparse, marshal_with

db=SQLAlchemy()

def create_app():
    #app creation
    app=Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY']='somekey'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///project_db.sqlite3'
    db.init_app(app)
    api=Api(app)          #api initialisation

    #importing components
    from admin_routes import admin
    from user_routes import user
    from all_api import SectionApi, BookApi, GetGraph, TopComments
    

    #registering blueprint
    app.register_blueprint(admin,url_prefix='/')
    app.register_blueprint(user,url_prefix='/')

    #adding api resources
    api.add_resource(SectionApi,'/api/section/<int:section_id>','/api/section')
    api.add_resource(BookApi,'/api/book/<int:book_id>','/api/book')
    api.add_resource(GetGraph,'/api/graph')
    api.add_resource(TopComments,'/api/comments')

    #getting db models
    from model import Admin, User, Section, Books, Review, Requests, Issued
    create_database(app)
    return app

def create_database(app):
    if not path.exists("/project_db"):
        with app.app_context():
            db.create_all()