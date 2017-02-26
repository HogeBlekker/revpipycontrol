#!/usr/bin/python3
#
# (c) Sven Sager, License: GPLv3
#
# -*- coding: utf-8 -*-
import revpicheckclient
import tkinter
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from xmlrpc.client import ServerProxy, Binary


class RevPiPyLogs(tkinter.Frame):
    
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
        self.plclog["yscrollcommand"] = self.plcscr.set
        self.plcscr["command"] = self.plclog.yview

        # APP Log
        self.applog = tkinter.Text(self)
        self.appscr = tkinter.Scrollbar(self)
        self.appscr.pack(side="right", fill="y")
        self.applog.pack(side="right", expand=True, fill="both")
        self.applog["yscrollcommand"] = self.appscr.set
        self.appscr["command"] = self.applog.yview

        self.get_applog()
        self.get_plclog()

    def get_applog(self):
        self.applog.delete(1.0, tkinter.END)
        self.applog.insert(1.0, self.xmlcli.get_applog())
        self.applog.see(tkinter.END)
    
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
        self.plcrunning()

    def _createwidgets(self):
        """Erstellt den Fensterinhalt."""
        # Hauptfenster
        self.master.wm_title("RevPi Python PLC Loader")

        self.var_status = tkinter.StringVar()
        self.txt_status = tkinter.Entry()
        self.txt_status["textvariable"] = self.var_status
        self.txt_status.pack(fill="x")

        self.btn_plcrunning = tkinter.Button(self)
        self.btn_plcrunning["text"] = "PLC Status"
        self.btn_plcrunning["command"] = self.plcrunning
        self.btn_plcrunning.pack(fill="x")

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

    def plclogs(self):
        root = tkinter.Tk()
        self.tklogs = RevPiPyLogs(root, self.cli)

    def plcmonitor(self):
        root = tkinter.Tk()
        self.tkmonitor = revpicheckclient.RevPiCheckClient(root, self.cli)

    def plcstart (self):
        self.cli.plcstart()
        self.plcrunning()

    def plcstop(self):
        self.cli.plcstop()
        self.plcrunning()

    def plcrestart(self):
        self.cli.plcrestart()
        self.plcrunning()

    def plcrunning(self):
        if self.cli.plcrunning():
            self.btn_plcrunning["activebackground"] = "green"
            self.btn_plcrunning["bg"] = "green"
        else:
            self.btn_plcrunning["activebackground"] = "red"
            self.btn_plcrunning["bg"] = "red"
        self.var_status.set(self.cli.plcexitcode())


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiPyControl(root)
    myapp.mainloop()
