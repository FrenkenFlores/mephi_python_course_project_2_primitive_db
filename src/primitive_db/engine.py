import re

import prompt

from primitive_db.core import (
    DATABASE_FILE,
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_table,
    select,
    update,
)
from primitive_db.utils import exit, help, load_metadata

RE_CREATE_TABLE = re.compile(
    r"^create_table (?P<table_name>\w+) (?P<columns>.+)$",
    re.IGNORECASE
)
RE_LIST_TABLES = re.compile(
    r"^list_tables$",
    re.IGNORECASE
)
RE_DROP_TABLE = re.compile(
    r"^drop_table (?P<table_name>\w+)$",
    re.IGNORECASE
)
RE_INSERT = re.compile(
    r"^insert into (?P<table_name>\w+) values \((?P<values>.+)\)$",
    re.IGNORECASE
)
RE_SELECT_WHERE = re.compile(
    r"^select from (?P<table_name>\w+) where (?P<column>\w+)\s*=\s*(?P<value>.+)$",
    re.IGNORECASE
)
RE_SELECT_ALL = re.compile(
    r"^select from (?P<table_name>\w+)$",
    re.IGNORECASE
)
RE_UPDATE = re.compile(
    (
        r"^update (?P<table_name>\w+) set (?P<column>\w+)\s*=\s*(?P<new_value>[^ ]+) "
        r"where (?P<where_col>\w+)\s*=\s*(?P<where_val>.+)$"
    ),
    re.IGNORECASE
)
RE_DELETE = re.compile(
    r"^delete from (?P<table_name>\w+) where (?P<column>\w+)\s*=\s*(?P<value>.+)$",
    re.IGNORECASE
)
RE_INFO = re.compile(
    r"^info (?P<table_name>\w+)$",
    re.IGNORECASE
)


def run():
    metadata = load_metadata(DATABASE_FILE)
    while True:
        command = prompt.string(">>>Введите команду: ")
        match command:
            case "help":
                help()
            case "exit":
                exit()
            case _ if m := RE_CREATE_TABLE.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                args = data['columns'].split()
                try:
                    create_table(metadata, table_name, args)

                except ValueError as e:
                    print(e)
            case _ if m := RE_DROP_TABLE.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                try:
                    drop_table(metadata, table_name)
                except ValueError as e:
                    print(e)
            case _ if m := RE_LIST_TABLES.match(command):
                list_table(metadata)
            case _ if m := RE_INSERT.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                args = [datom.strip('"\'') for datom in data['values'].split(", ")]
                try:
                    insert(metadata, table_name, args)
                except (TypeError, ValueError) as e:
                    print(e)
            case _ if m := RE_SELECT_WHERE.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                column = data['column']
                value = data['value']
                try:
                    select(metadata, table_name, where_clause=(column, value))
                except ValueError as e:
                    print(e)
            case _ if m := RE_SELECT_ALL.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                try:
                    select(metadata, table_name)
                except ValueError as e:
                    print(e)
            case _ if m := RE_UPDATE.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                column = data['column']
                new_value = data['new_value']
                where_col = data['where_col']
                where_val = data['where_val']
                try:
                    update(
                        metadata,
                        table_name,
                        set_clause=(column, new_value),
                        where_clause=(where_col, where_val)
                    )
                except ValueError as e:
                    print(e)
            case _ if m := RE_DELETE.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                column = data['column']
                value = data['value']
                try:
                    delete(metadata, table_name, where_clause=(column, value))
                except ValueError as e:
                    print(e)
            case _ if m := RE_INFO.match(command):
                data = m.groupdict()
                table_name = data['table_name']
                info(metadata, table_name)
            case _:
                print(f'Функции "{command}" нет. Попробуйте снова.')
