import json
import sys

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

"""


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
            not isinstance(filepath, str),
            not filepath,
            not filepath.endswith(".json"),
        )
    ):
        raise ValueError("The filepath should be a string that refers to a json file")
    data = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data.update(
                json.load(f)
            )
        if not isinstance(data, dict):
            raise ValueError("The JSON file should contain a dict")
    except FileNotFoundError as e:
        print(f"File {filepath} not found: {e}. File will be created")
    except json.decoder.JSONDecodeError as e:
        print(f"File {filepath} could not be decoded: {e}. File will be recreated")
    return data


def save_metadata(filepath: str, data: dict):
    """
    Takes filepath and saves metadata.

    Args:
        filepath (str): the path to the JSON file
        data (dict): a dictionary that will be saved into the JSON file
    Raises:
        ValueError: if an issue occurred while saving the metadata
    """
    if any(
        (
            not isinstance(filepath, str),
            not filepath,
            not filepath.endswith(".json"),
        )
    ):
        raise ValueError("The filepath should be a string that refers to a json file")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError as e:
        print(f"File {filepath} not found: {e}")


def help():
    print(TEMPLATE)

def exit():
    sys.exit(0)

