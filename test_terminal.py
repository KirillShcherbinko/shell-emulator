import pytest
from terminal import Terminal


@pytest.fixture
def terminal():
    username = "kirill"
    vfs_path = "filesystem.zip"
    logfile_path = "logfile.json"
    start_script_path = "startscript.txt"
    return Terminal(username, vfs_path, logfile_path, start_script_path)


def test_init1(terminal):
    assert terminal.username is not None
    assert terminal.vfsPath is not None
    assert terminal.logfilePath is not None
    assert terminal.startScriptPath is not None


def test_get_files_list(terminal):
    terminal.get_files_list("filesystem.zip")
    assert terminal.vfsFiles == ['root/bin', 'root/home', 'root/home/user', 'root/home/user/drinks.txt', 'root/home/user/food.txt',
     'root/home/user/textfiles', 'root/home/user/textfiles/text1.txt', 'root/home/user/textfiles/text2.txt',
     'root/home/user/textfiles/text3.txt', 'root/lib', 'root/lib/other', 'root/lib/other/otherdir', 'root']


def test_replace_basename1(terminal):
    assert terminal.replace_basename("root/home", "home", "") == "root"


def test_get_full_path1(terminal):
    assert terminal.get_full_path('~') == ""


def test_get_full_path2(terminal):
    assert terminal.get_full_path('.') == terminal.cur_dir

def test_get_full_path3(terminal):
    terminal.cur_dir = ""
    assert terminal.get_full_path('../../') == ""


def test_get_full_path4(terminal):
    terminal.cur_dir = "root/home/user"
    assert terminal.get_full_path('../..') == "root"


def test_get_full_path5(terminal):
    terminal.cur_dir = "root/home"
    assert terminal.get_full_path('../bin/') == "root/bin"


def test_get_full_path6(terminal):
    terminal.cur_dir = ""
    assert terminal.get_full_path("root/home/") == "root/home"


def test_get_full_path7(terminal):
    terminal.cur_dir = "root"
    assert terminal.get_full_path("~/root/home") == "root/home"


def test_get_full_path8(terminal):
    terminal.cur_dir = "root"
    assert terminal.get_full_path("home") == "root/home"


def test_command_selector(terminal, capfd):
    terminal.command_selector(["fd"])
    out, err = capfd.readouterr()
    assert out == "Введена неверная команда\n"


def test_ls1(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.ls([])
    out, err = capfd.readouterr()
    assert out == "bin    home    lib    \n"


def test_ls2(terminal, capfd):
    terminal.cur_dir = ""
    terminal.ls(["root", "sdf"])
    out, err = capfd.readouterr()
    assert out == "Введено слишком много аргументов\n"


def test_cd1(terminal, capfd):
    terminal.cur_dir = ""
    terminal.cd(["root", "sdf"])
    out, err = capfd.readouterr()
    assert out == "Слишком много аргументов для функции cd\n"


def test_cd2(terminal, capfd):
    terminal.cur_dir = ""
    terminal.cd(["roots"])
    out, err = capfd.readouterr()
    assert out == "Не удалось найти директорию с таким именем\n"


def test_exit1(terminal, capfd):
    terminal.exit()
    out, err = capfd.readouterr()
    assert out == "exit\n"


def test_pwd1(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.pwd()
    out, err = capfd.readouterr()
    assert out == "/home/kirill/root\n"


def test_whoami1(terminal, capfd):
    terminal.whoami([])
    out, err = capfd.readouterr()
    assert out == "kirill\n"


def test_whoami2(terminal, capfd):
    terminal.whoami(["kirill"])
    out, err = capfd.readouterr()
    assert out == "whoami: лишний операнд kirill\n"

def test_mv1(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.mv([])
    out, err = capfd.readouterr()
    assert out == "Введено не достаточно аргументов\n"


def test_mv2(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.mv(["root", "re", "ro"])
    out, err = capfd.readouterr()
    assert out == "Введено слишком много аргументов\n"


def test_mv3(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.mv(["home", "home"])
    out, err = capfd.readouterr()
    assert out == "Невозможно переместить файл в собственный каталог\n"


def test_mv4(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.mv(["bins", "home"])
    out, err = capfd.readouterr()
    assert out == "Файл, который нужно перенести, не найден\n"


def test_mv5(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.mv(["bin", "homes/home"])
    out, err = capfd.readouterr()
    assert out == "Директория для перемещения не найдена\n"


def test_mv6(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.mv(["bin", "drinks.txt"])
    out, err = capfd.readouterr()
    assert out == "Недопустимое имя файла drinks.txt\n"


def test_mv7(terminal, capfd):
    terminal.cur_dir = "root"
    terminal.mv(["bin", "~"])
    out, err = capfd.readouterr()
    assert out == "Файл успешно перемещён\n"


def test_mv8(terminal, capfd):
    terminal.cur_dir = ""
    terminal.mv(["bin", "root"])
    out, err = capfd.readouterr()
    assert out == "Файл успешно перемещён\n"