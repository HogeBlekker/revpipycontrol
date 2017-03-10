#!/usr/bin/python3
#
# RevPiPyControl
# Version: 0.2.1
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import revpicheckclient
import revpilogfile
import revpioption
import revpiplclist
import revpiprogram
import socket
import tkinter
import tkinter.messagebox as tkmsg
from functools import partial
from xmlrpc.client import ServerProxy

socket.setdefaulttimeout(3)


class RevPiPyControl(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.cli = None
        self.dict_conn = revpiplclist.get_connections()
        self.revpiname = None

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
        self.mbar = tkinter.Menu(self.master)
        self.master.config(menu=self.mbar)

        menu1 = tkinter.Menu(self.mbar, tearoff=False)
        menu1.add_command(label="Connections...", command=self.plclist)
        menu1.add_separator()
        menu1.add_command(label="Exit", command=self.master.destroy)
        self.mbar.add_cascade(label="Main", menu=menu1)

        self._fillmbar()
        self._fillconnbar()

        self.var_conn = tkinter.StringVar(self)
        self.txt_connect = tkinter.Entry(
            self, textvariable=self.var_conn, state="readonly", width=30)
        self.txt_connect.pack(fill="x")

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
        self.txt_status.pack(fill="x")

    def _fillmbar(self):
        # PLC Menü
        self.mplc = tkinter.Menu(self.mbar, tearoff=False)
        self.mplc.add_command(label="PLC log...", command=self.plclogs)
        self.mplc.add_command(label="PLC monitor...", command=self.plcmonitor)
        self.mplc.add_command(label="PLC options...", command=self.plcoptions)
        self.mplc.add_command(label="PLC program...", command=self.plcprogram)
        self.mbar.add_cascade(label="PLC", menu=self.mplc, state="disabled")

        # Connection Menü
        self.mconn = tkinter.Menu(self.mbar, tearoff=False)
        self.mbar.add_cascade(label="Connect", menu=self.mconn)

    def _fillconnbar(self):
        self.mconn.delete(0, "end")
        for con in sorted(self.dict_conn.keys(), key=lambda x: x.lower()):
            self.mconn.add_command(
                label=con, command=partial(self._opt_conn, con)
            )

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
            self.revpiname = text
            self.var_conn.set("{} - {}:{}".format(
                text, self.dict_conn[text][0], int(self.dict_conn[text][1])
            ))
            self.mbar.entryconfig("PLC", state="normal")

    def plclist(self):
        win = tkinter.Toplevel(self)
        revpiplclist.RevPiPlcList(win)
        win.focus_set()
        win.grab_set()
        self.wait_window(win)
        self.dict_conn = revpiplclist.get_connections()
        self._fillconnbar()

    def plclogs(self):
        # TODO: nicht doppelt starten
        win = tkinter.Toplevel(self)
        self.tklogs = revpilogfile.RevPiLogfile(win, self.cli)

    def plcmonitor(self):
        # TODO: Monitorfenster
        #self.tkmonitor = revpicheckclient.RevPiCheckClient(self.master, self.cli)
        pass

    def plcoptions(self):
        win = tkinter.Toplevel(self)
        revpioption.RevPiOption(win, self.cli)
        win.focus_set()
        win.grab_set()
        self.wait_window(win)

    def plcprogram(self):
        # TODO: Programfenster
        win = tkinter.Toplevel(self)
        revpiprogram.RevPiProgram(win, self.cli, self.revpiname)
        win.focus_set()
        win.grab_set()
        self.wait_window(win)

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
        self.mbar.entryconfig("PLC", state="disabled")
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
