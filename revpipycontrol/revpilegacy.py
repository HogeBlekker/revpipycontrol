# -*- coding: utf-8 -*-
u"""Alte Klassen laden hier, bevor sie entsorgt werden."""

__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2018 Sven Sager"
__license__ = "GPLv3"

import tkinter
import tkinter.messagebox as tkmsg
from mytools import gettrans

# Übersetzung laden
_ = gettrans()


class RevPiOption(tkinter.Frame):

    u"""Optionen für RevPiPyload vor 0.6.0."""

    def __init__(self, master, xmlcli):
        u"""Init RevPiOption-Class.
        @return None"""
        try:
            self.dc = xmlcli.get_config()
        except Exception:
            self.dc = None
            return None

        super().__init__(master)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.master.protocol("WM_DELETE_WINDOW", self._checkclose)
        self.pack(expand=True, fill="both")

        self.xmlcli = xmlcli
        self.mrk_var_xmlmod2 = False
        self.mrk_var_xmlmod3 = False
        self.mrk_xmlmodask = False
        self.dorestart = False

        # Fenster bauen
        self._createwidgets()
        self._loadappdata()

    def _changesdone(self):
        u"""Prüft ob sich die Einstellungen geändert haben.
        @return True, wenn min. eine Einstellung geändert wurde"""
        return (
            self.var_start.get() != self.dc.get("autostart", "1") or
            self.var_reload.get() != self.dc.get("autoreload", "1") or
            self.var_zexit.get() != self.dc.get("zeroonexit", "0") or
            self.var_zerr.get() != self.dc.get("zeroonerror", "0") or
            self.var_startpy.get() != self.dc.get("plcprogram", "none.py") or
            self.var_startargs.get() != self.dc.get("plcarguments", "") or
            self.var_pythonver.get() != self.dc.get("pythonversion", "3") or
            self.var_slave.get() != self.dc.get("plcslave", "0") or
            self.var_xmlon.get() != (self.dc.get("xmlrpc", 0) >= 1) or
            self.var_xmlmod2.get() != (self.dc.get("xmlrpc", 0) >= 2) or
            self.var_xmlmod3.get() != (self.dc.get("xmlrpc", 0) >= 3)
            # or self.var_xmlport.get() != self.dc.get("xmlrpcport", "55123")
        )

    def _checkclose(self, event=None):
        u"""Prüft ob Fenster beendet werden soll.
        @param event tkinter-Event"""
        ask = True
        if self._changesdone():
            ask = tkmsg.askyesno(
                _("Question"),
                _("Do you really want to quit? \nUnsaved changes will "
                    "be lost"),
                parent=self.master, default="no"
            )

        if ask:
            self.master.destroy()

    def _createwidgets(self):
        u"""Erstellt Widgets."""
        self.master.wm_title(_("RevPi Python PLC Options"))
        self.master.wm_resizable(width=False, height=False)

        xmlstate = "normal" if self.dc["xmlrpc"] >= 3 else "disabled"

        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}
        cpadwe = {"padx": 4, "pady": 2, "sticky": "we"}

        # Gruppe Start/Stop
        stst = tkinter.LabelFrame(self)
        stst["text"] = _("Start / Stop behavior")
        stst.grid(columnspan=2, pady=2, sticky="we")

        self.var_start = tkinter.BooleanVar(stst)
        self.var_reload = tkinter.BooleanVar(stst)
        self.var_zexit = tkinter.BooleanVar(stst)
        self.var_zerr = tkinter.BooleanVar(stst)

        ckb_start = tkinter.Checkbutton(stst)
        ckb_start["text"] = _("Start program automatically")
        ckb_start["state"] = xmlstate
        ckb_start["variable"] = self.var_start
        ckb_start.grid(**cpadw)

        ckb_reload = tkinter.Checkbutton(stst)
        ckb_reload["text"] = _("Restart program after exit")
        ckb_reload["state"] = xmlstate
        ckb_reload["variable"] = self.var_reload
        ckb_reload.grid(**cpadw)

        lbl = tkinter.Label(stst)
        lbl["text"] = _("Set process image to NULL if program terminates...")
        lbl.grid(**cpadw)

        ckb_zexit = tkinter.Checkbutton(stst, justify="left")
        ckb_zexit["state"] = xmlstate
        ckb_zexit["text"] = _("... successfully")
        ckb_zexit["variable"] = self.var_zexit
        ckb_zexit.grid(**cpadw)

        ckb_zerr = tkinter.Checkbutton(stst, justify="left")
        ckb_zerr["state"] = xmlstate
        ckb_zerr["text"] = _("... with errors")
        ckb_zerr["variable"] = self.var_zerr
        ckb_zerr.grid(**cpadw)

        # Gruppe Programm
        prog = tkinter.LabelFrame(self)
        prog["text"] = _("PLC program")
        prog.grid(columnspan=2, pady=2, sticky="we")

        self.var_pythonver = tkinter.IntVar(prog)
        self.var_startpy = tkinter.StringVar(prog)
        self.var_startargs = tkinter.StringVar(prog)
        self.var_slave = tkinter.BooleanVar(prog)

        self.var_pythonver.set(3)

        lbl = tkinter.Label(prog)
        lbl["text"] = _("Python version")
        lbl.grid(columnspan=2, row=0, **cpadw)

        rbn = tkinter.Radiobutton(prog)
        rbn["state"] = xmlstate
        rbn["text"] = "Python2"
        rbn["value"] = 2
        rbn["variable"] = self.var_pythonver
        rbn.grid(column=0, row=1, **cpadw)

        rbn = tkinter.Radiobutton(prog)
        rbn["state"] = xmlstate
        rbn["text"] = "Python3"
        rbn["value"] = 3
        rbn["variable"] = self.var_pythonver
        rbn.grid(column=1, row=1, **cpadw)

        # Row 2
        lbl = tkinter.Label(prog)
        lbl["text"] = _("Python PLC program name")
        lbl.grid(columnspan=2, **cpadw)

        # Row 3
        lst = self.xmlcli.get_filelist()
        if len(lst) == 0:
            lst.append("none")
        opt_startpy = tkinter.OptionMenu(
            prog, self.var_startpy, *lst
        )
        opt_startpy["state"] = xmlstate
        opt_startpy.grid(columnspan=2, **cpadwe)

        # Row 4
        lbl = tkinter.Label(prog)
        lbl["text"] = _("Program arguments")
        lbl.grid(columnspan=2, **cpadw)

        # Row 5
        txt = tkinter.Entry(prog)
        txt["textvariable"] = self.var_startargs
        txt.grid(columnspan=2, **cpadw)

        # Row 6
        ckb_slave = tkinter.Checkbutton(prog, justify="left")
        ckb_slave["state"] = xmlstate
        ckb_slave["text"] = _("Use RevPi as PLC-Slave")
        ckb_slave["variable"] = self.var_slave
        ckb_slave.grid(column=0, **cpadw)

        # Gruppe XMLRPC
        xmlrpc = tkinter.LabelFrame(self)
        xmlrpc["text"] = _("XML-RPC server")
        xmlrpc.grid(columnspan=2, pady=2, sticky="we")

        self.var_xmlon = tkinter.BooleanVar(xmlrpc)
        self.var_xmlmod2 = tkinter.BooleanVar(xmlrpc)
        self.var_xmlmod3 = tkinter.BooleanVar(xmlrpc)
#        self.var_xmlport = tkinter.StringVar(xmlrpc)
#        self.var_xmlport.set("55123")

        ckb_xmlon = tkinter.Checkbutton(xmlrpc)
        ckb_xmlon["command"] = self.askxmlon
        ckb_xmlon["state"] = xmlstate
        ckb_xmlon["text"] = _("Activate XML-RPC server on RevPi")
        ckb_xmlon["variable"] = self.var_xmlon
        ckb_xmlon.grid(**cpadw)

        self.ckb_xmlmod2 = tkinter.Checkbutton(xmlrpc, justify="left")
        self.ckb_xmlmod2["command"] = self.xmlmod2_tail
        self.ckb_xmlmod2["state"] = xmlstate
        self.ckb_xmlmod2["text"] = \
            _("Allow download of piCtory configuration and\nPLC programm")
        self.ckb_xmlmod2["variable"] = self.var_xmlmod2
        self.ckb_xmlmod2.grid(**cpadw)

        self.ckb_xmlmod3 = tkinter.Checkbutton(xmlrpc, justify="left")
        self.ckb_xmlmod3["state"] = xmlstate
        self.ckb_xmlmod3["text"] = \
            _("Allow upload of piCtory configuration and\nPLC programm")
        self.ckb_xmlmod3["variable"] = self.var_xmlmod3
        self.ckb_xmlmod3.grid(**cpadw)

        lbl = tkinter.Label(xmlrpc)
        lbl["text"] = _("XML-RPC server port")
        lbl.grid(**cpadw)

#        spb_xmlport = tkinter.Spinbox(xmlrpc)
#        spb_xmlport["to"] = 65535
#        spb_xmlport["from"] = 1024
#        spb_xmlport["state"] = xmlstate
#        spb_xmlport["textvariable"] = self.var_xmlport
#        spb_xmlport.grid(**cpadwe)

        # Buttons
        btn_save = tkinter.Button(self)
        btn_save["command"] = self._setappdata
        btn_save["state"] = xmlstate
        btn_save["text"] = _("Save")
        btn_save.grid(column=0, row=3)

        btn_close = tkinter.Button(self)
        btn_close["command"] = self._checkclose
        btn_close["text"] = _("Close")
        btn_close.grid(column=1, row=3)

    def _loadappdata(self, refresh=False):
        u"""Läd aktuelle Einstellungen vom RevPi.
        @param refresh Wenn True, werden Einstellungen heruntergeladen."""
        if refresh:
            self.dc = self.xmlcli.get_config()

        self.var_start.set(self.dc.get("autostart", "1"))
        self.var_reload.set(self.dc.get("autoreload", "1"))
        self.var_zexit.set(self.dc.get("zeroonexit", "0"))
        self.var_zerr.set(self.dc.get("zeroonerror", "0"))

        self.var_startpy.set(self.dc.get("plcprogram", "none.py"))
        self.var_startargs.set(self.dc.get("plcarguments", ""))
        self.var_pythonver.set(self.dc.get("pythonversion", "3"))
        self.var_slave.set(self.dc.get("plcslave", "0"))

        self.var_xmlon.set(self.dc.get("xmlrpc", 0) >= 1)
        self.var_xmlmod2.set(self.dc.get("xmlrpc", 0) >= 2)
        self.mrk_var_xmlmod2 = self.var_xmlmod2.get()
        self.var_xmlmod3.set(self.dc.get("xmlrpc", 0) >= 3)
        self.mrk_var_xmlmod3 = self.var_xmlmod3.get()

#        self.var_xmlport.set(self.dc.get("xmlrpcport", "55123"))

    def _setappdata(self):
        u"""Speichert geänderte Einstellungen auf RevPi.
        @return None"""

        if not self._changesdone():
            tkmsg.showinfo(
                _("Information"),
                _("You have not made any changes to save."),
                parent=self.master
            )
            self._checkclose()
            return None

        ask = tkmsg.askyesnocancel(
            _("Question"),
            _("The settings are now saved on the Revolution Pi. \n\n"
                "Should the new settings take effect immediately? \nThis "
                "means a restart of the service and the PLC program!"),
            parent=self.master
        )
        if ask is not None:
            self.dc["autostart"] = int(self.var_start.get())
            self.dc["autoreload"] = int(self.var_reload.get())
            self.dc["zeroonexit"] = int(self.var_zexit.get())
            self.dc["zeroonerror"] = int(self.var_zerr.get())

            self.dc["plcprogram"] = self.var_startpy.get()
            self.dc["plcarguments"] = self.var_startargs.get()
            self.dc["pythonversion"] = self.var_pythonver.get()
            self.dc["plcslave"] = int(self.var_slave.get())

            self.dc["xmlrpc"] = 0
            if self.var_xmlon.get():
                self.dc["xmlrpc"] += 1
                if self.var_xmlmod2.get():
                    self.dc["xmlrpc"] += 1
                    if self.var_xmlmod3.get():
                        self.dc["xmlrpc"] += 1

#            self.dc["xmlrpcport"] = self.var_xmlport.get()

            if self.xmlcli.set_config(self.dc, ask):
                tkmsg.showinfo(
                    _("Information"),
                    _("Settings saved"),
                    parent=self.master
                )
                self.dorestart = ask
                self._checkclose()
            else:
                tkmsg.showerror(
                    _("Error"),
                    _("The settings could not be saved. This can happen if "
                        "values are wrong!"),
                    parent=self.master
                )

    def askxmlon(self):
        u"""Fragt Nuter, ob wirklicht abgeschaltet werden soll."""
        if not (self.var_xmlon.get() or self.mrk_xmlmodask):
            self.mrk_xmlmodask = tkmsg.askyesno(
                _("Question"),
                _("Are you sure you want to deactivate the XML-RPC server? "
                    "You will NOT be able to access the Revolution Pi with "
                    "this program."),
                parent=self.master
            )
            if not self.mrk_xmlmodask:
                self.var_xmlon.set(True)

        self.xmlmod_tail()

    def xmlmod_tail(self):
        u"""Passt XML-Optionszugriff an."""
        if self.var_xmlon.get():
            self.var_xmlmod2.set(self.mrk_var_xmlmod2)
            self.ckb_xmlmod2["state"] = "normal"
        else:
            self.mrk_var_xmlmod2 = self.var_xmlmod2.get()
            self.var_xmlmod2.set(False)
            self.ckb_xmlmod2["state"] = "disabled"
        self.xmlmod2_tail()

    def xmlmod2_tail(self):
        u"""Passt XML-Optionszugriff an."""
        if self.var_xmlmod2.get():
            self.var_xmlmod3.set(self.mrk_var_xmlmod3)
            self.ckb_xmlmod3["state"] = "normal"
        else:
            self.mrk_var_xmlmod3 = self.var_xmlmod3.get()
            self.var_xmlmod3.set(False)
            self.ckb_xmlmod3["state"] = "disabled"
