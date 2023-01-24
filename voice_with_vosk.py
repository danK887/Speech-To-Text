from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import glob
from pydub import AudioSegment
import json
import wave
from moviepy.editor import *
from vosk import Model, KaldiRecognizer
from forms import ChooseLang


UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = set(['wav', 'mp4', 'mp3']) #допустимые расширения файлов

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'f3cf2de9e3dd8fae'

#Словарь и переменная нужны для взаимодействия с выбранным языком в форме. Данные сравниваются с ключем словаря и значение записывается в переменную
lang_menu = {'rus': 'vosk-model-small-ru-0.22', 'eng': 'vosk-model-small-en-us-0.15'}
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

    # Если загружено видео, вытаскиваем из видео звуковую дорожку
    audioclip = AudioFileClip(filename)
    audioclip.write_audiofile("our_sound.wav")

    '''преобразуем звуковую дорожку из стерео в моно и сохраняем в аудио файл с названием our_sound.wav 
    для дальнейшей работы с ним'''
    sound = AudioSegment.from_wav("our_sound.wav")
    sound = sound.set_channels(1)
    sound.export("our_sound.wav", format="wav")

    wf = wave.open("our_sound.wav", "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    # You can also init model by name or with a folder path
    model = Model(model_name=selected_lang)
    # selected_lang - переменная, которая говорит, какую модель нужно использовать в соответсвии с языком

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass

    wf.close()

    # создаем текстовый документ, куда записываем результат обработки
    with open("text_voice/voice_text.txt", "w", encoding="utf-8") as file:
        rec_text = json.loads(rec.FinalResult())
        file.write(f'{rec_text.get("text")}\n')

    # Удаляем все загруженные файлы, чтобы не переполнять память сервера
    all_files = './files'
    filelist = glob.glob(os.path.join(all_files, "*"))
    for f in filelist:
        os.remove(f)

    return f'<h2>{rec_text.get("text")}</h2>'



if __name__ == "__main__":
    app.run(debug=True)
