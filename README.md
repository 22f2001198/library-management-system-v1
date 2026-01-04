# Description 
LMS is a multiuser library management app with one admin/librarian, where users can 
read, download and comment on the books available. 
# Technologies Used 
• **Flask**: For basic background implementation.

• **Flask_sqlalchemy**: For implementing database.

• **Datetime**: For storing dates.

• **Inbuilt libraries**: jinja2, render_template, redirect, etc.

• **Flash**: For showing messages/alerts.

• **Werkzeug.security**: For hashing password.

• **Flask_restful**: For CRUD by api. 
# API Design 
There are four API:

• **SectionApi**: It is connected to two api - /api/section/<int:section_id>, /api/section

• **BookApi**: It is connected to two api - /api/book/<int:book_id>, /api/book 

• **GetGraph**: It is connected to one api - /api/graph 

• **TopComments**: It is connected to one api - /api/comments
# Architecture and Features 
➢ There are two controllers: 

• **Admin_routes**: It contains all the functions for admin/librarian. 

• **User_routes**: It contains all the functions for the users. 

➢ There are three folders:

• **Static**: It contains all the images, pdf (books).(Contains a dummy text file to help with uploading the project.)  

• **Templates**: It contains all the html templates used. 

• **Instance**: It contains the sqlite3 database. (will be created upon initialization of flask app.) 

➢ **Login/signup**: admin and user both have to login to access the app. And user can 
sign up also. 

➢ **Profile view**: admin and user both can view and edit their profiles. 

➢ **Book & section management**: Admin can perform CRUD on books and sections. 

➢ **Search**: admin and user both can search for books by name and author. 

➢ **Browse**: admin and user both can browse for books by section. 

➢ **Rate/comment**: user can rate and comment on any book. 

➢ **Request/Issue**: user can request and admin can issue any book.
