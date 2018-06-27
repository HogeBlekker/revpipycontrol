#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# RevPiPyControl
# Version: see global var pycontrolverion
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
u"""Hauptprogramm."""
import revpicheckclient
import revpiinfo
import revpilogfile
import revpioption
import revpilegacy
import revpiplclist
import revpiprogram
import socket
import tkinter
import tkinter.messagebox as tkmsg
import webbrowser
from mytools import addroot, gettrans
from xmlrpc.client import ServerProxy

# Übersetzung laden
_ = gettrans()

pycontrolversion = "0.6.2"


class RevPiPyControl(tkinter.Frame):

    u"""Baut Hauptprogramm auf."""

    def __init__(self, master=None):
        u"""Init RevPiPyControl-Class.
        @param master tkinter master"""
        super().__init__(master)
        self.master.protocol("WM_DELETE_WINDOW", self._closeapp)
        self.pack(fill="both", expand=True)

        self.cli = None
        self.dict_conn = revpiplclist.get_connections()
        self.errcount = 0
        self.revpiname = None
        self.revpipyversion = [0, 0, 0]
        self.xmlfuncs = []
        self.xmlmode = 0

        # Debugger vorbereiten
        self.debugframe = None

        # Globale Fenster
        self.tkcheckclient = None
        self.tklogs = None
        self.tkoptions = None
        self.tkprogram = None

        # Fenster aufbauen
        self._createwidgets()

        # Daten aktualisieren
        self.tmr_plcrunning()

    def _btnstate(self):
        u"""Setzt den state der Buttons."""
        stateval = "disabled" if self.cli is None else "normal"
        self.btn_plclogs["state"] = stateval
        self.btn_plcstart["state"] = stateval
        self.btn_plcstop["state"] = stateval
        self.btn_plcrestart["state"] = stateval
        self.btn_debug["state"] = stateval

    def _closeall(self):
        u"""Schließt alle Fenster."""
        if self.tkcheckclient is not None:
            self.tkcheckclient.destroy()
        if self.tklogs is not None:
            self.tklogs.master.destroy()
        if self.tkoptions is not None:
            self.tkoptions.destroy()
        if self.tkprogram is not None:
            self.tkprogram.destroy()
        if self.debugframe is not None:
            self.debugframe.destroy()
            self.debugframe = None
            try:
                self.cli.psstop()
            except:
                pass

    def _closeapp(self, event=None):
        u"""Räumt auf und beendet Programm.
        @param event tkinter Event"""
        self._closeall()
        self.master.destroy()

    def _createwidgets(self):
        u"""Erstellt den Fensterinhalt."""
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
        menu1.add_command(label=_("Connections..."), command=self.plclist)
        menu1.add_separator()
        menu1.add_command(label=_("Exit"), command=self.master.destroy)
        self.mbar.add_cascade(label=_("Main"), menu=menu1)

        self._fillmbar()
        self._fillconnbar()

        # Hilfe Menü
        menu1 = tkinter.Menu(self.mbar, tearoff=False)
        menu1.add_command(
            label=_("Visit website..."), command=self.visitwebsite)
        menu1.add_separator()
        menu1.add_command(label=_("Info..."), command=self.infowindow)
        self.mbar.add_cascade(label=_("Help"), menu=menu1)

        self.var_conn = tkinter.StringVar(self)
        self.txt_connect = tkinter.Entry(self, state="readonly", width=40)
        self.txt_connect["textvariable"] = self.var_conn
        self.txt_connect.pack(fill="x")

        self.btn_plcstart = tkinter.Button(self)
        self.btn_plcstart["text"] = _("PLC start")
        self.btn_plcstart["command"] = self.plcstart
        self.btn_plcstart.pack(fill="x")

        self.btn_plcstop = tkinter.Button(self)
        self.btn_plcstop["text"] = _("PLC stop")
        self.btn_plcstop["command"] = self.plcstop
        self.btn_plcstop.pack(fill="x")

        self.btn_plcrestart = tkinter.Button(self)
        self.btn_plcrestart["text"] = _("PLC restart")
        self.btn_plcrestart["command"] = self.plcrestart
        self.btn_plcrestart.pack(fill="x")

        self.btn_plclogs = tkinter.Button(self)
        self.btn_plclogs["text"] = _("PLC logs")
        self.btn_plclogs["command"] = self.plclogs
        self.btn_plclogs.pack(fill="x")

        self.var_status = tkinter.StringVar(self)
        self.txt_status = tkinter.Entry(self)
        self.txt_status["state"] = "readonly"
        self.txt_status["textvariable"] = self.var_status
        self.txt_status.pack(fill="x")

        self.btn_debug = tkinter.Button(self)
        self.btn_debug["text"] = _("PLC watch mode")
        self.btn_debug["command"] = self.plcdebug
        self.btn_debug.pack(fill="x")

    def _fillconnbar(self):
        u"""Generiert Menüeinträge für Verbindungen."""
        self.mconn.delete(0, "end")
        for con in sorted(self.dict_conn.keys(), key=lambda x: x.lower()):
            self.mconn.add_command(
                label=con, command=lambda con=con: self._opt_conn(con)
            )

    def _fillmbar(self):
        u"""Generiert Menüeinträge."""
        # PLC Menü
        self.mplc = tkinter.Menu(self.mbar, tearoff=False)
        self.mplc.add_command(
            label=_("PLC log..."), command=self.plclogs)
        self.mplc.add_command(
            label=_("PLC options..."), command=self.plcoptions)
        self.mplc.add_command(
            label=_("PLC program..."), command=self.plcprogram)
        self.mplc.add_separator()

        self.mplc.add_command(
            label=_("Disconnect"), command=self.serverdisconnect)
        self.mbar.add_cascade(label="PLC", menu=self.mplc, state="disabled")

        # Connection Menü
        self.mconn = tkinter.Menu(self.mbar, tearoff=False)
        self.mbar.add_cascade(label=_("Connect"), menu=self.mconn)

    def _opt_conn(self, text, reconnect=False):
        u"""Stellt eine neue Verbindung zu RevPiPyLoad her.
        @param text Verbindungsname
        @param reconnect Socket Timeout nicht heruntersetzen"""
        if reconnect:
            socket.setdefaulttimeout(10)
        else:
            socket.setdefaulttimeout(2)

        sp = ServerProxy(
            "http://{}:{}".format(
                self.dict_conn[text][0], int(self.dict_conn[text][1])
            )
        )
        # Server prüfen
        try:
            self.xmlfuncs = sp.system.listMethods()
            self.xmlmode = sp.xmlmodus()
            self.revpipyversion = list(map(int, sp.version().split(".")))
        except:
            self.servererror()
        else:
            self._closeall()
            socket.setdefaulttimeout(10)
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

    def infowindow(self):
        u"""Öffnet das Fenster für die Info."""
        win = tkinter.Toplevel(self)
        win.focus_set()
        win.grab_set()
        revpiinfo.RevPiInfo(win, self.cli, pycontrolversion)
        self.wait_window(win)
        self.dict_conn = revpiplclist.get_connections()
        self._fillconnbar()

    def plcdebug(self):
        u"""Baut den Debugframe und packt ihn.
        @return None"""
        self.btn_debug["state"] = "disabled"

        if "psstart" not in self.xmlfuncs:
            tkmsg.showwarning(
                _("Warning"),
                _("The watch mode ist not supported in version {} "
                    "of RevPiPyLoad on your RevPi! You need at least version "
                    "0.5.3! Maybe the python3-revpimodio2 module is not "
                    "installed on your RevPi at least version 2.0.0."
                    "").format(self.cli.version()),
                parent=self.master
            )
        else:
            # Debugfenster laden
            if self.debugframe is None \
                    or self.debugframe.err_workvalues >= \
                    self.debugframe.max_errors:
                try:
                    self.debugframe = revpicheckclient.RevPiCheckClient(
                        self, self.cli, self.xmlmode
                    )
                except:
                    tkmsg.showwarning(
                        _("Error"),
                        _("Can not load piCtory configuration. \n"
                            "Did you create a hardware configuration? "
                            "Please check this in piCtory!"),
                        parent=self.master
                    )
                    self.btn_debug["state"] = "normal"
                    return None

            # Show/Hide wechseln
            if self.debugframe.winfo_viewable():
                self.debugframe.hideallwindows()
                if self.debugframe.autorw.get():
                    self.debugframe.autorw.set(False)
                    self.debugframe.toggleauto()
                self.debugframe.dowrite.set(False)
                self.debugframe.pack_forget()
            else:
                self.debugframe.pack(fill="x")

            self.btn_debug["state"] = "normal"

    def plclist(self):
        u"""Öffnet das Fenster für die Verbindungen."""
        win = tkinter.Toplevel(self)
        win.focus_set()
        win.grab_set()
        revpiplclist.RevPiPlcList(win)
        self.wait_window(win)
        self.dict_conn = revpiplclist.get_connections()
        self._fillconnbar()

    def plclogs(self):
        u"""Öffnet das Fenster für Logdateien.
        @return None"""
        if "load_plclog" not in self.xmlfuncs:
            tkmsg.showwarning(
                _("Warning"),
                _("This version of Logviewer ist not supported in version {} "
                    "of RevPiPyLoad on your RevPi! You need at least version "
                    "0.4.1.").format(self.cli.version()),
                parent=self.master
            )
            return None

        if self.tklogs is None or len(self.tklogs.children) == 0:
            win = tkinter.Toplevel(self)
            self.tklogs = revpilogfile.RevPiLogfile(win, self.cli)
        else:
            self.tklogs.focus_set()

    def plcoptions(self):
        u"""Startet das Optionsfenster."""
        if self.xmlmode < 2:
            tkmsg.showwarning(
                _("Warning"),
                _("XML-RPC access mode in the RevPiPyLoad "
                    "configuration is too small to access this dialog!"),
                parent=self.master
            )
        else:
            win = tkinter.Toplevel(self)
            win.focus_set()
            win.grab_set()

            # Gegenstelle prüfen und passende Optionen laden
            if self.revpipyversion[0] == 0 and self.revpipyversion[1] < 6:
                self.tkoptions = \
                    revpilegacy.RevPiOption(win, self.cli)
            else:
                self.tkoptions = \
                    revpioption.RevPiOption(win, self.cli)

            self.wait_window(win)
            if self.tkoptions.dc is not None and self.tkoptions.dorestart:

                # Wenn XML-Modus anders und Dienstneustart
                if self.xmlmode != self.cli.xmlmodus():
                    self.serverdisconnect()
                    self._opt_conn(self.revpiname, True)

                if self.debugframe is not None:
                    self.cli.psstart()

    def plcprogram(self):
        u"""Startet das Programmfenster."""
        if self.xmlmode < 2:
            tkmsg.showwarning(
                _("Warning"),
                _("XML-RPC access mode in the RevPiPyLoad "
                    "configuration is too small to access this dialog!"),
                parent=self.master
            )
        else:
            win = tkinter.Toplevel(self)
            win.focus_set()
            win.grab_set()
            self.tkprogram = revpiprogram.RevPiProgram(
                win, self.cli, self.xmlmode, self.revpiname)
            self.wait_window(win)

    def plcstart(self):
        u"""Startet das PLC Programm."""
        self.cli.plcstart()

    def plcstop(self):
        u"""Beendet das PLC Programm."""
        self.cli.plcstop()

    def plcrestart(self):
        u"""Startet das PLC Programm neu."""
        self.cli.plcstop()
        self.cli.plcstart()

    def serverdisconnect(self):
        u"""Trennt eine bestehende Verbindung."""
        self._closeall()
        socket.setdefaulttimeout(2)
        self.cli = None
        self._btnstate()
        self.mbar.entryconfig("PLC", state="disabled")
        self.var_conn.set("")

    def servererror(self):
        u"""Setzt alles zurück für neue Verbindungen."""
        self.serverdisconnect()
        tkmsg.showerror(
            _("Error"),
            _("Can not connect to RevPi XML-RPC Service! \n\n"
                "This could have the following reasons: The RevPi is not "
                "online, the XML-RPC service is not running or the ACL "
                "permission is not set for your IP!!!"),
            parent=self.master
        )

    def tmr_plcrunning(self):
        u"""Timer der den Status des PLC Programms prüft."""
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
                elif plcec == -3:
                    plcec = "NOT RUNNING (NO STATUS)"
                elif plcec == -9:
                    plcec = "PROGRAM KILLED"
                elif plcec == -15:
                    plcec = "PROGRAM TERMED"
                elif plcec == 0:
                    plcec = "NOT RUNNING"
                self.var_status.set(plcec)

        self.master.after(1000, self.tmr_plcrunning)

    def visitwebsite(self):
        u"""Öffnet auf dem System einen Webbrowser zur Projektseite."""
        webbrowser.open("https://revpimodio.org")


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiPyControl(root)
    root.mainloop()
