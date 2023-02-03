import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import glob
import speech_recognition as sr
from forms import ChooseLang

UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = set(['wav', 'mp3']) #допустимые расширения файлов

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'f3cf2de9e3dd8fae'

lang_menu = {'rus': 'ru-RU', 'eng': 'en-US', 'arab': 'ar-AE'}
selected_lang = ''

def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Проверяем, что файл передается. После перенаправляет на страницу с результатом
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    '''Функция обработки данных о выбранном языке. Данные берутся из формы form.py'''
    global selected_lang
    form = ChooseLang()
    if form.validate_on_submit():
        lang_var = '{}'.format(form.lang.data)
        selected_lang = lang_menu.get(lang_var)
        #return selected_lang #если необходимо вывести значение переменной, которую стравниваю со словарем

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))

    return render_template('index.html', form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """ Отбработка выбранного (последнего) файла """
    filename_list = glob.glob('files/*')
    filename = filename_list[-1]  # Последний файл

    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)  # read the entire audio file

# Удаляем все загруженные файлы, чтобы не переполнять память сервера
    all_files = './files'
    filelist = glob.glob(os.path.join(all_files, "*"))
    for f in filelist:
        os.remove(f)

    return r.recognize_google(audio, language=selected_lang)

if __name__ == "__main__":
     app.run(debug=True)
