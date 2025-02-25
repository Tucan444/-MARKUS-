import os

def make_module_string(file_path: str) -> str:
    return file_path.replace("/", ".")[:-3]


def module_string() -> str:
    hidden_imports_string = ""
    dirs_to_do: set[str] = set()

    for file in os.listdir():
        if "__" in file:
            continue

        if file[-3:] == ".py":
            hidden_imports_string += f" --hidden-import {make_module_string(file)}"
        elif "." in file or file == "_trash":
            continue
        else:
            dirs_to_do.add(file)

    to_clear: list[str] = []
    to_add: list[str] = []
    while dirs_to_do:
        to_clear += dirs_to_do

        for dir_ in dirs_to_do:
            for file in os.listdir(dir_):
                if "__" in file:
                    continue

                if file[-3:] == ".py":
                    hidden_imports_string += f" --hidden-import {make_module_string(f'{dir_}/{file}')}"
                elif "." in file:
                    continue
                else:
                    to_add.append(f"{dir_}/{file}")

        for item in to_clear:
            dirs_to_do.remove(item)

        for item in to_add:
            dirs_to_do.add(item)

        to_clear = []
        to_add = []

    return hidden_imports_string

if __name__ == '__main__':
    print(module_string())
    s = module_string()

    with open("compile_command.txt", "w") as f:
        f.write(f"pyinstaller --onefile --noconsole{s} game.py")