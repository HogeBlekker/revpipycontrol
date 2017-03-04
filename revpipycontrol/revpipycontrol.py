#!/usr/bin/python3
#
# RevPiPyControl
# Version: 0.2.0
#
# Webpage: https://revpimodio.org/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import revpicheckclient
import tkinter
from argparse import ArgumentParser
from xmlrpc.client import ServerProxy, Binary


class RevPiPlcLogs(tkinter.Frame):

    def __init__(self, master, xmlcli):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.xmlcli = xmlcli
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


class RevPiPyControl(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        # Command arguments
        parser = ArgumentParser(
            description="Revolution Pi IO-Client"
        )
        parser.add_argument(
            "-a", "--address", dest="address", default="127.0.0.1",
            help="Server address (Default: 127.0.0.1)"
        )
        parser.add_argument(
            "-p", "--port", dest="port", type=int, default=55123,
            help="Use port to connect to server (Default: 55074)"
        )
        self.pargs = parser.parse_args()

        self.cli = ServerProxy(
            "http://{}:{}".format(self.pargs.address, self.pargs.port)
        )

        # Fenster aufbauen
        self._createwidgets()

        # Daten aktualisieren
        self.tmr_plcrunning()

    def _createwidgets(self):
        """Erstellt den Fensterinhalt."""
        # Hauptfenster
        self.master.wm_title("RevPi Python PLC Loader")

        self.var_opt = tkinter.StringVar()
        self.lst_opt = [
            "Verbindungen...",
            "------------------",
            "PLC Log...",
            "PLC Monitor...",
            "PLC Optionen...",
            "------------------",
            "Beenden",
        ]
        self.opt_menu = tkinter.OptionMenu(
            self, self.var_opt, *self.lst_opt, command=self._opt_do
        )
        self.opt_menu.pack(fill="x")

        self.var_conn = tkinter.StringVar()
        self.txt_conn = tkinter.Entry(self)
        self.txt_conn["state"] = "readonly"
        self.txt_conn["textvariable"] = self.var_conn
        self.txt_conn.pack()

        self.btn_plcstart = tkinter.Button(self)
        self.btn_plcstart["text"] = "PLC Start"
        self.btn_plcstart["command"] = self.plcstart
        self.btn_plcstart.pack(fill="x")

        self.btn_plcstop = tkinter.Button(self)
        self.btn_plcstop["text"] = "PLC Stop"
        self.btn_plcstop["command"] = self.plcstop
        self.btn_plcstop.pack(fill="x")

        self.btn_plcrestart = tkinter.Button(self)
        self.btn_plcrestart["text"] = "PLC Restart"
        self.btn_plcrestart["command"] = self.plcrestart
        self.btn_plcrestart.pack(fill="x")

#        self.btn_plcrestart = tkinter.Button(self)
#        self.btn_plcrestart["text"] = "PLC Monitor"
#        self.btn_plcrestart["command"] = self.plcmonitor
#        self.btn_plcrestart.pack(fill="x")

        self.btn_plcrestart = tkinter.Button(self)
        self.btn_plcrestart["text"] = "PLC Logs"
        self.btn_plcrestart["command"] = self.plclogs
        self.btn_plcrestart.pack(fill="x")

        self.var_status = tkinter.StringVar()
        self.txt_status = tkinter.Entry(self)
        self.txt_status["state"] = "readonly"
        self.txt_status["textvariable"] = self.var_status
        self.txt_status.pack()

    def _opt_do(self, text):
        optselect = self.lst_opt.index(text)
        if optselect == 0:
            # Verbindungen
            pass
        elif optselect == 2:
            self.plclogs()
        elif optselect == 3:
            pass
            # self.plcmonitor()
        elif optselect == 4:
            # Optionen
            pass
        elif optselect == 6:
            self.master.destroy()
        self.var_opt.set("")

    def plclogs(self):
        root = tkinter.Tk()
        self.tklogs = RevPiPlcLogs(root, self.cli)

    def plcmonitor(self):
        root = tkinter.Tk()
        self.tkmonitor = revpicheckclient.RevPiCheckClient(root, self.cli)

    def plcstart(self):
        self.cli.plcstart()

    def plcstop(self):
        self.cli.plcstop()

    def plcrestart(self):
        self.cli.plcstop()
        self.cli.plcstart()

    def tmr_plcrunning(self):
        if self.cli.plcrunning():
            self.txt_status["readonlybackground"] = "green"
        else:
            self.txt_status["readonlybackground"] = "red"

        plcec = self.cli.plcexitcode()
        if plcec == -1:
            plcec = "RUNNING"
        elif plcec == 0:
            plcec = "NOT RUNNING"
        self.var_status.set(plcec)

        self.master.after(1000, self.tmr_plcrunning)


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiPyControl(root)
    myapp.mainloop()
