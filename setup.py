import os

from setuptools import setup, find_packages, Command
from setuptools.command.install import install


NAME = 'Migrate'
AUTHOR = 'Hugo'
VERSION = '0.0.0.1'
EMAIL = 'hugoxia@126.com'
DESCRIPTION = ()
KEYWORDS = []

with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()

PACKAGES = find_packages(exclude=['tests'])
EXTRAS_REQUIRE = {}


if __name__ == '__main__':
    setup(
        name=NAME,
        author=AUTHOR,
        version=VERSION,
        author_email=EMAIL,
        description=DESCRIPTION,
        keywords=KEYWORDS,
        entry_points={
            'console_scripts': [
                'migrate': 'migrate.command:main',
            ],
        }
        extras_require=EXTRAS_REQUIRE,
        tests_require=['nose'],
        install_requires=INSTALL_REQUIRES,
        packages=PACKAGES,
        include_package_data=True,
        zip_safe=False,
    )
