from setuptools import setup

setup(
    name='aioCoAPthon',
    version='1.0',
    packages=['tests', 'client', 'layers', 'server', 'messages', 'protocol', 'resources', 'utilities'],
    url='https://github.com/Tanganelli/aioCoAPthon',
    license='MIT',
    author='Giacomo Tanganelli',
    author_email='giacomo.tanganelli@for.unipi.it',
    description='',
    scripts=['server.py', 'client.py', 'run_tests.py'],
    requires=['aiounittest', 'cachetools']
)
