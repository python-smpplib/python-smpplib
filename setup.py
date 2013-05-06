from setuptools import setup, find_packages
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name="python-smpplib",
      version='1.0.1',
      url='https://github.com/podshumok/python-smpplib',
      description='SMPP library for python',
      packages=find_packages(),
      zip_safe=True,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Communications :: Telephony',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved',
        ],
      **extra
)
