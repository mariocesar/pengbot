from setuptools import setup, find_packages


setup(
    name='pengbot',
    version='0.1',
    author='Mario César Señoranis Ayala',
    author_email='mariocesar.c50@gmail.com',
    packages=find_packages(''),
    entry_points={
        'console_scripts': ['pengbot = pengbot.main:main']
    }
)
