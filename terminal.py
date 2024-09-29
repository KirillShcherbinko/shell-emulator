from os import path
from os import remove
from json import dump
from zipfile import ZipFile
from socket import gethostname
from time import time
from functions import get_extension
from shutil import move


class Terminal(object):

    cur_dir = ""
    processing = True
    vfsFiles = []
    old_file_path = ""
    new_file_path = ""

    def __init__(self, username, vfs_path, logfile_path, start_script_path):
        self.username = username
        self.vfsPath = vfs_path
        self.logfilePath = logfile_path
        self.start_script_path = start_script_path
        self.get_files_list(vfs_path)

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

    def replace_basename(self, file_path, old, new):
        return file_path[::-1].replace(old[::-1], new[::-1], 1)[::-1]

    def get_previous_dir(self, file_path_parts, cur_dir):
        if cur_dir == "" or not ".." in file_path_parts:
            return cur_dir
        file_basename = path.basename(cur_dir)
        cur_dir = self.replace_basename(cur_dir, file_basename, "").rstrip('/')
        return self.get_previous_dir(file_path_parts[1:], cur_dir)

    def get_full_path(self, file_path):
        if file_path == "~":
            return ""
        if file_path == ".":
            return self.cur_dir
        if ".." in file_path:
            file_path_parts = file_path.rstrip('/').split('/')
            real_file_path_parts = file_path.rstrip('/').split('.')
            return (self.get_previous_dir(file_path_parts, self.cur_dir) + '/' + real_file_path_parts[-1]).rstrip('/')
        if file_path[:2] == "~/" or self.cur_dir == "":
            return file_path.lstrip("~/")
        return self.cur_dir + '/' + file_path

    def rename_check(self, old_file_name, new_file_name):
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
            print("Файл не найден")
            return False
        if self.new_file_path not in self.vfsFiles and self.new_file_path != "":
            if self.rename_check(old_file_name, new_file_name):
                real_new_file_path = self.replace_basename(self.new_file_path, new_file_name, '').rstrip('/')
                if real_new_file_path not in self.vfsFiles and new_file_name != self.new_file_path:
                    print("Файл не найден")
                    return False
                return True
            print(f'Недопустимое имя файла {self.new_file_path}')
            return False
        self.new_file_path = (self.new_file_path + '/' +  old_file_name).strip('/')
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

    def start_work_process(self):
        while self.processing:
            message = input(f'{self.username}@{gethostname()}:~{self.cur_dir}$ ')
            message_data = message.split()
            self.command_selector(message_data)

    def command_selector(self, message_data):
        if len(message_data) == 0:
            return
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

    def ls(self, message_data):
        try:
            if len(message_data) > 1:
                print("Введено слишком много аргументов")
                return
            if len(message_data) == 0:
                message_data.append('.')
            dir_name = self.get_full_path(message_data[0])
            for file in self.vfsFiles:
                file_basename = path.basename(file)
                if dir_name == self.replace_basename(file, file_basename, "").rstrip('/'):
                    print(file_basename, end = '    ')
            print()
        except:
            print("Не удалось выполнить команду")

    def cd(self, message_data):
        try:
            if len(message_data) == 0:
                self.cur_dir = ""
                return
            elif len(message_data) > 1:
                print("Слишком много аргументов для функции cd")
                return
            new_dir = self.get_full_path(message_data[0].rstrip('/'))
            if new_dir in self.vfsFiles and get_extension(new_dir) == new_dir:
                self.cur_dir = new_dir
                return
            if new_dir == "":
                return
            print("Не удалось найти директорию с таким именем")
        except:
            print("Не удалось выполнить команду")


    def exit(self):
        print('exit')
        self.processing = False

    def pwd(self):
        print(("/home/" + self.username + '/' + self.cur_dir).rstrip('/'))

    def whoami(self, message_data):
        if len(message_data) > 0:
            print(f'whoami: лишний операнд {message_data[0]}')
        else:
            print(self.username)

    def mv(self, message_data):
        try:
            if len(message_data) > 2:
                print("Введено слишком много аргументов")
                return
            if len(message_data) < 2:
                print("Введено не достаточно аргументов")
                return
            self.old_file_path = self.get_full_path(message_data[0].rstrip('/'))
            self.new_file_path = self.get_full_path(message_data[1].rstrip('/'))
            if self.move_ability():
                self.move_file()
                self.get_files_list(self.vfsPath)
            self.old_file_path = ""
            self.new_file_path = ""
        except:
            print("Не удалось выполнить команду")
