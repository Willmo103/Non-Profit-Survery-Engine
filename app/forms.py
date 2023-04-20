from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    SelectField,
    IntegerField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")


class AdminUserForm(FlaskForm):
    is_admin = BooleanField(
        "Admin User",
        default=False,
        description="Check this box if you want to make this user an admin.",
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Update User")


class CreateSurveyForm(FlaskForm):
    title = StringField("Survey Title", validators=[DataRequired()])
    submit = SubmitField("Create Survey")
    is_anonymous = BooleanField(
        "Anonymous Survey",
        default=False,
        description="Check this box if you want to hide the names of the respondents.",
    )


class AddQuestionForm(FlaskForm):
    question_text = StringField(
        "Question", validators=[DataRequired(), Length(min=1, max=200)]
    )
    input_type = SelectField(
        "Input Type", choices=[("text", "Text"), ("number", "Number")]
    )
    input_length = IntegerField("Input Length", default=100)
    add_another = BooleanField("Add Another Question", default=False)
    submit = SubmitField("Add Question")

    def validate_input_length(self, input_length):
        if input_length.data < 1:
            raise ValidationError("Input length must be greater than 0.")

    def validate_input_type(self, input_type):
        if input_type.data not in ["text", "number"]:
            raise ValidationError("Input type must be either text or number.")

    def validate_question_text(self, question_text):
        if len(question_text.data) > 200:
            raise ValidationError("Question text must be less than 200 characters.")


class SurveyResponseForm(FlaskForm):
    response = TextAreaField(
        "Response", validators=[DataRequired(), Length(min=1, max=200)]
    )
    submit = SubmitField("Submit Response")
