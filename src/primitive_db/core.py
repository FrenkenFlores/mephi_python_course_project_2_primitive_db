

DATABASE_FILE = "db_meta.json"


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
    return metadata


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
    return metadata


def list_table(metadata):
    for table in metadata:
        print(f"- {table}")

