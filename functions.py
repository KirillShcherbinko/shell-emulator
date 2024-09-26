from os.path import exists


def username_correctness(username):
    if len(username) > 32:
        print("Длина имени превышает допустимое значение")
        return False
    if not ('a' <= username[0] <= 'z' or username[0] == '_'):
        print(f'Имя не может начинаться с {username[0]}')
        return False
    for i in range(1, len(username)):
        if not('a' <= username[i] <= 'z' or '0' <= username[i] <= '9' or username[i] == '_'
                or username[i] == '-' or (username[i] == '$' and i == len(username) - 1)):
            print(f'Имя не может содержать символ {username[i]}')
            return False
    return True


def get_extension(file_path):
    extension = ""
    for i in range(-1, -len(file_path), -1):
        if file_path[i] != '.':
            extension += file_path[i]
        else:
            break
    return extension[::-1]


def file_path_existence(file_path):
    if not exists(file_path):
        print(f'Файла по пути {file_path} не существует')
        return False
    return True


def file_path_extension(file_path, required_extension):
    real_extension = get_extension(file_path)
    if required_extension != real_extension:
        print(f'Данный файл имеет разрешение {real_extension}, а должен иметь - {required_extension}')
        return False
    return True


def file_path_correctness(file_path,  required_extension):
    if not file_path_existence(file_path):
        return False
    if not file_path_extension(file_path, required_extension):
        return False
    return True