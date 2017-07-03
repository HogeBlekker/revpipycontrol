#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import gettext
import locale
import sys
from os.path import dirname
from os.path import join as pathjoin


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

    # Sprache auswählen
    if proglang is None:
        # Autodetect Language or switch to static
        proglang = locale.getdefaultlocale()[0]
        if not proglang is None and proglang.find("_") >= 0:
            proglang = proglang.split('_')[0]

    # Übersetzungen laden
    trans = gettext.translation(
        "revpipycontrol",
        addroot("locale"),
        languages=[proglang],
        fallback=True
    )
    return trans.gettext
