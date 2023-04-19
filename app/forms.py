from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class CreateSurveyForm(FlaskForm):
    title = StringField('Survey Title', validators=[DataRequired()])
    submit = SubmitField('Create Survey')

class AddQuestionForm(FlaskForm):
    question_text = StringField('Question', validators=[DataRequired(), Length(min=1, max=200)])
    input_type = SelectField('Input Type', choices=[('text', 'Text'), ('number', 'Number')])
    input_length = IntegerField('Input Length', default=100)
    submit = SubmitField('Add Question')

class SurveyResponseForm(FlaskForm):
    response = TextAreaField('Response', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Submit Response')

class AddQuestionsForm(FlaskForm):
    question_text = StringField('Question', validators=[DataRequired()])
    add_another = BooleanField('Add another question')
    submit = SubmitField('Submit')
