from types import NoneType
from typing import Any, Callable

from prettytable import PrettyTable

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import (
    load_table_data,
    save_metadata,
    save_table_data,
    str_to_class,
)

DATABASE_FILE = "db_meta.json"
cache_result: Callable[[Any, Callable], Any] = create_cacher()


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """
    Create a table and save the scheme in the metadata dictionary inplace.

    Args:
        metadata (dict): the table schemas
        table_name (str): the table name
        columns (list): a pair of column name and column type name:type
    Returns:
        metadata (dict): the updated table schemas
    Raises:
    ValueError: if the table could not be created because
    it already exists or the args format is invalid
    """
    if table_name in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" уже существует.')
    if not columns:
        raise ValueError(
            'Необходимо задать столбцы. Попробуйте снова.'
        )
    for pair in columns:
        parts = pair.split(":")
        if len(parts) != 2 or parts[1] not in ["str", "int", "bool"]:
            raise ValueError(
                f'Некорректное значение: "{pair}". Попробуйте снова.'
            )
    if "ID:int" not in columns:
        columns.insert(0, "ID:int")
    metadata.update(
        {
            table_name: {
                pair.split(":")[0]: pair.split(":")[1] for pair in columns
            }
        }
    )
    save_metadata(DATABASE_FILE, metadata)
    print(
        f'Таблица "{table_name}" успешно '
        f'создана со столбцами: {", ".join(columns)}'
    )
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """
    Remove table schema from the metadata dictionary inplace.

    Args:
        metadata (dict): the table schemas
        table_name (str): the table name that will be dropped
    Returns:
        metadata (dict): the updated table schemas
    Raises:
        ValueError: if the table could not be dropped because it does not exist
    """
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')
    metadata.pop(table_name)
    save_metadata(DATABASE_FILE, metadata)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_table(metadata):
    """
    Print the list of all tables in database.

    Args:
        metadata (dict): the table schemas
    """
    for table in metadata:
        print(f"- {table}")


@log_time
@handle_db_errors
def insert(
    metadata: dict,
    table_name: str,
    values: list
):
    """
    Insert values into the table schemas.

    Args:
        metadata (dict): the table schemas
        table_name (str): the table name that will be inserted
        values (list): a pair of values to be inserted
    Raises:
        ValueError: invalid number of arguments
        TypeError: incorrect data type for values
    """
    if table_name not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_name}" не существует.')
    metadata_iter = iter(metadata[table_name])
    next(metadata_iter) # Skip the ID column
    typed_values = []
    for value, schema_value in zip(values, metadata_iter):
        schema_value_class = str_to_class(metadata, table_name, schema_value)
        try:
            if schema_value_class is bool:
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                else:
                    raise ValueError()
            typed_values.append(
                schema_value_class(value)
            )
        except ValueError:
            raise TypeError(
                f'Ошибка: неправильный тип данных '
                f'"{type(value)}" для "{schema_value}". '
                f'Ожидается "{metadata[table_name][schema_value]}"'
            )
    if len(typed_values) != len(values):
        raise ValueError(
            f'Ошибка: ожидается {len(values)} аргументов, получно {len(typed_values)}'
        )
    data = load_table_data(table_name)
    lst_index = max((int(i) for i in data.keys()), default=0)
    cur_index = lst_index + 1
    metadata_iter = iter(metadata[table_name])
    next(metadata_iter) # Skip the ID column
    data.update(
        {
            cur_index: {
                schema_value: value for schema_value, value in zip(
                    metadata_iter,
                    typed_values
                )
            }
        }
    )
    save_table_data(table_name, data)
    print(f'Запись с ID={cur_index} успешно добавлена в таблицу "{table_name}"')


@log_time
@handle_db_errors
def select(
    metadata: dict,
    table_data: str,
    where_clause: tuple | NoneType = None
):
    """
    Prints rows of the given table. If where_clauses is
    provided, then the values will be filtered.

    Args:
        metadata (dict): the table schemas
        table_data (str): the table name
        where_clause (tuple | NoneType): a tuple with column name
        and value that will be selected
    Raises:
        ValueError: invalid input data
    """
    if table_data not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_data}" не существует.')
    table = PrettyTable()
    table.field_names = list(metadata[table_data].keys())
    data = cache_result(table_data, lambda: load_table_data(table_data))
    if not data:
        return table
    flattened_data = []
    for idx, obj in data.items():
        o = {
            "ID": str_to_class(metadata, table_data, "ID")(idx),
        }
        for k, v in obj.items():
            o[k] = str_to_class(metadata, table_data, k)(v)
        flattened_data.append(o)
    if where_clause and isinstance(where_clause, tuple) and len(where_clause) == 2:
        filter_column, filter_value = where_clause
        schema_filter_value_class = str_to_class(metadata, table_data, filter_column)
        if schema_filter_value_class is bool:
            if filter_value.lower() == "true":
                filter_value = True
            elif filter_value.lower() == "false":
                filter_value = False
            else:
                raise ValueError(
                    f'Ошибка: Логический тип неправильно указан "{filter_value}"'
                )
        try:
            flattened_data = list(
                filter(
                    lambda x: x[filter_column] == str_to_class(
                        metadata,
                        table_data,
                        filter_column
                    )(filter_value),
                    flattened_data
                )
            )
        except KeyError:
            raise ValueError(
                f'Ошибка: Ключ "{filter_column}" недоступен для фильтрации. '
                f'Выберите один из: {", ".join(list(metadata[table_data].keys()))}'
            )
    for row in flattened_data:
        table.add_row(list(row.values()))
    print(table)


@handle_db_errors
def update(metadata, table_data, set_clause, where_clause):
    """
    Updates the given table value that is located by column and value.

    Args:
        metadata (dict): the table schemas
        table_data (str): the table name
        set_clause (tuple): a tuple with column name and its new value
        where_clause (tuple): a tuple with column name and value that will be selected
    Raises:
        ValueError: invalid input data
    """
    if table_data not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_data}" не существует.')
    data = load_table_data(table_data)
    col, val = set_clause
    filter_col, filter_val = where_clause
    schema_value_class = str_to_class(metadata, table_data, col)
    if schema_value_class is bool:
        if val.lower() == "true":
            val = True
        elif val.lower() == "false":
            val = False
        else:
            raise ValueError(f'Ошибка: Логический тип неправильно указан "{val}"')
    schema_filter_value_class = str_to_class(metadata, table_data, filter_col)
    if schema_filter_value_class is bool:
        if filter_val.lower() == "true":
            filter_val = True
        elif filter_val.lower() == "false":
            filter_val = False
        else:
            raise ValueError(
                f'Ошибка: Логический тип неправильно указан "{filter_val}"'
            )
    if filter_col == "ID":
        data[filter_val][col] = schema_value_class(val)
        print(f'Запись с ID={filter_val} в таблице "{table_data}" успешно обновлена')
    else:
        for idx, o in data.items():
            try:
                if o[filter_col] == schema_filter_value_class(filter_val):
                    data[idx][col] = schema_value_class(val)
                    print(
                        f'Запись с ID={idx} в таблице "{table_data}" успешно обновлена'
                    )
            except KeyError:
                raise ValueError(
                    f'Ошибка: Ключ "{filter_col}" недоступен для фильтрации. '
                    f'Выберите один из: {", ".join(list(metadata[table_data].keys()))}'
                )
    save_table_data(table_data, data)


@handle_db_errors
@confirm_action("удаление записи")
def delete(metadata, table_data, where_clause):
    """
    Deletes the row selected by the given expression.

    Args:
        metadata (dict): the table schemas
        table_data (str): the table name
        where_clause (tuple): a tuple with column name and value that will be deleted
    Raises:
        ValueError: invalid input data
    """
    if table_data not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_data}" не существует.')
    data = load_table_data(table_data)
    filter_col, filter_val = where_clause
    schema_filter_value_class = str_to_class(metadata, table_data, filter_col)
    if schema_filter_value_class is bool:
        if filter_val.lower() == "true":
            filter_val = True
        elif filter_val.lower() == "false":
            filter_val = False
        else:
            raise ValueError(
                f'Ошибка: Логический тип неправильно указан "{filter_val}"'
            )
    if filter_col == "ID":
        del data[filter_val]
        print(f'Запись с ID={filter_val} успешно удалена из таблицы "{table_data}"')
    else:
        for idx, o in data.copy().items():
            try:
                if o[filter_col] == schema_filter_value_class(filter_val):
                    del data[idx]
                    print(
                        f'Запись с ID={idx} успешно удалена из таблицы "{table_data}"'
                    )
            except KeyError:
                raise ValueError(
                    f'Ошибка: Ключ "{filter_col}" недоступен для фильтрации. '
                    f'Выберите один из: {", ".join(list(metadata[table_data].keys()))}'
                )
    save_table_data(table_data, data)


@handle_db_errors
def info(metadata, table_data):
    """
    Prints table metadata.

    Args:
        metadata (dict): the table schemas
        table_data (str): the table name
    Raises:
        ValueError: invalid input data
    """
    if table_data not in metadata:
        raise ValueError(f'Ошибка: Таблица "{table_data}" не существует.')
    data = load_table_data(table_data)
    print(f'Таблица: {table_data}')
    print(f'Столбцы: {", ".join(f"{k}:{v}"for k, v in metadata[table_data].items())}')
    print(f'Количество записей: {len(data)}')
