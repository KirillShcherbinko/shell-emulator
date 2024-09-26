from json import dump
from socket import gethostname


class Terminal(object):

    cur_dir = ""
    processing = True

    def __init__(self, username, vfs_file, logfile_path, start_script_path):
        self.username = username
        self.vfsFile = vfs_file
        self.logfilePath = logfile_path
        self.start_script_path = start_script_path

    def start_work_process(self):
        while self.processing:
            message = input(f'{self.username}@{gethostname()}:~{self.cur_dir}$ ')
            message_data = message.split()
            self.command_selector(message_data)

    def command_selector(self, message_data):
        if message_data[0] == "ls":
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
        print()

    def whoami(self, message_data):
        if len(message_data) > 0:
            print(f'whoami: лишний операнд {message_data[0]}')
        else:
            print(self.username)

    def mv(self, message_data):
        print()