import prompt

TEMPLATE = """
Первая попытка запустить проект!

***
<command> exit - выйти из программы
<command> help - справочная информация
Введите команду: 
"""

def welcome():
    prompt.string(TEMPLATE)
