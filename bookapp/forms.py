from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import StringField,SubmitField,TextAreaField,PasswordField
from wtforms.validators import Email,DataRequired,EqualTo,Length

class RegForm(FlaskForm):
    fullname = StringField("First Name",validators=[DataRequired(message="The Firstname is a must")])
    email = StringField("Email",validators=[Email(message="Invalid Email format"),DataRequired()])
    pwd = PasswordField("Enter Password",validators=[DataRequired(message="Enter Password")])
    confirmpwd = PasswordField("Enter Password",validators=[EqualTo("pwd",message="bros, Let the two passwords match")])
    profile= TextAreaField("Your Profile")
    btnsubmit = SubmitField("Register!")


class Dpform(FlaskForm):
    dp = FileField('Upload A Profile Picture', validators=[FileRequired(), FileAllowed(['jpg','png','jpeg'])])
    btnupload =SubmitField('Upload Your Picture')

class Profileform(FlaskForm):
    fullname = StringField("First Name",validators=[DataRequired(message="The Fullname is a must")])
    btnsubmit =SubmitField('Submit')


class Contact(FlaskForm):
    email = StringField("Email",validators=[Email(message="Invalid Email format")])
    submit =SubmitField('Subscribe')
