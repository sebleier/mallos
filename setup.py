from setuptools import setup
import os

try:
    long_desc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
except (IOError, OSError):
    long_desc = ''

setup(
    name = "mallos",
    version = '0.1',
    url = 'http://github.com/sebleier/mallos',
    author = 'Sean Bleier',
    author_email = 'sebleier@gmail.com',
    description = 'Mallos is a small multiprocess spider',
    long_description = long_desc,
    install_requires = ['httplib2', 'lxml', 'logbook'],
    py_modules = ['mallos'],
)
