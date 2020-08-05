"""
"yarn add" like pip functionality -- install package and modify setup.py

TODO:
- make the whole thing use libcst, or at least parse the requirements list with ast.literal_eval...
  currently it's very hacky
- implement "wip remove"
- also update requirements.txt (maybe make it optional)
- detect if duplicate modules are being added
"""
import argparse
import sys
import os
from pathlib import Path
import subprocess
import ast


cwd = Path.cwd().resolve()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['add', 'remove'])
    parser.add_argument('package')
    args = parser.parse_args()

    venv = find_venv()
    setup_py = find_setuppy()

    pip_executable = str(venv / 'bin' / 'pip')

    if args.command == 'add':
        subprocess.check_call([
            pip_executable,
            'install',
            args.package,
        ])
        add_to_setuppy(setup_py, args.package)
    elif args.command == 'remove':
        sys.exit('Remove is not yet implemented!')
        subprocess.check_call([
            pip_executable,
            'uninstall',
            args.package,
        ])


def add_to_setuppy(setup_py, package):
    """add `package` to install_requires list in setup.py"""
    # TODO: this method is a mess. It does very naive string manipulation
    # We should rather use libcst

    print(f'Adding {package!r} to {setup_py}...')

    with open(setup_py) as f:
        contents = f.read()
    module = ast.parse(contents)
    setup_exprs = [
        x for x in module.body
        if (
            isinstance(x, ast.Expr)
            and isinstance(x.value, ast.Call)
            and x.value.func.id == 'setup'
        )
    ]
    if not setup_exprs:
        raise ValueError('setup() call not found')
    setup_call = setup_exprs[0].value
    try:
        install_requires_keyword = [kw for kw in setup_call.keywords if kw.arg == 'install_requires'][0]
    except IndexError:
        raise ValueError('install_requires keyword not found in setup() call')

    install_requires_list = install_requires_keyword.value
    if not isinstance(install_requires_list, ast.List):
        # TODO: add support for tuples and variables
        raise ValueError(f'install_requires value must be a list (got {type(install_requires_list)})')

    start_lineno = install_requires_list.lineno - 1
    end_lineno = install_requires_list.end_lineno - 1
    lines = contents.splitlines(keepends=True)

    start_line = lines[start_lineno]

    # detect line separator and indentation
    if start_line.endswith('\r\n'):
        linesep = '\r\n'
    else:
        linesep = '\n'
    # assume indentation with 4 spaces
    spaces_per_indent_level = 4
    num_spaces = 0
    for c in start_line:
        if c != ' ':
            break
        num_spaces += 1
    current_indent_size = (num_spaces // spaces_per_indent_level)
    current_indent = ' ' * current_indent_size * spaces_per_indent_level
    new_indent = ' ' * (current_indent_size + 1) * spaces_per_indent_level

    if start_lineno == end_lineno:
        # install_requires=['foo', 'bar']
        start_col_offset = install_requires_list.col_offset + 1
        end_col_offset = install_requires_list.end_col_offset
        head = start_line[:start_col_offset]
        middle = start_line[start_col_offset:end_col_offset - 1]
        tail = start_line[end_col_offset - 1:]
        if not middle.strip():
            # if the list is empty, start new line
            lines[start_lineno:start_lineno + 1] = [
                head + linesep,
                f'{new_indent}{package!r},{linesep}',
                f'{current_indent}{tail}',
            ]
        else:
            # else the user seems to actually want to have the packages on one line...
            # so make it so.
            middle = f'{middle}, {package!r}'
            lines[start_lineno] = head + middle + tail
    else:
        # install_requires=[
        #     'foo',
        #     'bar',
        # ]
        if (end_lineno - 1) != start_lineno and not lines[end_lineno - 1].rstrip().endswith(','):
            # last line doesn't end with comma
            lines[end_lineno - 1] = lines[end_lineno - 1].rstrip() + ',' + linesep
        lines.insert(
            end_lineno,
            f'{new_indent}{package!r},{linesep}'
        )

    contents = ''.join(lines)
    with open(setup_py, 'w') as f:
        f.write(contents)


def find_venv() -> Path:
    venv_dir = os.getenv('VIRTUAL_ENV')
    if venv_dir:
        return Path(venv_dir)

    path = cwd
    while True:
        venv_dir = path / 'venv'
        if venv_dir.exists() and venv_dir.is_dir():
            return venv_dir
        if path.parent == path:
            raise ValueError(f'did not find "venv" in {Path.cwd()} or parent directories')
        path = path.parent


def find_setuppy() -> Path:
    path = cwd
    while True:
        venv_dir = path / 'setup.py'
        if venv_dir.exists() and venv_dir.is_file():
            return venv_dir
        if path.parent == path:
            raise ValueError(f'did not find "setup.py" in {Path.cwd()} or parent directories')
        path = path.parent


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # noqa
        # sys.exit(1)
        sys.exit(str(e))
