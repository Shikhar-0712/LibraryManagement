from flask import Flask
from flask_security import SQLAlchemyUserDatastore , Security
from applications.models import db , User, Role
from config import DevelopmentConfig
from applications.resources import api
from applications.sec import datastore
from applications.worker import celery_init_app
#import flask_excel as excel
from celery.schedules import crontab
from applications.tasks import daily_reminder, send_monthly_reports
from applications.instances import cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app) 
    api.init_app(app)
    #excel.init_excel(app)
    app.security=Security(app,datastore)
    cache.init_app(app)
    with app.app_context():
        import applications.views
    return app

app=create_app()

celery_app=celery_init_app(app)

@celery_app.on_after_configure.connect
def send_email(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=19, minute=47),
        daily_reminder.s('Daily Reminder'),
    )

@celery_app.on_after_configure.connect
def send_email_monthly(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=19, minute=47 , day_of_month=14), send_monthly_reports.s(),
    )

if __name__ == '__main__':
    app.run(debug=True)