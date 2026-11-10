import shlex

import prompt

from primitive_db.core import DATABASE_FILE, create_table, drop_table, list_table
from primitive_db.utils import exit, help, load_metadata, save_metadata


def run():
    metadata = load_metadata(DATABASE_FILE)
    while True:
        prmpt = prompt.string(">>>Введите команду: ")
        args = shlex.split(prmpt)
        cmd = args.pop(0)
        match cmd:
            case "create_table":
                table_name = args.pop(0)
                try:
                    create_table(metadata, table_name, args)
                    save_metadata(DATABASE_FILE, metadata)
                    print(
                        f'Таблица "{table_name}" успешно '
                        f'создана со столбцами: {", ".join(args)}'
                    )
                except ValueError as e:
                    print(e)
            case "drop_table":
                try:
                    table_name = args.pop(0)
                    drop_table(metadata, table_name)
                    save_metadata(DATABASE_FILE, metadata)
                    print(f'Таблица "{table_name}" успешно удалена.')
                except ValueError as e:
                    print(e)
            case "list_tables":
                list_table(metadata)
            case "help":
                help()
            case "exit":
                exit()
            case _:
                print(f'Функции "{cmd}" нет. Попробуйте снова.')
