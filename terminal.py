from os import path
from os import remove
from json import dump
from zipfile import ZipFile
from socket import gethostname
from time import time
from datetime import datetime, timedelta
from functions import get_extension
from shutil import move


class Terminal(object):

    cur_dir = ""
    processing = True
    vfsFiles = []
    old_file_path = ""
    new_file_path = ""
    command_data = {
        "user": "",
        "command": "",
        "status": "",
        "time": ""
    }

    def __init__(self, username, vfs_path, logfile_path, start_script_path):
        self.username = username
        self.vfsPath = vfs_path
        self.logfilePath = logfile_path
        self.startScriptPath = start_script_path
        self.get_files_list(vfs_path)
        try:
            with open(self.logfilePath, 'w') as logfile:
                dump({}, logfile)
        except:
            print("Не удалось открыть файл")

    def record_data(self, command, status):
        self.command_data["user"] = str(self.username).strip()
        self.command_data["command"] = command.strip()
        self.command_data["status"] = status.strip()
        self.command_data["time"] = str(datetime.utcnow() + timedelta(hours=3)).strip()
        try:
            with open(self.logfilePath, 'a', encoding='utf-8') as logfile:
                logfile.write('\n')
                dump(self.command_data, logfile, ensure_ascii=False, indent=4)
        except:
            print("Не удалось открыть файл")

    def get_files_list(self, vfs_path):
        with ZipFile(vfs_path, 'r') as vfs_file:
            self.vfsFiles = vfs_file.namelist()
        vfs_file.close()
        for i in range(len(self.vfsFiles)):
            self.vfsFiles[i] = self.vfsFiles[i].rstrip('/')
            top_files = self.vfsFiles[i].split('/')
            top_file = ""
            for j in range(len(top_files)):
                top_file += top_files[j] + '/'
                if top_file.rstrip('/') not in self.vfsFiles:
                    self.vfsFiles.append(top_file.rstrip('/'))

    @staticmethod
    def replace_basename(file_path, old, new):
        return file_path[::-1].replace(old[::-1], new[::-1], 1)[::-1].rstrip('/')

    def get_previous_dir(self, file_path_parts, cur_dir):
        if cur_dir == "" or ".." not in file_path_parts:
            return cur_dir.rstrip('/')
        file_basename = path.basename(cur_dir)
        cur_dir = self.replace_basename(cur_dir, file_basename, "")
        return self.get_previous_dir(file_path_parts[1:], cur_dir)

    def get_full_path(self, file_path):
        if file_path == "~":
            return ""
        if file_path == ".":
            return self.cur_dir
        if ".." in file_path:
            file_path_parts = file_path.rstrip('/').split('/')
            real_file_path_parts = file_path.strip('/').split('.')
            if self.cur_dir != "" or self.cur_dir == self.old_file_path:
                return (self.get_previous_dir(file_path_parts, self.cur_dir) + '/'
                    + real_file_path_parts[-1].strip('/')).rstrip('/')
            if self.old_file_path == ".." and self.cur_dir == "":
                self.old_file_path = ""
            dir_basename = path.basename(self.old_file_path).rstrip('/')
            real_dir = self.replace_basename(self.old_file_path, dir_basename, "")
            return (self.get_previous_dir(file_path_parts, real_dir) + '/'
                    + real_file_path_parts[-1].strip('/')).rstrip('/')
        if file_path[:2] == "~/" or self.cur_dir == "":
            file_path = file_path.lstrip("~/")
            file_path = file_path.rstrip("/")
            return file_path
        return (self.cur_dir + '/' + file_path).rstrip('/')

    @staticmethod
    def rename_check(old_file_name, new_file_name):
        old_file_extension = get_extension(old_file_name)
        new_file_extension = get_extension(new_file_name)
        if old_file_extension == old_file_name and new_file_extension == new_file_name:
            return True
        elif old_file_extension == new_file_extension and old_file_name != new_file_name:
            return True
        return False

    def move_ability(self):
        old_file_name = path.basename(self.old_file_path)
        new_file_name = path.basename(self.new_file_path)
        if self.old_file_path not in self.vfsFiles:
            print("Файл, который нужно перенести, не найден")
            self.record_data(f'mv {self.old_file_path} {self.new_file_path}', "ERROR")
            return False
        if self.new_file_path not in self.vfsFiles and self.new_file_path != "":
            if self.rename_check(old_file_name, new_file_name):
                real_new_file_path = self.replace_basename(self.new_file_path, new_file_name, '')
                if real_new_file_path not in self.vfsFiles and new_file_name != self.new_file_path:
                    print("Директория для перемещения не найдена")
                    self.record_data(f'mv {self.old_file_path} {self.new_file_path}', "ERROR")
                    return False
                return True
            print(f'Недопустимое имя файла {new_file_name}')
            self.record_data(f'mv {self.old_file_path} {self.new_file_path}', "ERROR")
            return False
        self.new_file_path = (self.new_file_path + '/' + old_file_name).strip('/')
        return True

    def move_file(self):
        tmp_vfs_path = path.join(path.dirname(self.vfsPath), f'{int(time())}_{path.basename(self.vfsPath)}')
        with ZipFile(tmp_vfs_path, 'w') as tmp_vfs_file:
            with ZipFile(self.vfsPath, 'r') as vfs_file:
                for file in vfs_file.namelist():
                    if file == self.old_file_path or file.startswith(self.old_file_path + '/'):
                        new_file = file.replace(self.old_file_path, self.new_file_path, 1)
                        tmp_vfs_file.writestr(new_file, vfs_file.read(file))
                    else:
                        tmp_vfs_file.writestr(file, vfs_file.read(file))
            for empty_folder in self.vfsFiles:
                if (self.new_file_path in empty_folder
                        and get_extension(empty_folder) == empty_folder
                        and empty_folder + '/' not in vfs_file.namelist()
                        and empty_folder + '/' not in tmp_vfs_file.namelist()):
                    tmp_vfs_file.writestr(empty_folder + '/', '')
        remove(self.vfsPath)
        move(tmp_vfs_path, self.vfsPath)
        print("Файл успешно перемещён")

    def start_script_exec(self):
        with open(self.startScriptPath, 'r') as start_script_file:
            end_of_message = "\n"
            for message in start_script_file:
                print(f'{self.username}@{gethostname()}:~{self.cur_dir}$ {message.strip(end_of_message)}')
                message_data = message.split()
                self.command_selector(message_data)

    def start_work_process(self):
        while self.processing:
            message = input(f'{self.username}@{gethostname()}:~{self.cur_dir}$ ')
            message_data = message.split()
            self.command_selector(message_data)

    def command_selector(self, message_data):
        if len(message_data) == 0:
            self.record_data("", "OK")
        elif message_data[0] == "ls":
            self.ls(message_data[1:])
        elif message_data[0] == "cd":
            self.cd(message_data[1:])
        elif message_data[0] == "exit":
            self.exit()
        elif message_data[0] == "mv":
            self.mv(message_data[1:])
        elif message_data[0] == "whoami":
            self.whoami(message_data[1:])
        elif message_data[0] == "pwd":
            self.pwd()
        else:
            print("Введена неверная команда")
            self.record_data("".join(message_data), "ERROR")

    def ls(self, message_data):
        try:
            if len(message_data) > 1:
                print("Введено слишком много аргументов")
                self.record_data(f'ls {"".join(message_data)}', "ERROR")
                return
            if len(message_data) == 1 and get_extension(message_data[0]) != message_data[0]:
                print(f'Введено некорректное значение {message_data[0]}')
                self.record_data(f'ls {"".join(message_data)}', "ERROR")
                return
            if len(message_data) == 0:
                message_data.append('.')
            dir_name = self.get_full_path(message_data[0])
            if dir_name not in self.vfsFiles and dir_name != "":
                print(f'Директория {message_data[0]} не найдена')
                self.record_data(f'ls {"".join(message_data)}', "ERROR")
                return
            for file in self.vfsFiles:
                file_basename = path.basename(file)
                if dir_name == self.replace_basename(file, file_basename, ""):
                    print(file_basename, end='    ')
            print()
            self.record_data(f'ls {"".join(message_data)}', "OK")
        except:
            print("Не удалось выполнить команду")
            self.record_data(f'ls {"".join(message_data)}', "ERROR")

    def cd(self, message_data):
        try:
            if len(message_data) == 0:
                self.cur_dir = ""
                self.record_data("cd", "OK")
                return
            elif len(message_data) > 1:
                print("Слишком много аргументов для функции cd")
                self.record_data(f'cd {"".join(message_data)}', "ERROR")
                return
            new_dir = self.get_full_path(message_data[0].rstrip('/'))
            if new_dir in self.vfsFiles and get_extension(new_dir) == new_dir:
                self.cur_dir = new_dir
                self.record_data(f'cd {"".join(message_data)}', "OK")
                return
            if new_dir == "":
                self.record_data(f'cd {"".join(message_data)}', "OK")
                return
            print("Не удалось найти директорию с таким именем")
            self.record_data(f'cd {"".join(message_data)}', "ERROR")
        except:
            print("Не удалось выполнить команду")
            self.record_data(f'cd {"".join(message_data)}', "ERROR")

    def exit(self):
        print('exit')
        self.processing = False
        self.record_data("exit", "OK")

    def pwd(self):
        print(("/home/" + self.username + '/' + self.cur_dir).rstrip('/'))
        self.record_data("pwd", "OK")

    def whoami(self, message_data):
        if len(message_data) > 0:
            print(f'whoami: лишний операнд {message_data[0]}')
            self.record_data(f'whoami {"".join(message_data)}', "ERROR")
        else:
            print(self.username)
            self.record_data("whoami", "OK")

    def mv(self, message_data):
        try:
            if len(message_data) > 2:
                print("Введено слишком много аргументов")
                self.record_data(f'mv {"".join(message_data)}', "ERROR")
                return
            if len(message_data) < 2:
                print("Введено не достаточно аргументов")
                self.record_data(f'mv {"" if len(message_data) != 0 else "".join(message_data) }', "ERROR")
                return
            self.old_file_path = self.get_full_path(message_data[0].rstrip('/'))
            self.new_file_path = self.get_full_path(message_data[1].rstrip('/'))
            if self.old_file_path in self.new_file_path:
                print("Невозможно переместить каталог в собственный подкаталог")
                self.record_data(f'mv {"".join(message_data)}', "ERROR")
                return
            if self.move_ability():
                self.move_file()
                self.get_files_list(self.vfsPath)
            self.old_file_path = ""
            self.new_file_path = ""
            self.record_data(f'mv {"".join(message_data)}', "OK")
        except:
            print("Не удалось выполнить команду")
            self.record_data(f'mv {"".join(message_data)}', "ERROR")
