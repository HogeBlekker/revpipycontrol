#! /usr/bin/env python3
#
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
"""Setupscript fuer RevPiPyLoad."""
import distutils.command.install_egg_info
from sys import platform
from glob import glob


class MyEggInfo(distutils.command.install_egg_info.install_egg_info):

    u"""Disable egg_info installation, seems pointless for a non-library."""

    def run(self):
        u"""just pass egg_info."""
        pass


globsetup = {
    "author": "Sven Sager",
    "author_email": "akira@narux.de",
    "url": "https://revpimodio.org/revpipyplc/",
    "license": "LGPLv3",
    "version": "0.4.1",

    "name": "revpipycontrol",

    "description": "PLC Loader für Python-Projekte auf den RevolutionPi",
    "long_description": ""
    "Dieses Programm startet beim Systemstart ein angegebenes Python PLC\n"
    "Programm. Es überwacht das Programm und startet es im Fehlerfall neu.\n"
    "Bei Abstruz kann das gesamte /dev/piControl0 auf 0x00 gesettz werden.\n"
    "Außerdem stellt es einen XML-RPC Server bereit, über den die Software\n"
    "auf den RevPi geladen werden kann. Das Prozessabbild kann über ein Tool\n"
    "zur Laufzeit überwacht werden.",
}

if platform == "linux":
    from setuptools import setup
    setup(
        maintainer="Sven Sager",
        maintainer_email="akira@revpimodio.org",

        scripts=["data/revpipycontrol"],

        data_files=[
            ("share/applications", ["data/revpipycontrol.desktop"]),
            ("share/icons/hicolor/32x32/apps", ["data/revpipycontrol.png"]),
            ("share/revpipycontrol", glob("revpipycontrol/*.*")),
            (
                "share/revpipycontrol/locale/de/LC_MESSAGES",
                glob("revpipycontrol/locale/de/LC_MESSAGES/*.mo")
            ),
        ],

        install_requires=["tkinter"],

        classifiers=[
            "License :: OSI Approved :: "
            "GNU Lesser General Public License v3 (LGPLv3)",
            "Operating System :: POSIX :: Linux",
        ],
        cmdclass={"install_egg_info": MyEggInfo},
        **globsetup
    )

elif platform == "win32":
    import sys
    from cx_Freeze import setup, Executable

    sys.path.append("revpipycontrol")

    exe = Executable(
        script="revpipycontrol/revpipycontrol.py",
        base="Win32GUI",
        compress=False,
        copyDependentFiles=True,
        appendScriptToExe=True,
        appendScriptToLibrary=False,
        icon="data/revpipycontrol.ico"
    )

    setup(
        options={"build_exe": {
            "include_files": [
                "revpipycontrol/revpipycontrol.png",
                "revpipycontrol/locale"
            ]
        }},
        executables=[exe],
        **globsetup
    )
