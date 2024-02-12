import pandas as pd
import sqlite3


class DFManager:
    """
    Класс для работы с csv-файлами с помощью pandas
    """

    def __init__(self, csv_file_tut, csv_file_ru):
        """
        Инициализатор класса
        :param csv_file_tut: Путь к csv файлу с сайта santehnika-tut
        :param csv_file_ru: Путь к csv файлу с сайта santehnika.ru
        """

        self.filename = f'merge_{csv_file_tut.split("_")[0]}.csv'
        self.db_name = csv_file_tut.split("_")[0]
        self.df_tut = pd.read_csv(csv_file_tut, delimiter=';')
        self.df_ru = pd.read_csv(csv_file_ru, delimiter=';')
        self.general_df = None

    def get_data(self):
        conn = sqlite3.connect(f'{self.db_name}.db')
        query = "SELECT * FROM products_pandas;"
        self.general_df = pd.read_sql_query(query, conn)
        conn.close()

    def save_db(self):
        conn = sqlite3.connect(f'{self.db_name}.db')
        self.general_df.to_sql('products_pandas', conn, if_exists='replace', index=False)
        conn.close()

    def merge_files(self):
        self.df_tut.drop_duplicates(subset=['Артикул'], keep='first', inplace=True)
        self.df_ru.drop_duplicates(subset=['Артикул'], keep='first', inplace=True)
        self.general_df = pd.merge(self.df_tut, self.df_ru, on='Артикул', how='outer', suffixes=('_tut', '_ru'))

    def get_all_columns(self):
        """
        Получает имена всех столбцов, имующихся в датафрейме
        :return: Список столбцов в датафрейме
        """

        all_columns = []
        for i, column in enumerate(self.general_df.columns, start=1):
            all_columns.append({"title": column, "number": i})
        return all_columns

    def get_unique_values(self, column_name):
        """
        Получает уникальные значения в указанном столбце
        :param column_name: Наименование столбца
        :return: список уникальных значений в столбце
        """

        unique_values = []
        for i, column in enumerate(self.general_df[column_name].unique(), start=1):
            unique_values.append({"title": column, "number": i})
        return unique_values

    def delete_column(self, column_name):
        """
        Удаляет столбец из датафрейма
        :param column_name: Имя столбца
        :return: None
        """

        self.general_df.drop(column_name, axis=1, inplace=True)

    def change_value(self, column_name, old_value, new_value):
        """
        Изменяет все значения в указанном столбце датафрейма
        :param column_name: Имя столбца
        :param old_value: Старое значение
        :param new_value: Новое значение
        :return: None
        """

        self.general_df[column_name].replace(old_value, new_value, inplace=True)

    def change_column_name(self, old_column_name, new_column_name):
        """
        Изменяет название столбца в датафрейме
        :param old_column_name: Старое имя столбца
        :param new_column_name: Новое имя столбца
        :return:
        """
        self.general_df.rename(columns={old_column_name: new_column_name}, inplace=True)

    def save_to_csv(self):
        """
        Сохраняет датафрейм с файл csv
        :return: None
        """

        self.general_df.to_csv(self.filename, index=False)

    def merge_columns(self, main_column, second_column):
        """
        Объединяет два столбца. После чего удаляет столбец-донор
        :param main_column: Основной столбец
        :param second_column: Столбец-донор
        :return: None
        """

        self.general_df[main_column] = self.general_df[main_column].fillna(self.general_df[second_column])
        self.general_df.drop(second_column, axis=1, inplace=True)
