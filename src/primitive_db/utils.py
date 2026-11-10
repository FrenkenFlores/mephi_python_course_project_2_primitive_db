import json
import os
import pydoc
import sys
from typing import Callable

TEMPLATE = """
***Общие команды***

Функции:
<command> exit - выход из программы
<command> help - справочная информация

***База данных***

Функции:
<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу

***Операции с данными***

Функции:
<command> insert into <имя_таблицы> values \
(<значение1>, <значение2>, ...) - создать запись.
<command> select from <имя_таблицы> where <столбец> = <значение> - \
прочитать записи по условию.
<command> select from <имя_таблицы> - прочитать все записи.
<command> update <имя_таблицы> set <столбец1> = <новое_значение1> \
where <столбец_условия> = <значение_условия> - обновить запись.
<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.
<command> info <имя_таблицы> - вывести информацию о таблице.

"""
DATA_DIR = "data"

def load_metadata(filepath: str) -> dict:
    """
    Takes filepath and loads metadata.

    Args:
        filepath (str): the path to the JSON file
    Returns:
        dict: metadata dictionary that was loaded from filepath
    Raises:
        ValueError: if an issue occurred while loading the metadata
    """
    if any(
        (
            not filepath,
            not isinstance(filepath, str),
            not filepath.endswith(".json"),
        )
    ):
        raise ValueError(
            "Ошибка: Путь должен представлять собой строку, "
            "которая указывает на JSON файл"
        )
    data = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data.update(
                json.load(f)
            )
    except FileNotFoundError as e:
        print(
            f'Ошибка: Файл "{filepath}" не найден. Исключение: "{e}". '
            f'Новый файл будт создан'
        )
    except (json.decoder.JSONDecodeError, TypeError) as e:
        print(
            f'Ошибка: У файла "{filepath} неправильный JSON формат или не представляет '
            f'собой словарь. Исключение: "{e}". Файл будет создан заново'
        )
    return data


def save_metadata(filepath: str, data: dict):
    """
    Takes filepath and saves metadata.

    Args:
        filepath (str): the path to the JSON file
        data (dict): a dictionary that will be saved into the JSON file
    Raises:
        ValueError: if an issue occurred while saving the metadata
        TypeError: if data is not a dict
    """
    if any(
        (
            not filepath,
            not isinstance(filepath, str),
            not filepath.endswith(".json"),
        )
    ):
        raise ValueError(
            "Ошибка: Путь должен представлять собой строку, "
            "которая указывает на JSON файл"
        )
    if not isinstance(data, dict):
        raise TypeError(
            f'Ошибка: Неподходящий тип "{type(data)}" у аргумента "data". '
            f'Тип должен быть dict'
        )
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def help():
    """
    Prints help message.
    """
    print(TEMPLATE)


def exit():
    """
    Exits the program.
    """
    sys.exit(0)


def load_table_data(table_name: str):
    """
    Loads table data from JSON file.

    Args:
        table_name (str): the table name
    Returns:
        dict: table data that was loaded from JSON file
    Raises:
        ValueError: if an issue occurred while loading the table
    """
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    data = {}
    if any(
        (
            not filepath,
            not isinstance(filepath, str),
            not filepath.endswith(".json"),
        )
    ):
        raise ValueError(
            "Ошибка: Путь должен представлять собой строку, "
            "которая указывает на JSON файл"
        )
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data.update(json.load(f))
    except FileNotFoundError as e:
        print(
            f'Ошибка: Файл "{filepath}" не найден. Исключение: "{e}". '
            f'Новый файл будт создан'
        )
    except (json.decoder.JSONDecodeError, TypeError) as e:
        print(
            f'Ошибка: У файла "{filepath} неправильный JSON формат или не представляет '
            f'собой словарь. Исключение: "{e}". Файл будет создан заново'
        )
    return data


def save_table_data(table_name, data):
    """
    Saves data into table JSON file.

    Args:
        table_name (str): the table name
        data (dict): table data
    Raises:
        ValueError: if an issue occurred while saving the table
        TypeError: if data is not a dict
    """
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    if any(
        (
            not filepath,
            not isinstance(filepath, str),
            not filepath.endswith(".json"),
        )
    ):
        raise ValueError(
            "Ошибка: Путь должен представлять собой строку, "
            "которая указывает на JSON файл"
        )
    if not isinstance(data, dict):
        raise TypeError(
            f'Ошибка: Неподходящий тип "{type(data)}" у аргумента "data". '
            f'Тип должен быть dict'
        )
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def str_to_class(metadata, table_name, column_name) -> Callable:
    """
    Converts string class name into class.

    Args:
        metadata (dict): a dictionary that holds the table schema
        table_name (str): the table name
        column_name (str): the column name
    Returns:
        Callable: a class that converts string class name into class
    """
    return pydoc.locate(metadata[table_name][column_name])
