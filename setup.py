import os
from setuptools import setup, find_packages


def read(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='flyingrat',
    version='0.2.1',
    description='Simple mail server for local development',
    long_description=read('README.rst'),
    url='https://github.com/dmth/flyingrat/',
    author='Kevin Wetzels, Dustin Demuth',
    author_email='kevin@roam.be, dustin.demuth@intevation.de',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points='''
        [console_scripts]
        flyingrat=flyingrat.cli:main
    ''',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)
