# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
setup(
    name="TanTan",
    version="0.2.0",
    author="Joaquin Rosales",
    author_email="globojorro@gmail.com",
    packages=["tantan"],
    scripts=[],
    url="https://pypi.python.org/pypi/TanTan",
    license="LICENSE",
    description="An open-source application for communicating with \
        Physical-Area-Networks using the ZigBee protocol",
    long_description="""A collection of services, protocols, clients and
        servers based on the Twisted framework.
        """,
    install_requires=[
        "setuptools >= 3.4.4",
        "pySerial",
        "pyOpenSSl",
        "autobahn[twisted,accelerate] == 0.8.10",
        "paisley",
        "txXBee"
    ],
)
