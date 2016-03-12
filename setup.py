from setuptools import setup
import sys

if sys.platform == "win32":
    # python setup.py py2exe
    import py2exe
    platform_options = {
        "windows": [{
            "script": "gachon_autograder_client.py",
            "dest_base": "gachon_autograder_client"
        }],
        "zipfile": None,
        "setup_requires": ["py2exe"],
        "options": {
            "py2exe": {
                "compressed": True
            }
        }
    }
elif sys.platform == "darwin":
    # python setup.py py2app
    platform_options = {
        "setup_requires": ["py2app"],
        "app": ["gachon_autograder_client.py"],
        "options": {
            "py2app": {
                "argv_emulation": True,
            }
        }
    }
else:
    # python setup.py install
    platform_options = {
        "scripts": ["gachon_autograder_client.py"]
    }

setup(
    name = 'Gachon-Autograder-Client',
    version = '0.0.2',
    py_modules = ['gachon_autograder_client'],
    author = 'Teamlab@GachonUniversity',
    author_email = 'teamlab.gachon AT gmail DOT com',
    install_requires=["requests"],
    url =    'http://cs50.gachon.ac.kr/gachon_auto_grader',
    description = 'This is a program to automatically grade a submitted code for Gachon CS50 Classes.',
    **platform_options
)