from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class ChooseLang(FlaskForm):
    lang = SelectField("Язык", choices=[("rus", "Русский"), ("eng", "Английский")])
    submit = SubmitField("Выбрать")
