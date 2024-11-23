# Описание
Эмулятор для языка оболочки ОС, имитирующий сеанс shell в UNIX-подобной ОС. Эмулятор позволяет пользователю работать с виртуальной файловой системой при помощи интерфейса командной строки(CLI)

# Запуск
Запуск эмулятора происходит из командной строки путём ввода:
```
py [path]/main.py [username] [[path]/filesystem.zip] [[path]/logfile.json] [[path]/startscript.txt]
```
Где
* path - путь до файла main.py
* username - имя пользователя
* filesystem.zip - zip-архив, предназначенный для хранения файлов для эмуляции
* logfile.json - файл в формате json, содержащий сведения о пользователе, осуществившим команду, самой команде, успешности выполнения команды и дате выполнения
* startscript.txt - стартовый скрипт - тестовый файл, содержащий команды, которые выполнятся при запуске файла

  После ввода команд пользователю выведется сообщение об ошибке или предложится запустить выполнение команд из стартового скрипта

# Команды эмулятора

## ls

Выводит содержимое директории (directory). При отсутствии агрументов выводит содержимое текущей директории

```
ls [directory]
```

## cd

Осуществляет переход в новую директорию (new directory), при отсутствии аргументов перенаправляет пользователя в домашнюю директорию

```
cd [new directory]
```

## exit

Осуществляет выход из эмулятораю

```
exit
```

## pwd

Выводит полный путь от корневого каталога к текущему рабочему каталогу.

```
pwd
```
## whoami

Выводит имя пользователя.

```
whoami
```

## Функция mv

Осуществляет перемещение файла из данной директории (old file path) в другую (new file path) с возможностью переименования этого файла.

```
mv [old file path] [new file path]
```

# Тестирование
Для всех команд были написаны тесты. В ходе тестирования удалось добиться покрытия 83%.

## Запуск тестирования

Перед запуском нужно убедиться, что на устройстве есть библиотека pytest. При её отсутсвии выполните установку при помощи команды:

```
pip install pytest
```

Для запуска тестирования выполните следующую команду:

```
pytest -v
```

Для генерации отчёта о покрытии тестами выполните команду:

```
coverage run --branch -m pytest test_terminal.py
```

Посмотреть результаты покрытия можно при помощи команды:

```
coverage report
```

## Прохождение всех тестов и процент покрытия
![image](https://github.com/user-attachments/assets/279cdaec-b536-4db5-bb7a-32e52783cdef)

