from setuptools import setup, find_packages


setup(
    name='pengbot',
    version='0.1',
    author='Mario César Señoranis Ayala',
    author_email='mariocesar.c50@gmail.com',
    packages=find_packages(''),
    entry_points={
        'console_scripts': ['pengbot = pengbot.main:main']
    },
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Development Status :: 4 - Beta'
    ]
)
