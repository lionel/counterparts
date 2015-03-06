
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

from counterparts import __version__ as package_version

short_description_text = ("Configuration file-driven values " +
                          "for shell and Python scripts")
long_description_text = open("README.rst", "r").read()

setup(
    name='counterparts',
    version=package_version,
    description=short_description_text,
    long_description=long_description_text,
    author='Lionel D. Hummel',
    author_email='lionel@ieee.org',
    url='https://github.com/lionel/counterparts',
    packages=find_packages(),
    package_data={"tests": ["counterparts_data/conf-*"]},
    py_modules=['counterparts'],
    entry_points={
        "console_scripts": ["counterpart=counterparts:main"]
    },
    test_suite="tests.test_counterparts",
    license="GPLv2",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Filters',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Console',
        'Operating System :: POSIX'
    ],
)
