import glob
from DFManager import DFManager

csv_file_tut = ''.join(glob.glob('*tut.csv'))
csv_file_ru = ''.join(glob.glob('*ru.csv'))
df_manager = DFManager(csv_file_tut, csv_file_ru)
df_manager.merge_files()
columns = df_manager.get_all_columns()
unique = df_manager.get_unique_values('Материал:')
print(type(unique))
for value in unique:
    print(value)
