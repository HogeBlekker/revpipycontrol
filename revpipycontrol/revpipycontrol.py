#!/usr/bin/python3
#
# RevPiPyControl
# Version: 0.2.0
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import revpicheckclient
import revpilogfile
import revpiplclist
import socket
import tkinter
import tkinter.messagebox as tkmsg
from xmlrpc.client import ServerProxy

socket.setdefaulttimeout(3)


class RevPiPyControl(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.cli = None
        self.dict_conn = revpiplclist.get_connections()

        # Fenster aufbauen
        self._createwidgets()

        # Daten aktualisieren
        self.tmr_plcrunning()

    def _btnstate(self):
        stateval = "disabled" if self.cli is None else "normal"
        self.btn_plclogs["state"] = stateval
        self.btn_plcstart["state"] = stateval
        self.btn_plcstop["state"] = stateval
        self.btn_plcrestart["state"] = stateval

    def _createwidgets(self):
        """Erstellt den Fensterinhalt."""
        # Hauptfenster
        self.master.wm_title("RevPi Python PLC Loader")
        self.master.wm_resizable(width=False, height=False)

        # Menü ganz oben
        self.var_opt = tkinter.StringVar(self)
        self.lst_opt = [
            "Connections...",
            "------------------",
            "PLC log...",
            "PLC monitor...",
            "PLC options...",
            "PLC program...",
            "------------------",
            "Exit",
        ]
        self.opt_menu = tkinter.OptionMenu(
            self, self.var_opt, *self.lst_opt, command=self._opt_do)
        self.opt_menu.pack(fill="x")

        # Verbindungen
        self.var_conn = tkinter.StringVar(self)
        self.lst_conn = sorted(self.dict_conn.keys(), key=lambda x: x.lower())
        self.opt_conn = tkinter.OptionMenu(
            self, self.var_conn, *self.lst_conn, command=self._opt_conn)
        self.opt_conn.pack(fill="x")

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

        self.btn_plclogs = tkinter.Button(self)
        self.btn_plclogs["text"] = "PLC Logs"
        self.btn_plclogs["command"] = self.plclogs
        self.btn_plclogs.pack(fill="x")

        self.var_status = tkinter.StringVar(self)
        self.txt_status = tkinter.Entry(self)
        self.txt_status["state"] = "readonly"
        self.txt_status["textvariable"] = self.var_status
        self.txt_status.pack()

    def _opt_conn(self, text):
        sp = ServerProxy(
            "http://{}:{}".format(
                self.dict_conn[text][0], int(self.dict_conn[text][1])
            )
        )
        # Server prüfen
        try:
            sp.system.listMethods()
        except:
            self.servererror()
        else:
            self.cli = sp

    def _opt_do(self, text):
        optselect = self.lst_opt.index(text)
        if optselect == 0:
            # Verbindungen
            self.plclist()
        elif optselect == 2:
            # Logs
            self.plclogs()
        elif optselect == 3:
            pass
            # self.plcmonitor()
        elif optselect == 4:
            # Optionen
            pass
        elif optselect == 5:
            # Programm updown
            pass
        elif optselect == 7:
            self.master.destroy()
        self.var_opt.set("")

    def plclist(self):
        win = tkinter.Toplevel(self)
        revpiplclist.RevPiPlcList(win)
        win.focus_set()
        win.grab_set()
        self.wait_window(win)

    def plclogs(self):
        win = tkinter.Toplevel(self)
        self.tklogs = revpilogfile.RevPiLogfile(win, self.cli)

    def plcmonitor(self):
        #self.tkmonitor = revpicheckclient.RevPiCheckClient(self.master, self.cli)
        pass

    def plcstart(self):
        self.cli.plcstart()

    def plcstop(self):
        self.cli.plcstop()

    def plcrestart(self):
        self.cli.plcstop()
        self.cli.plcstart()

    def servererror(self):
        self.cli = None
        self._btnstate()
        self.var_conn.set("")
        tkmsg.showerror("Fehler", "Server ist nicht erreichbar!")

    def tmr_plcrunning(self):
        self._btnstate()
        if self.cli is None:
            self.txt_status["readonlybackground"] = "lightblue"
            self.var_status.set("NOT CONNECTED")
        else:
            try:
                if self.cli.plcrunning():
                    self.txt_status["readonlybackground"] = "green"
                else:
                    self.txt_status["readonlybackground"] = "red"

                plcec = self.cli.plcexitcode()
            except:
                self.var_status.set("SERVER ERROR")
                self.servererror()
            else:
                if plcec == -1:
                    plcec = "RUNNING"
                elif plcec == -2:
                    plcec = "FILE NOT FOUND"
                elif plcec == 0:
                    plcec = "NOT RUNNING"
                self.var_status.set(plcec)

        self.master.after(1000, self.tmr_plcrunning)


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiPyControl(root)
    root.mainloop()
