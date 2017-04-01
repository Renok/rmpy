from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='rmpy',
    version='1.0',
    include_package_data=True,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    entry_points={
            'console_scripts':
                ['rmpy = rmpy.rmpy:main']
            }
)
