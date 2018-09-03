# -*- coding: utf-8 -*-
u"""Programminformationen anzeigen."""

__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2018 Sven Sager"
__license__ = "GPLv3"

import tkinter
import tkinter.font as tkf
import webbrowser
from mytools import gettrans

# Übersetzung laden
_ = gettrans()


class RevPiInfo(tkinter.Frame):

    u"""Baut Frame für Programminformationen."""

    def __init__(self, master, xmlcli, version):
        u"""Init RevPiLogfile-Class."""
        self.master = master
        self.xmlcli = xmlcli

        # Systemvariablen
        self.version = version

        # Fenster bauen
        self._createwidgets()

    def _checkclose(self, event=None):
        u"""Prüft ob Fenster beendet werden soll.
        @param event tkinter-Event"""
        self.master.destroy()

    def _createwidgets(self, extended=False):
        u"""Erstellt alle Widgets."""
        super().__init__(self.master)
        self.master.wm_title(_("RevPi Python PLC info"))
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.master.resizable(False, False)
        self.pack(fill="both", expand=True)

        # Fonts laden
        fntlarge = tkf.Font(size=20, weight="bold")
        fntmid = tkf.Font(size=15)
        fntbold = tkf.Font(size=10, weight="bold")

        # Kopfdaten
        lbl = tkinter.Label(self)
        lbl["font"] = fntlarge
        lbl["text"] = _("RevPi Python PLC - Control")
        lbl.pack(pady=5)
        lbl = tkinter.Label(self)
        lbl["font"] = fntmid
        lbl["text"] = _("Version: {0}").format(self.version)
        lbl.bind(
            "<ButtonPress-2>",
            lambda event: self._createwidgets(extended=not extended)
        )
        lbl.pack(pady=5)

        # Mittelframe geteilt (links/rechts) ---------------------------------
        frame_main = tkinter.Frame(self)
        frame_main.pack(anchor="nw", fill="x", pady=5)

        # Rows konfigurieren
        frame_main.rowconfigure(0, weight=0)
        frame_main.rowconfigure(1, weight=1)
        frame_main.rowconfigure(2, weight=1)

        int_row = 0
        cpadnw = {"padx": 4, "pady": 2, "sticky": "nw"}
        cpadsw = {"padx": 4, "pady": 2, "sticky": "sw"}

        # Linke Seite Mittelframe ----------------
        lbl = tkinter.Label(frame_main)
        lbl["font"] = fntbold
        lbl["text"] = _("RevPiPyLoad version on RevPi:")
        lbl.grid(column=0, row=int_row, **cpadnw)

        lbl = tkinter.Label(frame_main)
        lbl["font"] = fntbold
        lbl["text"] = _("not conn.") if self.xmlcli is None \
            else self.xmlcli.version()
        lbl.grid(column=1, row=int_row, **cpadnw)

        int_row += 1  # 1
        lbl = tkinter.Label(frame_main)
        lbl["justify"] = "left"
        lbl["text"] = _(
            "\nRevPiModIO, RevPiPyLoad and RevPiPyControl\n"
            "are community driven projects. They are all\n"
            "free and open source software.\n"
            "All of them comes with ABSOLUTELY NO\n"
            "WARRANTY, to the extent permitted by \n"
            "applicable law.\n"
            "\n"
            "\n"
            "(c) Sven Sager, License: LGPLv3"
        )
        lbl.grid(column=0, row=int_row, columnspan=2, **cpadnw)

        int_row += 1  # 2
        lbl = tkinter.Label(frame_main)
        lbl.bind("<ButtonPress-1>", self.visitwebsite)
        lbl["fg"] = "blue"
        lbl["text"] = "https://revpimodio.org/"
        lbl.grid(column=0, row=int_row, columnspan=2, **cpadsw)

        # int_row += 1  # 3

        # Rechte Seite Mittelframe ---------------

        # Funktionen der Gegenstelle
        if self.xmlcli is not None:
            frame_func = tkinter.Frame(frame_main)
            txt_xmlfunc = tkinter.Text(frame_func, width=30, height=15)
            scr_xmlfunc = tkinter.Scrollbar(frame_func)
            if extended:
                txt_xmlfunc.insert(tkinter.END, "\n".join(
                    self.xmlcli.system.listMethods()
                ))
            elif "get_filelist" in self.xmlcli.system.listMethods():
                txt_xmlfunc.insert(tkinter.END, "\n".join(
                    self.xmlcli.get_filelist()
                ))
            txt_xmlfunc["yscrollcommand"] = scr_xmlfunc.set
            txt_xmlfunc["state"] = "disabled"
            scr_xmlfunc["command"] = txt_xmlfunc.yview
            txt_xmlfunc.pack(side="left")
            scr_xmlfunc.pack(fill="y", side="right")
            if txt_xmlfunc.get(1.0) != "\n":
                frame_func.grid(column=3, row=0, rowspan=int_row + 1, **cpadnw)

        # Unten Beenden-Button -----------------------------------------------
        self.btnapplog = tkinter.Button(self)
        self.btnapplog["command"] = self._checkclose
        self.btnapplog["text"] = _("Close")
        self.btnapplog.pack(fill="x", padx=100)

    def visitwebsite(self, event=None):
        u"""Öffnet auf dem System einen Webbrowser zur Projektseite."""
        webbrowser.open("https://revpimodio.org")
