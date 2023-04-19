from flask import render_template, flash, redirect, url_for, request, make_response, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Survey, Question, Response
from app.forms import LoginForm, RegistrationForm, CreateSurveyForm, AddQuestionForm, SurveyResponseForm
from app import routes
from werkzeug.urls import url_parse
import csv
from io import StringIO

bp = Blueprint('routes', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    is_admin = False
    surveys = Survey.query.order_by(Survey.timestamp.desc()).all()
    if current_user.is_authenticated:
        is_admin = current_user.is_admin  # Check if the current user is an admin
    return render_template('index.html', title='Home', surveys=surveys, is_admin=is_admin)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('routes.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('routes.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for
    ('routes.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        if User.query.count() == 0:
            user.is_admin = True
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    form = CreateSurveyForm()
    if form.validate_on_submit():
        survey = Survey(title=form.title.data, author=current_user)
        db.session.add(survey)
        db.session.commit()
        flash('Your survey is now live!')
        return redirect(url_for('routes.add_questions', survey_id=survey.id))
    return render_template('create_survey.html', title='Create Survey', form=form)

@bp.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    form = AddQuestionForm()
    if form.validate_on_submit():
        question = Question(text=form.question_text.data, input_type=form.input_type.data, input_length=form.input_length.data, survey=survey)
        db.session.add(question)
        db.session.commit()
        flash('Your question has been added to the survey.')
        return redirect(url_for('routes.survey', survey_id=survey.id))
    questions = survey.questions.all()
    return render_template('survey.html', title=survey.title, survey=survey, form=form, questions=questions)

@bp.route('/take_survey/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def take_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    questions = survey.questions.all()
    form = SurveyResponseForm()
    if request.method == 'POST':
        for question in questions:
            response_text = request.form.get(f'question_{question.id}')
            response = Response(user_id=current_user.id, question_id=question.id, response_text=response_text)
            db.session.add(response)
            db.session.commit()
        flash('Your survey responses have been recorded.')
        return redirect(url_for('routes.index'))
    return render_template('take_survey.html', title=survey.title, survey=survey, questions=questions, form=form)

@bp.route('/view_results/<int:survey_id>')
@login_required
def view_results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if not current_user.is_admin:
        flash('You do not have permission to view the results.')
        return redirect(url_for('routes.index'))
    questions = survey.questions.all()
    return render_template('view_results.html', title=survey.title, survey=survey, questions=questions)

@bp.route('/export_csv/<int:survey_id>')
@login_required
def export_csv(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if not current_user.is_admin:
        flash('You do not have permission to export the data.')
        return redirect(url_for('routes.index'))
    questions = survey.questions.all()
    si = StringIO()
    cw = csv.writer(si)
    headers = ['Username', 'Question', 'Response']
    cw.writerow(headers)
    for question in questions:
        responses = question.responses.all()
        for response in responses:
            user = User.query.get(response.user_id)
            cw.writerow([user.username, question
        .text, response.response_text])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=survey_{survey_id}_results.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@bp.route('/add_questions/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def add_questions(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    form = AddQuestionForm()
    if form.validate_on_submit():
        question = Question(question_text=form.question_text.data, survey_id=survey.id)
        db.session.add(question)
        db.session.commit()
        if form.add_another.data:
            return redirect(url_for('routes.add_questions', survey_id=survey.id))
        else:
            return redirect(url_for('index'))
    return render_template('routes.add_questions.html', title='Add Questions', form=form, survey=survey)
