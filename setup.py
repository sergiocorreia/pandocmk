"""A minimalistic make for pandoc

See:
https://github.com/sergiocorreia/pandocmk
"""

from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get requirements from 'requirements.txt'
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [x.strip() for x in f.readlines()]

# Get version number
version = {}
with open("pandocmk/version.py") as fp:
    exec(fp.read(), version)
version = version['__version__']


setup(
    name='pandocmk',
    version=version,
    description='A minimalistic make for pandoc',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/sergiocorreia/pandocmk',
    author="Sergio Correia",
    author_email='sergio.correia@gmail.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Environment :: Console',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Text Processing :: Filters',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    keywords='pandoc panflute markdown latex',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples', 'demo']),
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pandocmk=pandocmk:main'
        ],
    },

    # Add the YAML file
    # https://python-packaging.readthedocs.io/en/latest/non-code-files.html
    include_package_data=True
)
