import os

def get_files_from_directory(directory):
    """Lee los archivos del directorio especificado y devuelve un diccionario con sus contenidos."""
    resources = {}
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                resources[filename] = file.read()
    return resources

def write_files_in_directory(directory, resources):
    """Escribe los archivos en el directorio especificado."""
    for filename, content in resources.items():
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w') as file:
            file.write(content)