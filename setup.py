from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

with open('VERSION') as f:
    version = f.read().strip()

setup(
    name='simple-http-monitor',
    version=version,
    description='small utilities to monitor http traffic',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Jonathan Billaud',
    url='https://github.com/jonatak/simple-http-monitor',
    install_requires=requirements,
    packages=find_packages(exclude=("tests",)),
    entry_points={
        'console_scripts': ['simple-http-monitor=aio.monitoring:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
    tests_require=['pytest', 'pytest-asyncio'],
)
