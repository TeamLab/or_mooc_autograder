from setuptools import setup

setup(
    name = 'Gachon-Autograder-Client',
    version = '0.0.1',
    py_modules = ['gachon_autograder_client'],
    author = 'Teamlab@GachonUniversity',
    author_email = 'teamlab.gachon AT gmail DOT com',
    install_requires=["requests"],
    url =    'http://cs50.gachon.ac.kr/gachon_auto_grader',
    scripts=['bin/gachon_autograder_client'],
    description = 'This is a program to automatically grade a submitted code for Gachon CS50 Classes.',
)