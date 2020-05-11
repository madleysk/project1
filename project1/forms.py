from wtforms import Form, BooleanField, StringField, PasswordField, SelectField, HiddenField, FileField, validators
from wtforms.fields.html5 import DateField, TelField, EmailField

class RegistrationForm(Form):
	username = StringField('Username',[validators.Length(min=4,max=30)])
	passwd = PasswordField('Password',[validators.DataRequired(),validators.EqualTo('pwd_confirm', message='Passwords must match')])
	pwd_confirm = PasswordField('Confirm Password')
	auth_level = HiddenField('Role',[validators.DataRequired()])
	code = StringField('Code',[validators.Length(min=2,max=10,message='Code invalide')])

class LoginForm(Form):
	username = StringField('Username',[validators.Length(min=4,max=30)])
	passwd = PasswordField('Password',[validators.DataRequired()])
