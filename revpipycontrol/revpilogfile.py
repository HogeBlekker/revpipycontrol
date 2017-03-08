#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import tkinter


class RevPiLogfile(tkinter.Frame):

    def __init__(self, master, xmlcli):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.xmlcli = xmlcli

        # Fenster bauen
        self._createwidgets()

    def _createwidgets(self):
        self.master.wm_title("RevPi Python PLC Logs")

        # PLC Log
        self.plclog = tkinter.Text(self)
        self.plcscr = tkinter.Scrollbar(self)
        self.plclog.pack(side="left", expand=True, fill="both")
        self.plcscr.pack(side="left", fill="y")
        # self.plclog["state"] = "disabled"
        self.plclog["yscrollcommand"] = self.plcscr.set
        self.plcscr["command"] = self.plclog.yview

        # APP Log
        self.applog = tkinter.Text(self)
        self.appscr = tkinter.Scrollbar(self)
        self.appscr.pack(side="right", fill="y")
        self.applog.pack(side="right", expand=True, fill="both")
        # self.applog["state"] = "disabled"
        self.applog["yscrollcommand"] = self.appscr.set
        self.appscr["command"] = self.applog.yview

        self.get_applog()
        self.get_plclog()

        # Timer zum nachladen aktivieren
        self.master.after(1000, self.get_applines)
        self.master.after(1000, self.get_plclines)

    def get_applines(self):
        roll = self.applog.yview()[1] == 1.0
        for line in self.xmlcli.get_applines():
            self.applog.insert(tkinter.END, line)
        if roll:
            self.applog.see(tkinter.END)
        self.master.after(1000, self.get_applines)

    def get_applog(self):
        self.applog.delete(1.0, tkinter.END)
        self.applog.insert(1.0, self.xmlcli.get_applog())
        self.applog.see(tkinter.END)

    def get_plclines(self):
        roll = self.plclog.yview()[1] == 1.0
        for line in self.xmlcli.get_plclines():
            self.plclog.insert(tkinter.END, line)
        if roll:
            self.plclog.see(tkinter.END)
        self.master.after(1000, self.get_plclines)

    def get_plclog(self):
        self.plclog.delete(1.0, tkinter.END)
        self.plclog.insert(1.0, self.xmlcli.get_plclog())
        self.plclog.see(tkinter.END)
