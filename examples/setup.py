from setuptools import setup

setup(
    name='pengbot-example-bots',
    version='0.1',
    py_modules=['bob'],
    include_package_data=True,
    install_requires=['pengbot'],
    entry_points='''
        [console_scripts]
        bob=bob:main_handler
    ''',
)
