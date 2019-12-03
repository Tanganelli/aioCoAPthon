from setuptools import setup

setup(
    name='aioCoAPthon',
    version='1.0',
    packages=['aiocoapthon.tests', 'aiocoapthon.client', 'aiocoapthon.layers', 'aiocoapthon.server',
              'aiocoapthon.messages', 'aiocoapthon.protocol', 'aiocoapthon.resources', 'aiocoapthon.utilities'],
    url='https://github.com/Tanganelli/aioCoAPthon',
    license='MIT',
    author='Giacomo Tanganelli',
    author_email='giacomo.tanganelli@for.unipi.it',
    description='',
    scripts=['server.py', 'client.py', 'run_tests.py'],
    requires=['aiounittest', 'cachetools']
)
