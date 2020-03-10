import io

from setuptools import find_packages, setup

setup(
    name='smpplib',
    version='2.1.0',
    url='https://github.com/podshumok/python-smpplib',
    description='SMPP library for python',
    long_description=io.open('README.md', 'rt', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['six'],
    tests_require=['pytest', 'mock', 'tox'],
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Communications :: Telephony',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
    ],
)
