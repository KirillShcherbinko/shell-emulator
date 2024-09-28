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

    def __init__(self, username, vfs_path, logfile_path, start_script_path):
        self.username = username
        self.vfsPath = vfs_path
        self.logfilePath = logfile_path
        self.start_script_path = start_script_path
        with ZipFile(vfs_path, 'r') as vfs_file:
            self.vfsFiles = vfs_file.namelist()
        vfs_file.close()
        for i in range(len(self.vfsFiles)):
            top_file = self.vfsFiles[i].split('/')[0]
            if top_file not in self.vfsFiles:
                self.vfsFiles.append(top_file)
            self.vfsFiles[i] = self.vfsFiles[i].rstrip('/')


    def get_file_name(self, file_path):
        file_name = file_path.split('/')
        for dir in reversed(file_name):
            if dir != '':
                return dir

    def get_full_path(self, file_path):
        if self.cur_dir in file_path:
            return file_path
        return self.cur_dir + file_path

    def rename_check(self, old_file_name, new_file_name):
        old_file_extension = get_extension(old_file_name)
        new_file_extension = get_extension(new_file_name)
        if old_file_extension == old_file_name and new_file_extension == new_file_name:
            return True
        elif old_file_extension == new_file_extension and old_file_name != new_file_name:
            return True
        return False

    def move_ability(self, old_file_path, new_file_path):
        if old_file_path not in self.vfsFiles:
            print(f'Файла {old_file_path} не существует')
            return False
        if new_file_path not in self.vfsFiles:
            old_file_name = path.basename(old_file_path)
            new_file_name = path.basename(new_file_path)
            if self.rename_check(old_file_name, new_file_name):
                if get_extension(new_file_path) == new_file_path:
                    real_new_file_path = new_file_path.replace('/' + new_file_name, '')
                if real_new_file_path not in self.vfsFiles:
                    print(f'Директории {new_file_path} не существует')
                    return False
                return True
        else:
            return True

    def move_file(self, old_file_path, new_file_path):
        tmp_vfs_path = path.join(path.dirname(self.vfsPath), f'{int(time())}_{path.basename(self.vfsPath)}')
        with ZipFile(tmp_vfs_path, 'w') as tmp_vfs_file:
            with ZipFile(self.vfsPath, 'r') as vfs_file:
                for file in vfs_file.namelist():
                    if file == old_file_path or file.startswith(old_file_path + '/'):
                        new_file = file.replace(old_file_path, new_file_path, 1)
                        tmp_vfs_file.writestr(new_file, vfs_file.read(file))
                    else:
                        tmp_vfs_file.writestr(file, vfs_file.read(file))
        remove(self.vfsPath)
        move(tmp_vfs_path, self.vfsPath)

    def start_work_process(self):
        while self.processing:
            message = input(f'{self.username}@{gethostname()}:~{self.cur_dir}$ ')
            message_data = message.split()
            self.command_selector(message_data)

    def command_selector(self, message_data):
        if len(message_data) == 0:
            print()
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
            self.pwd(message_data[1:])
        else:
            print("Введена неверная команда")

    def ls(self, message_data):
        try:
            print()
        except:
            print()

    def cd(self, message_data):
        print()

    def exit(self):
        print('exit')
        self.processing = False

    def pwd(self, message_data):
        print(self.cur_dir)

    def whoami(self, message_data):
        if len(message_data) > 0:
            print(f'whoami: лишний операнд {message_data[0]}')
        else:
            print(self.username)

    def mv(self, message_data):
        try:
            if len(message_data) < 2:
                print("Введено не достаточно аргументов")
                return
            old_file_path = self.get_full_path(message_data[0])
            new_file_path = self.get_full_path(message_data[1])
            if self.move_ability(old_file_path, new_file_path):
                self.move_file(old_file_path, new_file_path)
        except:
            print("Не удалось выполнить команду")