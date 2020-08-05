from os import path

# a comment here

from setuptools import setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='wip',
    version='0.0.0',
    url='https://github.com/koirikivi/wip',
    author='Rainer Koirikivi',
    author_email='rainer@koirikivi.fi',
    description='WIP is Pip-wrapper',
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['wip'],
    license='MIT',
    entry_points={
        'console_scripts': ['wip=wip:main']
    },
    install_requires=[
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-watch',
            'flake8',
            #'mocktail',
            'pip-tools',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Software Distribution',
    ],
)
