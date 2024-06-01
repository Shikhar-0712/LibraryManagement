from celery import shared_task
from sqlalchemy import or_
from .models import Book
from .mail_service import send_message
from .models import User, Role, Book , BookIssuance,Section,Feedback,db
from jinja2 import Template
import os
from datetime import datetime, timedelta



# Get the directory of the current file
current_directory = os.path.dirname(os.path.abspath(__file__))
# Construct the absolute path to test.html
html_file_path = os.path.join(current_directory, 'test.html')
html_file_path1 = os.path.join(current_directory, 'report.html')


@shared_task(ignore_result=True)
def daily_reminder(subject):
    users = User.query.filter(User.roles.any(Role.name == 'user')).all()
    for user in users:
        if user and user.last_login_at:
            time = datetime.utcnow() - user.last_login_at
            if time.days >=  1:
                with open(html_file_path, 'r') as f:
                    template = Template(f.read())
                    send_message(user.email, subject,
                                template.render(email=user.email , user=user.username))
    return "OK"

@shared_task(ignore_result=True)
def send_monthly_reports():
    users = User.query.filter(User.roles.any(Role.name == 'user')).all()
    for user in users:
        print("monthly report for", user.email)
        monthly_report.delay(user.id, user.email, 'Monthly Report')

@shared_task(ignore_result=True)
def monthly_report(id, to, subject):
    books_issued = db.session.query(BookIssuance, Book) \
        .join(Book) \
        .filter(BookIssuance.user_id == id) \
        .filter(or_(BookIssuance.returned_at == None, BookIssuance.returned_at > datetime.now())) \
        .all()

    # books_issued = db.session.query(BookIssuance, Book) \
    # .join(Book) \
    # .filter(BookIssuance.user_id == id, \
    #         (BookIssuance.returned_at == None) | (BookIssuance.returned_at > datetime.now())) \
    # .all()


    books_data = []
    feed=[]

    feedbacks = db.session.query(Feedback, Book) \
        .join(Book) \
        .filter(Feedback.book_id == Book.id) \
        .all()

    for f,b in feedbacks:
        feed_data={
            "feedback":f.text,
            "rating":f.rating,
            "bid":b.id,
        } 
        feed.append(feed_data)

    for issuance, book in books_issued:
        book_data = {
            "id": book.id,
            "name": book.name,
            "content": book.content,
            "author": book.author,
            "date_issue": issuance.issued_at.strftime("%Y-%m-%d") if issuance.issued_at else None,
        }
        books_data.append(book_data)
    

    with open(html_file_path1, 'r') as f:
        template = Template(f.read())
        # a template needs to be used to generate the email content, such that i accepts the data 
        send_message(to=to,subject=subject,
                    content_body=template.render(email=to , books_data=books_data , feed=feed))
    return "OK"


    
  