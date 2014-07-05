# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from setuptools.command import egg_info
    egg_info.write_toplevel_names
except (ImportError, AttributeError):
    pass
else:
    def _top_level_package(name):
        return name.split('.', 1)[0]

    def _hacked_write_toplevel_names(cmd, basename, filename):
        pkgs = dict.fromkeys(
                [_top_level_package(k)
                    for k in cmd.distribution.iter_distribution_names()
                    if _top_level_package(k) != "twisted"
                    ]
                )
        cmd.write_file("top-level names", filename, '\n'.join(pkgs) + '\n')

    egg_info.write_toplevel_names = _hacked_write_toplevel_names

setup(
    name="TanTan",
    version="0.2.0",
    author="Joaquin Rosales",
    author_email="globojorro@gmail.com",
    packages=["tantan", "twisted.plugins"],
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

try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))
