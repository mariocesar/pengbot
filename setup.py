from setuptools import setup

with open('README.rst', 'r') as f:
    readme = f.read()

packages = [
    'pengbot',
    'pengbot.adapters',
]

setup(
    name='pengbot',
    description='A Bot framework to build bots with human manners',
    long_description=readme,
    version='0.1a1',
    author='Mario César Señoranis Ayala',
    author_email='mariocesar.c50@gmail.com',
    url='https://github.com/mariocesar/pengbot',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'requests': 'requests'},
    entry_points={
        'console_scripts': ['pengbot = pengbot.main:main']
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Development Status :: 2 - Pre-Alpha',
    ]
)
