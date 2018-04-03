# -*- coding: utf-8 -*-
#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
u"""Zeigt die Logfiles an."""
import tkinter
from mytools import gettrans

# Übersetzung laden
_ = gettrans()


class RevPiLogfile(tkinter.Frame):

    u"""Baut Fenster für Logfiles."""

    def __init__(self, master, xmlcli):
        u"""Init RevPiLogfile-Class."""
        super().__init__(master)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.pack(fill="both", expand=True)
        self.xmlcli = xmlcli

        # Systemvariablen
        self.loadblock = 16384
        self.errapp = 0
        self.errplc = 0
        self.mrkapp = 0
        self.mrkplc = 0

        # Fenster bauen
        self._createwidgets()

    def _checkclose(self, event=None):
        u"""Prüft ob Fenster beendet werden soll.
        @param event tkinter-Event"""
        self.master.destroy()

    def _createwidgets(self):
        u"""Erstellt alle Widgets."""
        self.master.wm_title(_("RevPi Python PLC Logs"))

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=0)

        # PLC Log
        self.lblapplog = tkinter.Label(self)
        self.lblapplog["text"] = _("RevPiPyLoad - Logfile")
        self.lblapplog.grid(column=0, row=0, sticky="w")
        self.btnapplog = tkinter.Button(self)
        self.btnapplog["command"] = self.btn_clearplc
        self.btnapplog["text"] = _("Clear screen")
        self.btnapplog.grid(column=1, row=0, sticky="e")

        self.plclog = tkinter.Text(self)
        self.plcscr = tkinter.Scrollbar(self)
        self.plclog.grid(sticky="wnse", columnspan=2, column=0, row=1)
        self.plcscr.grid(sticky="ns", column=2, row=1)
        self.plclog["yscrollcommand"] = self.plcscr.set
        self.plcscr["command"] = self.plclog.yview

        # APP Log
        self.lblapplog = tkinter.Label(self)
        self.lblapplog["text"] = _("Python PLC program - Logfile")
        self.lblapplog.grid(column=3, row=0, sticky="w")
        self.btnapplog = tkinter.Button(self)
        self.btnapplog["command"] = self.btn_clearapp
        self.btnapplog["text"] = _("Clear screen")
        self.btnapplog.grid(column=4, row=0, sticky="e")

        self.applog = tkinter.Text(self)
        self.appscr = tkinter.Scrollbar(self)
        self.applog.grid(sticky="nesw", columnspan=2, column=3, row=1)
        self.appscr.grid(sticky="ns", column=5, row=1)
        self.applog["yscrollcommand"] = self.appscr.set
        self.appscr["command"] = self.applog.yview

        # Logtimer zum Laden starten
        self.get_applog(full=True)
        self.get_plclog(full=True)

    def btn_clearapp(self):
        u"""Leert die Logliste der App."""
        self.applog.delete(1.0, tkinter.END)

    def btn_clearplc(self):
        u"""Leert die Logliste des PLC."""
        self.plclog.delete(1.0, tkinter.END)

    def get_applog(self, full=False):
        u"""Ruft App Logbuch ab.
        @param full Ganzes Logbuch laden"""

        # Logs abrufen und letzte Position merken
        try:
            self.mrkapp = self._load_log(
                self.applog, self.xmlcli.load_applog, self.mrkapp, full
            )
            self.errapp = 0
        except:
            self.errapp += 1

        # Timer neu starten
        self.master.after(1000, self.get_applog)

    def get_plclog(self, full=False):
        u"""Ruft PLC Logbuch ab.
        @param full Ganzes Logbuch laden"""

        # Logs abrufen und letzte Position merken
        try:
            self.mrkplc = self._load_log(
                self.plclog, self.xmlcli.load_plclog, self.mrkplc, full
            )
            self.errplc = 0
        except:
            self.errplc += 1

        # Timer neu starten
        self.master.after(1000, self.get_plclog)

    def _load_log(self, textwidget, xmlcall, startposition, full):
        u"""Läd die angegebenen Logfiles herunter.

        @param textwidget Widget in das Logs eingefügt werden sollen
        @param xmlcall xmlrpc Funktion zum Abrufen der Logdaten
        @param startposition Startposition ab der Logdaten kommen sollen
        @param full Komplettes Logbuch laden
        @return Ende der Datei (neue Startposition)

        """
        roll = textwidget.yview()[1] == 1.0
        startposition = 0 if full else startposition
        logbytes = b''
        while True:
            # Datenblock vom XML-RPC Server holen
            bytebuff = xmlcall(startposition, self.loadblock).data

            logbytes += bytebuff
            startposition += len(bytebuff)

            # Prüfen ob alle Daten übertragen wurden
            if len(bytebuff) < self.loadblock:
                break

        if full:
            textwidget.delete(1.0, tkinter.END)

        if bytebuff == b'\x16':  # 'ESC'
            # Kein Zugriff auf Logdatei
            textwidget.delete(1.0, tkinter.END)
            textwidget.insert(
                tkinter.END, _("Can not access log file on the RevPi")
            )
        elif bytebuff == b'\x19':  # 'EndOfMedia'
            # Logdatei neu begonnen
            startposition = 0
        else:
            # Text in Widget übernehmen
            textwidget.insert(tkinter.END, logbytes.decode("utf-8"))

        # Automatisch ans Ende rollen
        if roll or full:
            textwidget.see(tkinter.END)

        return startposition
