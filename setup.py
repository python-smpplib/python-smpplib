import io

from setuptools import find_packages, setup

try:
    long_description_kwd=dict(
        long_description=io.open('README.md', 'rt', encoding='utf-8').read(),
        long_description_content_type='text/markdown',
    )
except OSError:
    long_description_kwd=dict()

setup(
    name='smpplib',
    version='2.2.4',
    url='https://github.com/python-smpplib/python-smpplib',
    description='SMPP library for python',
    packages=find_packages(),
    install_requires=['six'],
    zip_safe=True,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python',
        'Topic :: Communications :: Telephony',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
    ),
    **long_description_kwd
)
