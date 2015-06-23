from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required
from flask.ext.pagedown.fields import PageDownField

class PostForm(Form):
    tag = SelectField('Tag', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')])
    title = StringField('Title', validators=[Required()])
    text = PageDownField('Text', validators=[Required()])
    submit = SubmitField('Submit')

class DeleteForm(Form):
	confirm = SubmitField('Yes')