import functools
import time

import prompt


def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
            FileNotFoundError,
            KeyError,
            ValueError
        ) as e:
            print(e)
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            action = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if action.lower() == 'y':
                return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        print(
            f'Функция {func.__name__} выполнилась '
            f'за {end_time - start_time:.3f} секунд'
        )
        return result
    return wrapper


def create_cacher():
    cache = {}
    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()
        return cache[key]
    return cache_result
