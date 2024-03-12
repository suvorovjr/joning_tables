import glob
from DFManager import DFManager
from flask import Flask, render_template, request, url_for, redirect, g, send_file
from pathlib import Path
import os

UPLOAD_FOLDER = Path(__file__).parent
ALLOWED_EXTENSIONS = ['csv']
DATABASE = 'database'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_df_manager():
    csv_file_tut = ''.join(glob.glob('*tut.csv'))
    csv_file_ru = ''.join(glob.glob('*ru.csv'))
    if 'df_manager' not in g:
        # Создаем экземпляр кастомного класса, если его нет в контексте g
        g.df_manager = DFManager(csv_file_tut, csv_file_ru, DATABASE)
    return g.df_manager


@app.route('/', methods=['GET', 'POST'])
def uploaded_files():
    if request.method == 'POST':
        files = request.files.getlist("file")
        for file in files:
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        csv_file_tut = ''.join(glob.glob('*tut.csv'))
        csv_file_ru = ''.join(glob.glob('*ru.csv'))
        if len(files) == 2 and csv_file_tut and csv_file_ru:
            df_manager = DFManager(csv_file_tut, csv_file_ru, DATABASE)
            df_manager.delete_colons()
            df_manager.merge_files()
            df_manager.save_db()
            return redirect(url_for('columns'))
        else:
            return render_template('error.html')
    else:
        if os.path.exists(f'{DATABASE}.db') or len(glob.glob('*.csv')):
            text = 'Необходимо либо продолжить работу в сессии, либо ее завершить'
            show_button = False
        else:
            text = 'Загрузите файлы santehnika-tut и santehnika-ru'
            show_button = True
        return render_template('upload.html', text=text, show_button=show_button)


@app.route('/columns/', methods=['GET', 'POST'])
def columns(column_name=None):
    if request.method == 'POST':
        new_column_name = request.form['new_column_name']
        return redirect(url_for('change_column', column_name=column_name, new_column_name=new_column_name))
    elif request.method == 'GET':
        df_manager = get_df_manager()
        df_manager.get_data()
        all_columns = df_manager.get_all_columns()
        return render_template('columns.html', columns=all_columns)


@app.route('/delete_column/<column_name>')
def delete_column(column_name):
    df_manager = get_df_manager()
    df_manager.get_data()
    df_manager.delete_column(column_name)
    df_manager.save_db()
    return redirect(url_for('columns'))


@app.route('/change_column/<column_name>', methods=['GET', 'POST'])
def change_column(column_name):
    if request.method == 'POST':
        new_column_name = request.form['new_column_name']
        df_manager = get_df_manager()
        df_manager.get_data()
        df_manager.change_column_name(column_name, new_column_name)
        df_manager.save_db()
        return redirect(url_for('columns'))


@app.route('/values/<column_name>/', methods=['GET', 'POST'])
def values(column_name):
    if request.method == 'POST':
        old_value = request.form['hidden_field']
        new_value = request.form['new_value']
        return redirect(url_for('change_value', column_name=column_name, old_value=old_value, new_value=new_value))
    elif request.method == 'GET':
        df_manager = get_df_manager()
        df_manager.get_data()
        unique_values = df_manager.get_unique_values(column_name)
        return render_template('values.html', column_name=column_name, values=unique_values)


@app.route('/change_value/<column_name>/<old_value>/<new_value>')
def change_value(column_name, old_value, new_value):
    df_manager = get_df_manager()
    df_manager.get_data()
    df_manager.change_value(column_name=column_name, old_value=old_value, new_value=new_value)
    df_manager.save_db()
    return redirect(url_for('values', column_name=column_name))


@app.route('/merge_column/<main_column>/', methods=['POST'])
def merge_column(main_column):
    if request.method == 'POST':
        df_manager = get_df_manager()
        df_manager.get_data()
        second_column = request.form['second_column']
        df_manager.merge_columns(main_column=main_column, second_column=second_column)
        df_manager.save_db()
        return redirect(url_for('columns'))


@app.route('/download/')
def download():
    df_manager = get_df_manager()
    df_manager.get_data()
    df_manager.save_to_csv()
    return send_file(df_manager.filename)


@app.route('/change_dimensional/<column_name>')
def change_dimensional(column_name):
    df_manager = get_df_manager()
    df_manager.get_data()
    unique_values = df_manager.get_unique_values(column_name)
    for value in unique_values:
        if value['title']:
            if 'мм' in value.get('title'):
                new_value = str(int(value['title'].split(' ')[0]) / 10)
                df_manager.change_value(column_name=column_name, old_value=value['title'], new_value=new_value)
    df_manager.save_db()
    return redirect(url_for('columns'))


@app.route('/value_capitalize/<column_name>')
def value_capitalize(column_name):
    df_manager = get_df_manager()
    df_manager.get_data()
    unique_values = df_manager.get_unique_values(column_name)
    for value in unique_values:
        if value['title']:
            if not value['title'][0].isupper():
                df_manager.change_value(column_name=column_name, old_value=value['title'],
                                        new_value=value['title'].capitalize())
    df_manager.save_db()
    return redirect(url_for('columns'))


@app.route('/complete/')
def complete():
    if os.path.exists(f'{DATABASE}.db'):
        os.remove(f'{DATABASE}.db')
    csv_files = glob.glob('*.csv')
    for csv_file in csv_files:
        os.remove(csv_file)
    return redirect(url_for('uploaded_files'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
