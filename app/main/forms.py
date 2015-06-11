from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.pagedown.fields import PageDownField

class PostForm(Form):
    title = StringField('Title', validators=[Required()])
    text = PageDownField('Text', validators=[Required()])
    submit = SubmitField('Submit')

class DeleteForm(Form):
	confirm = SubmitField('Yes')