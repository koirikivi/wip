import argparse
import sys
import os
from pathlib import Path
import subprocess


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
    elif args.command == 'remove':
        subprocess.check_call([
            pip_executable,
            'uninstall',
            args.package,
        ])


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
    sys.exit(main())

