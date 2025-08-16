from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .models import User, Quiz, Question, QuestionOption, UserQuizAttempt, UserAnswer
from .extensions import db

def create_admin(app):
    try:
        admin = Admin(app, name='AI Quiz Bot Admin', template_mode='bootstrap3')
        admin.add_view(ModelView(User, db.session))
        admin.add_view(ModelView(Quiz, db.session))
        admin.add_view(ModelView(Question, db.session))
        admin.add_view(ModelView(QuestionOption, db.session))
        admin.add_view(ModelView(UserQuizAttempt, db.session))
        admin.add_view(ModelView(UserAnswer, db.session))
    except Exception as e:
        app.logger.error(f"Failed to initialize admin panel: {e}")
