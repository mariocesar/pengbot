from setuptools import setup

setup(
    name='pengbot-example-bots',
    version='0.1',
    py_modules=['bob', 'vvbot'],
    include_package_data=True,
    install_requires=['pengbot', 'slacker'],
    entry_points='''
        [console_scripts]
        bob=bob:cli_handler
        vvbot=vvbot:cli_handler
    ''',
)
