import os
import sqlite3
import clang.cindex


# Функция для извлечения сигнатур функций из C++ файла
def extract_function_signatures(file_path):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(file_path)
    signatures = []

    for node in translation_unit.cursor.get_children():
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            signature = {
                'name': node.spelling,
                'args': [arg.spelling for arg in node.get_arguments()],
                'return_type': node.result_type.spelling
            }
            signatures.append(signature)

    return signatures


# Функция для создания базы данных и таблицы
def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY,
            file_name TEXT,
            function_name TEXT,
            args TEXT,
            return_type TEXT
        )
    ''')
    conn.commit()
    return conn


# Основная функция для анализа C++ файлов
def analyze_cpp_files(directory, db_name):
    # Создание базы данных
    conn = create_database(db_name)
    cursor = conn.cursor()

    # Обход всех файлов в директории
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.cpp') or file.endswith('.h'):
                file_path = os.path.join(root, file)
                signatures = extract_function_signatures(file_path)
                for sig in signatures:
                    cursor.execute('''
                        INSERT INTO functions (file_name, function_name, args, return_type)
                        VALUES (?, ?, ?, ?)
                    ''', (file_path, sig['name'], str(sig['args']), sig['return_type']))

    conn.commit()
    conn.close()
    print(f"Analysis complete. Data saved to {db_name}.")


# Пример использования
if __name__ == "__main__":
    clang.cindex.Config.set_library_path('C:\\Users\\eprig\\Documents\\TCHMK\\lab4\\Lab4Reverse\\')
    DIRECTORY = "C:/Users/eprig/Documents/Projects for OSs/TCP/ServerTCP"  # Укажите путь к директории с C++ файлами
    DB_NAME = "functions.db"

    analyze_cpp_files(DIRECTORY, DB_NAME)
