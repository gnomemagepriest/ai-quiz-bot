from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import Quiz, UserQuizAttempt, UserAnswer, User, db
from .auth import create_token, get_user
from .models import Quiz, UserQuizAttempt, UserAnswer, db
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/login', methods=['POST'])
def login():
    return create_token()

@bp.route('/user', methods=['GET'])
@jwt_required()
def user():
    return get_user()

@bp.route('/')
def index():
	return 'Index Page'

@bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'created_at': quiz.created_at.isoformat(),
        'is_active': quiz.is_active,
        'questions': [{'id': q.id, 'text': q.text, 'question_type': q.question_type} for q in quiz.questions]
    })

@bp.route('/user_answers/<int:answer_id>', methods=['GET'])
def get_user_answer(answer_id):
    user_answer = UserAnswer.query.get_or_404(answer_id)
    return jsonify({
        'id': user_answer.id,
        'attempt_id': user_answer.attempt_id,
        'question_id': user_answer.question_id,
        'answer_text': user_answer.answer_text
    })

@bp.route('/attempts', methods=['POST'])
def create_attempt():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    user_id = data.get('user_id')

    if not quiz_id or not user_id:
        return jsonify({'error': 'quiz_id and user_id are required'}), 400

    attempt = UserQuizAttempt(quiz_id=quiz_id, user_id=user_id)
    db.session.add(attempt)
    db.session.commit()

    return jsonify({'id': attempt.id, 'quiz_id': attempt.quiz_id, 'user_id': attempt.user_id}), 201

@bp.route('/attempts/<int:attempt_id>', methods=['GET'])
def get_attempt(attempt_id):
    attempt = UserQuizAttempt.query.get_or_404(attempt_id)
    answers = [{'id': a.id, 'question_id': a.question_id, 'answer_text': a.answer_text} for a in attempt.answers]
    return jsonify({
        'id': attempt.id,
        'quiz_id': attempt.quiz_id,
        'user_id': attempt.user_id,
        'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
        'answers': answers
    })

@bp.route('/attempts/<int:attempt_id>/answers', methods=['POST'])
def add_user_answer(attempt_id):
    data = request.get_json()
    question_id = data.get('question_id')
    answer_text = data.get('answer_text')

    if not question_id or not answer_text:
        return jsonify({'error': 'question_id and answer_text are required'}), 400

    user_answer = UserAnswer(attempt_id=attempt_id, question_id=question_id, answer_text=answer_text)
    db.session.add(user_answer)
    db.session.commit()

    return jsonify({'id': user_answer.id, 'attempt_id': user_answer.attempt_id, 'question_id': user_answer.question_id, 'answer_text': user_answer.answer_text}), 201

@bp.route('/attempts/<int:attempt_id>/complete', methods=['POST'])
def complete_attempt(attempt_id):
    attempt = UserQuizAttempt.query.get_or_404(attempt_id)
    attempt.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'id': attempt.id, 'quiz_id': attempt.quiz_id, 'user_id': attempt.user_id, 'completed_at': attempt.completed_at.isoformat()}), 200
