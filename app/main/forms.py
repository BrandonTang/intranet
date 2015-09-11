from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.pagedown.fields import PageDownField

class DeleteForm(Form):
	confirm = SubmitField('Yes')


class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')