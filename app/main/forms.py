from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, SelectMultipleField, BooleanField, SelectField, widgets
from wtforms.validators import Required, DataRequired
from flask.ext.pagedown.fields import PageDownField

class DeleteForm(Form):
	submit = SubmitField('Yes')


class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')


type = [('Birth','Birth'), ('Death','Death'), ('Marriage','Marriage'),
        ('Marriage License', 'Marriage License')]

borough = [('Manhattan','Manhattan'), ('Bronx','Bronx'), ('Brooklyn', 'Brooklyn'),
           ('Queens', 'Queens'), ('Richmond', 'Richmond')]


class NameForm(Form):
    type = SelectField(
        'Type:',
        choices=type,
        option_widget=widgets.RadioInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )
    name = StringField('Name:', validators=[DataRequired()])
    bride_name = StringField('Bride\'s Name:')
    year = StringField('Year:', validators=[DataRequired()])
    borough = SelectMultipleField(
        'Borough:',
        choices=borough,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )
    signature = BooleanField('Print without Signature:')
    submit = SubmitField('Print')