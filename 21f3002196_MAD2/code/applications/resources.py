from flask_restful import Resource,Api, reqparse, marshal_with, fields
from flask_security import auth_required , roles_required, roles_accepted, auth_token_required
from .models import BookIssuance, Feedback, Section,Book ,db
from datetime import datetime
from .instances import cache

api=Api(prefix='/api')

section_parser = reqparse.RequestParser()
section_parser.add_argument('name', type=str, help='Section name', required=True)
section_parser.add_argument('description', type=str, help='Section description', required=True)

book_parser = reqparse.RequestParser()
book_parser.add_argument('name', type=str, help='Book name', required=True)
book_parser.add_argument('content', type=str, help='Book content', required=True)
book_parser.add_argument('author', type=str, help='Book author', required=True)
book_parser.add_argument('quantity', type=int, help='Quantity of books', default=1)
book_parser.add_argument('section_id', type=int, help='ID of section to which the book belongs', required=True)

section_fields = {
    'id':fields.Integer,
    'name':fields.String,
    'description':fields.String
}

book_fields = {
    'id':fields.Integer,
    'name':fields.String,
    'content':fields.String,
    'author':fields.String,
    'quantity':fields.Integer,
    'section_id':fields.Integer
}
class test(Resource):
    @auth_token_required
    @roles_accepted('user')
    def post(self):
        return {'message':'Hello World'}
api.add_resource(test,'/test')

class SectionApi(Resource):
    @auth_required('token')
    @marshal_with(section_fields)
    @cache.cached(timeout=10)
    def get(self):
        all_sections=Section.query.all()
        return all_sections
    
    @auth_required('token')
    @roles_required('librarian')
    def post(self):
        args = section_parser.parse_args()
        sec=Section(name=args.get("name"),description=args.get("description"),date_created=datetime.now())
        db.session.add(sec)
        db.session.commit()
        return {'message':'Section created'}
    
    @auth_required('token')
    @roles_required('librarian')
    def patch(self, id):
        args = section_parser.parse_args()
        name=args.get("name")
        description=args.get("description")
        sec=Section.query.get(id)
        if sec:
            if name:
                sec.name=name
            if description:
                sec.description=description
            db.session.commit()
            return {'message':'Section updated'}
        return{'path_var': id, 'name':name, 'description':description}
    
    @auth_required('token')
    @roles_required('librarian')
    def delete(self, id):
        sec = Section.query.get(id)
        if sec:
            # Delete all books associated with this section
            books_to_delete = Book.query.filter_by(section_id=id).all()
            for book in books_to_delete:
                feedbacks = Feedback.query.filter_by(book_id=book.id).all()
                book_issuances = BookIssuance.query.filter_by(book_id=book.id).all()
                
                for issuance in book_issuances:
                    db.session.delete(issuance)

                # Delete the associated feedback records
                for feedback in feedbacks:
                    db.session.delete(feedback)

                # Commit the changes to delete the feedback records
                db.session.commit()

                # Now delete the book itself
                book = Book.query.get_or_404(book.id)
                db.session.delete(book)

            db.session.delete(sec)
            db.session.commit()
            return {'message': 'Section and associated books deleted'}
        else:
            return{ 'message':'Section not found'}

class BookApi(Resource):
    @marshal_with(book_fields)
    @auth_required('token')
    @cache.cached(timeout=20)
    def get(self):
        all_books=Book.query.all()
        return all_books

    @auth_required('token')
    @roles_required('librarian')
    def post(self):
        args = book_parser.parse_args()
        name=args.get("name")
        content=args.get("content")
        author=args.get("author")
        quantity=args.get("quantity")
        section_id=args.get("section_id")
        print(name,content,author,quantity,section_id)
        book=Book(name=name,content=content,author=author,quantity=quantity,section_id=section_id)
        db.session.add(book)
        db.session.commit()  
        return {'message':'Book created', 'name':name, 'content':content, 'author':author, 'quantity':quantity, 'section_id':section_id} 
    
    @auth_required('token')
    @roles_required('librarian')
    def put(self, id):
        args = book_parser.parse_args()
        book = Book.query.get_or_404(id)
        
        book.name = args.get("name", book.name)
        book.content = args.get("content", book.content)
        book.author = args.get("author", book.author)
        book.quantity = args.get("quantity", book.quantity)
        book.section_id = args.get("section_id", book.section_id)
        
        db.session.commit()
        
        return {'message': 'Book updated', 'id': id}

    @auth_required('token')
    @roles_required('librarian')
    def delete(self, id):
        # book = Book.query.get_or_404(id)
        # db.session.delete(book)
        # db.session.commit()
        # return {'message': 'Book deleted', 'id': id}
        feedbacks = Feedback.query.filter_by(book_id=id).all()
        book_issuances = BookIssuance.query.filter_by(book_id=id).all()
        
        for issuance in book_issuances:
            db.session.delete(issuance)

        # Delete the associated feedback records
        for feedback in feedbacks:
            db.session.delete(feedback)

        # Commit the changes to delete the feedback records
        db.session.commit()

        # Now delete the book itself
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()

        return {'message': 'Book and associated feedback deleted', 'id': id}
        
    

api.add_resource(SectionApi,'/section', '/section/<int:id>')
api.add_resource(BookApi,'/book', '/book/<int:id>')