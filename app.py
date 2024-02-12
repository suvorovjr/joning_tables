import glob
from DFManager import DFManager
from flask import Flask, render_template, request, url_for, redirect, g
from pathlib import Path
import os

UPLOAD_FOLDER = Path(__file__).parent
ALLOWED_EXTENSIONS = ['csv']

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
        g.df_manager = DFManager(csv_file_tut, csv_file_ru)
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
            df_manager = DFManager(csv_file_tut, csv_file_ru)
            df_manager.merge_files()
            df_manager.save_db()
            return redirect(url_for('columns'))
        else:
            return render_template('error.html')
    else:
        return render_template('upload.html')


@app.route('/columns/', methods=['GET', 'POST'])
def columns(column_name=None):
    if request.method == 'POST':
        new_column_name = request.form['new_column_name']
        print(new_column_name, column_name)
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


@app.route('/values/<column_name>', methods=['GET', 'POST'])
def values(column_name, old_value=None):
    df_manager = get_df_manager()
    df_manager.get_data()
    if request.method == 'POST':
        new_value = request.form['new_value']
        df_manager.change_value(column_name=column_name, old_value=old_value, new_value=new_value)
        df_manager.save_db()
        unique_values = df_manager.get_unique_values(column_name)
        return render_template('values.html', values=unique_values)
    elif request.method == 'GET':
        unique_values = df_manager.get_unique_values(column_name)
        return render_template('values.html', column_name=column_name, values=unique_values)


if __name__ == '__main__':
    app.run(debug=True)
