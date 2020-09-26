from ez_setup import use_setuptools

use_setuptools()
from setuptools import setup, find_packages

setup(name='TracSelectAdmin',
      version='0.1.0',
      packages=find_packages(exclude=''),
      package_data={'TracSelectAdmin': ['templates/*.html']},
      author='Jimmy Theis, Jan Rodeheger',
      author_email='j.rodeheger@semantics.de',
      description='Modify custom select fields for tickets in an admin panel within Trac. Now with extra bugs!',
      long_description=open('README.md').read() + '\n' + open('CHANGES').read(),
      url='http://github.com/jrod-97/TracSelectAdmin',
      license='GPLv3',
      entry_points={'trac.plugins': ['TracSelectAdmin = TracSelectAdmin.admin']},
      )
