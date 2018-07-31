# -*- coding: utf-8 -*-
#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
"""Tools-Sammlung."""
import gettext
import locale
import sys
from os import environ
from os.path import dirname
from os.path import join as pathjoin
from sys import platform

# Systemwerte und SaveFiles
if platform == "linux":
    homedir = environ["HOME"]
else:
    homedir = environ["APPDATA"]

savefile_connections = pathjoin(
    homedir, ".revpipyplc", "connections.dat")
savefile_developer = pathjoin(
    homedir, ".revpipyplc", "developer.dat")
savefile_programpath = pathjoin(
    homedir, ".revpipyplc", "programpath.dat")


def addroot(filename):
    u"""Hängt root-dir der Anwendung vor Dateinamen.

        Je nach Ausführungsart der Anwendung muss das root-dir über
        andere Arten abgerufen werden.

        @param filename Datei oder Ordnername
        @return root dir

    """
    if getattr(sys, "frozen", False):
        return pathjoin(dirname(sys.executable), filename)
    else:
        return pathjoin(dirname(__file__), filename)


def gettrans(proglang=None):
    u"""Wertet die Sprache des OS aus und gibt Übersetzung zurück.

    @param proglang Bestimmte Sprache laden
    @return gettext Übersetzung für Zuweisung an '_'

    """
    # Sprache auswählen
    if proglang is None:
        # Autodetect Language or switch to static
        proglang = locale.getdefaultlocale()[0]
        if proglang is not None and proglang.find("_") >= 0:
            proglang = proglang.split('_')[0]
        else:
            proglang = "en"

    # Übersetzungen laden
    trans = gettext.translation(
        "revpipycontrol",
        addroot("locale"),
        languages=[proglang],
        fallback=True
    )
    return trans.gettext
