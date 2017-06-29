#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import pickle
import tkinter
from mytools import gettrans

# Übersetzung laden
_ = gettrans()


class RevPiLogfile(tkinter.Frame):

    def __init__(self, master, xmlcli):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.xmlcli = xmlcli

        # Fenster bauen
        self._createwidgets()

    def _createwidgets(self):
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

        self.get_applog()
        self.get_plclog()

        # Timer zum nachladen aktivieren
        self.master.after(1000, self.get_applines)
        self.master.after(1000, self.get_plclines)

    def btn_clearapp(self):
        self.applog.delete(1.0, tkinter.END)

    def btn_clearplc(self):
        self.plclog.delete(1.0, tkinter.END)

    def get_applines(self):
        roll = self.applog.yview()[1] == 1.0
        try:
            for line in pickle.loads(self.xmlcli.get_applines().data):
                self.applog.insert(tkinter.END, line)
        except:
            pass
        if roll:
            self.applog.see(tkinter.END)
        self.master.after(1000, self.get_applines)

    def get_applog(self):
        self.applog.delete(1.0, tkinter.END)
        self.applog.insert(1.0, pickle.loads(self.xmlcli.get_applog().data))
        self.applog.see(tkinter.END)

    def get_plclines(self):
        roll = self.plclog.yview()[1] == 1.0
        try:
            for line in pickle.loads(self.xmlcli.get_plclines().data):
                self.plclog.insert(tkinter.END, line)
        except:
            pass
        if roll:
            self.plclog.see(tkinter.END)
        self.master.after(1000, self.get_plclines)

    def get_plclog(self):
        self.plclog.delete(1.0, tkinter.END)
        self.plclog.insert(1.0, pickle.loads(self.xmlcli.get_plclog().data))
        self.plclog.see(tkinter.END)
