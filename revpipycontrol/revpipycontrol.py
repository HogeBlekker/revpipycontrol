#!/usr/bin/python3
#
# RevPiPyControl
# Version: 0.2.8
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import revpilogfile
import revpioption
import revpiplclist
import revpiprogram
import socket
import sys
import tkinter
import tkinter.messagebox as tkmsg
from functools import partial
from os.path import dirname
from os.path import join as pathjoin
from xmlrpc.client import ServerProxy


def addroot(filename):
    u"""Hängt root-dir der Anwendung vor Dateinamen.

        Je nach Ausführungsart der Anwendung muss das root-dir über
        andere Arten abgerufen werden.

        @param filename: Datei oder Ordnername
        @returns: root dir

    """
    if getattr(sys, "frozen", False):
        return pathjoin(dirname(sys.executable), filename)
    else:
        return pathjoin(dirname(__file__), filename)


class RevPiPyControl(tkinter.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.cli = None
        self.dict_conn = revpiplclist.get_connections()
        self.errcount = 0
        self.revpiname = None
        self.xmlmode = 0

        # Globale Fenster
        self.tklogs = None
        self.tkoptions = None
        self.tkprogram = None

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
        self.master.wm_iconphoto(
            True, tkinter.PhotoImage(file=addroot("revpipycontrol.png"))
        )
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
        #self.mplc.add_command(label="PLC monitor...", command=self.plcmonitor)
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
        socket.setdefaulttimeout(2)
        sp = ServerProxy(
            "http://{}:{}".format(
                self.dict_conn[text][0], int(self.dict_conn[text][1])
            )
        )
        # Server prüfen
        try:
            self.xmlmode = sp.xmlmodus()
        except:
            self.servererror()
        else:
            self._closeall()
            socket.setdefaulttimeout(15)
            self.cli = ServerProxy(
                "http://{}:{}".format(
                    self.dict_conn[text][0], int(self.dict_conn[text][1])
                )
            )
            self.revpiname = text
            self.var_conn.set("{} - {}:{}".format(
                text, self.dict_conn[text][0], int(self.dict_conn[text][1])
            ))
            self.mbar.entryconfig("PLC", state="normal")

    def _closeall(self):
        if self.tklogs is not None:
            self.tklogs.master.destroy()
        if self.tkoptions is not None:
            self.tkoptions.destroy()
        if self.tkprogram is not None:
            self.tkprogram.destroy()

    def plclist(self):
        win = tkinter.Toplevel(self)
        revpiplclist.RevPiPlcList(win)
        win.focus_set()
        win.grab_set()
        self.wait_window(win)
        self.dict_conn = revpiplclist.get_connections()
        self._fillconnbar()

    def plclogs(self):
        if self.tklogs is None or len(self.tklogs.children) == 0:
            win = tkinter.Toplevel(self)
            self.tklogs = revpilogfile.RevPiLogfile(win, self.cli)
        else:
            self.tklogs.focus_set()

    def plcmonitor(self):
        # TODO: Monitorfenster
        pass

    def plcoptions(self):
        if self.xmlmode < 2:
            tkmsg.showwarning(
                parent=self.master, title="Warnung",
                message="Der XML-RPC Modus ist beim RevPiPyLoad nicht hoch "
                "genug eingestellt, um diesen Dialog zu verwenden!"
            )
        else:
            win = tkinter.Toplevel(self)
            self.tkoptions = \
                revpioption.RevPiOption(win, self.cli, self.xmlmode)
            win.focus_set()
            win.grab_set()
            self.wait_window(win)
            self.xmlmode = self.tkoptions.xmlmode

    def plcprogram(self):
        if self.xmlmode < 2:
            tkmsg.showwarning(
                parent=self.master, title="Warnung",
                message="Der XML-RPC Modus ist beim RevPiPyLoad nicht hoch "
                "genug eingestellt, um diesen Dialog zu verwenden!"
            )
        else:
            win = tkinter.Toplevel(self)
            self.tkprogram = revpiprogram.RevPiProgram(
                win, self.cli, self.xmlmode, self.revpiname)
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
        """Setzt alles auf NULL."""
        socket.setdefaulttimeout(2)
        self.cli = None
        self._btnstate()
        self.mbar.entryconfig("PLC", state="disabled")
        self.var_conn.set("")
        self._closeall()
        tkmsg.showerror("Fehler", "Server ist nicht erreichbar!")

    def tmr_plcrunning(self):
        self._btnstate()
        if self.cli is None:
            self.txt_status["readonlybackground"] = "lightblue"
            self.var_status.set("NOT CONNECTED")
        else:
            try:
                plcec = self.cli.plcexitcode()
            except:
                self.errcount += 1
                if self.errcount >= 5:
                    self.var_status.set("SERVER ERROR")
                    self.servererror()
            else:
                self.errcount = 0
                self.txt_status["readonlybackground"] = \
                    "green" if plcec == -1 else "red"

                if plcec == -1:
                    plcec = "RUNNING"
                elif plcec == -2:
                    plcec = "FILE NOT FOUND"
                elif plcec == -9:
                    plcec = "PROGRAM KILLED"
                elif plcec == -15:
                    plcec = "PROGRAMS TERMED"
                elif plcec == 0:
                    plcec = "NOT RUNNING"
                self.var_status.set(plcec)

        self.master.after(1000, self.tmr_plcrunning)


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiPyControl(root)
    root.mainloop()
