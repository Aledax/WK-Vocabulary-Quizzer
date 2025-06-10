import os, csv, sys

def resource_path(path):
    return os.path.join(os.path.dirname(sys.argv[0]), "data", "resources", path)

def list_files(path):
    return [f for f in os.listdir(resource_path(path)) if os.path.isfile(os.path.join(resource_path(path), f))]

def load_file(path):
    try:
        f = open(resource_path(path), encoding='utf-8')
        return f
    except:
        return None

def load_file_lines(path):
    f = load_file(path)
    if f:
        return list(f.read().splitlines())
    return None

def load_file_grid(path):
    f = load_file(path)
    if f:
        return [[*s] for s in f.read().splitlines()]
    return None

def load_csv(path):
    f = load_file(path)
    if f:
        return [row for row in csv.reader(f)]
    return None

def new_file(path):
    return open(resource_path(path), 'a')

def write_text_file(path, text):
    new_file(path).write(text)

def new_directory(path):
    os.mkdir(resource_path(path))

def rename_file(src, dst):
    os.rename(resource_path(src), resource_path(dst))