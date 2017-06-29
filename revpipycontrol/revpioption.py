#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import tkinter
import tkinter.messagebox as tkmsg
from mytools import gettrans

# Übersetzung laden
_ = gettrans()


class RevPiOption(tkinter.Frame):

    def __init__(self, master, xmlcli, xmlmode):
        u"""Init RevPiOption-Class.
        @returns: None"""
        if xmlmode < 2:
            return None

        super().__init__(master)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.master.protocol("WM_DELETE_WINDOW", self._checkclose)
        self.pack(expand=True, fill="both")

        self.xmlcli = xmlcli
        self.xmlmode = xmlmode
        self.xmlstate = "normal" if xmlmode == 3 else "disabled"

        # Fenster bauen
        self._createwidgets()
        self._loadappdata()

    def _changesdone(self):
        u"""Prüft ob sich die Einstellungen geändert haben.
        @returns: True, wenn min. eine Einstellung geändert wurde"""
        return (
            self.var_start.get() != self.dc.get("autostart", "1")
            or self.var_reload.get() != self.dc.get("autoreload", "1")
            or self.var_zexit.get() != self.dc.get("zeroonexit", "0")
            or self.var_zerr.get() != self.dc.get("zeroonerror", "0")
            or self.var_startpy.get() != self.dc.get("plcprogram", "none.py")
            or self.var_startargs.get() != self.dc.get("plcarguments", "")
            or self.var_pythonver.get() != self.dc.get("pythonversion", "3")
            or self.var_slave.get() != self.dc.get("plcslave", "0")
            or self.var_xmlon.get() != (self.dc.get("xmlrpc", 0) >= 1)
            or self.var_xmlmod2.get() != (self.dc.get("xmlrpc", 0) >= 2)
            or self.var_xmlmod3.get() != (self.dc.get("xmlrpc", 0) >= 3)
            or self.var_xmlport.get() != self.dc.get("xmlrpcport", "55123")
        )

    def _checkclose(self, event=None):
        u"""Prüft ob Fenster beendet werden soll.
        @param event: tkinter-Event"""
        ask = True
        if self._changesdone():
            ask = tkmsg.askyesno(
                _("Question"),
                _("Do you really want to quit? \nUnsaved changes will "
                    "be lost"),
                parent=self.master
            )

        if ask:
            self.master.destroy()

    def _createwidgets(self):
        u"""Erstellt Widgets."""
        self.master.wm_title(_("RevPi Python PLC Options"))
        self.master.wm_resizable(width=False, height=False)

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
        ckb_start["state"] = self.xmlstate
        ckb_start["variable"] = self.var_start
        ckb_start.grid(**cpadw)

        ckb_reload = tkinter.Checkbutton(stst)
        ckb_reload["text"] = _("Restart program after exit")
        ckb_reload["state"] = self.xmlstate
        ckb_reload["variable"] = self.var_reload
        ckb_reload.grid(**cpadw)

        ckb_zexit = tkinter.Checkbutton(stst, justify="left")
        ckb_zexit["state"] = self.xmlstate
        ckb_zexit["text"] = _(
            "Set process image to NULL if program\n"
            "terminates successfully")
        ckb_zexit["variable"] = self.var_zexit
        ckb_zexit.grid(**cpadw)

        ckb_zerr = tkinter.Checkbutton(stst, justify="left")
        ckb_zerr["state"] = self.xmlstate
        ckb_zerr["text"] = _(
            "Set process image to NULL if program\n"
            "terminates with errors")
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
        rbn["state"] = self.xmlstate
        rbn["text"] = "Python2"
        rbn["value"] = 2
        rbn["variable"] = self.var_pythonver
        rbn.grid(column=0, row=1, **cpadw)

        rbn = tkinter.Radiobutton(prog)
        rbn["state"] = self.xmlstate
        rbn["text"] = "Python3"
        rbn["value"] = 3
        rbn["variable"] = self.var_pythonver
        rbn.grid(column=1, row=1, **cpadw)

        lbl = tkinter.Label(prog)
        lbl["text"] = _("Python PLC program name")
        lbl.grid(columnspan=2, **cpadw)

        lst = self.xmlcli.get_filelist()
        if len(lst) == 0:
            lst.append("none")
        opt_startpy = tkinter.OptionMenu(
            prog, self.var_startpy, *lst)
        opt_startpy["state"] = self.xmlstate
        opt_startpy.grid(columnspan=2, **cpadwe)

        lbl = tkinter.Label(prog)
        lbl["text"] = _("Program arguments")
        lbl.grid(columnspan=2, **cpadw)

        txt = tkinter.Entry(prog)
        txt["textvariable"] = self.var_startargs
        txt.grid(columnspan=2, **cpadw)

        ckb_slave = tkinter.Checkbutton(prog, justify="left")
        ckb_slave["state"] = self.xmlstate
        ckb_slave["text"] = _("Use RevPi as PLC-Slave")
        ckb_slave["state"] = "disabled"
        ckb_slave["variable"] = self.var_slave
        ckb_slave.grid(columnspan=2, **cpadw)

        # Gruppe XMLRPC
        xmlrpc = tkinter.LabelFrame(self)
        xmlrpc["text"] = _("XML-RPC server")
        xmlrpc.grid(columnspan=2, pady=2, sticky="we")

        self.var_xmlon = tkinter.BooleanVar(xmlrpc)
        self.var_xmlmod2 = tkinter.BooleanVar(xmlrpc)
        self.var_xmlmod3 = tkinter.BooleanVar(xmlrpc)
        self.var_xmlport = tkinter.StringVar(xmlrpc)
        self.var_xmlport.set("55123")

        ckb_xmlon = tkinter.Checkbutton(xmlrpc)
        ckb_xmlon["command"] = self.askxmlon
        ckb_xmlon["state"] = self.xmlstate
        ckb_xmlon["text"] = _("Activate XML-RPC server on RevPi")
        ckb_xmlon["variable"] = self.var_xmlon
        ckb_xmlon.grid(**cpadw)

        self.ckb_xmlmod2 = tkinter.Checkbutton(xmlrpc, justify="left")
        self.ckb_xmlmod2["command"] = self.xmlmods
        self.ckb_xmlmod2["state"] = self.xmlstate
        self.ckb_xmlmod2["text"] = \
            _("Allow download of piCtory configuration and\nPLC programm")
        self.ckb_xmlmod2["variable"] = self.var_xmlmod2
        self.ckb_xmlmod2.grid(**cpadw)

        self.ckb_xmlmod3 = tkinter.Checkbutton(xmlrpc, justify="left")
        self.ckb_xmlmod3["state"] = self.xmlstate
        self.ckb_xmlmod3["text"] = \
            _("Allow upload of piCtory configuration and\nPLC programm")
        self.ckb_xmlmod3["variable"] = self.var_xmlmod3
        self.ckb_xmlmod3.grid(**cpadw)

        lbl = tkinter.Label(xmlrpc)
        lbl["text"] = _("XML-RPC server port")
        lbl.grid(**cpadw)

        spb_xmlport = tkinter.Spinbox(xmlrpc)
        spb_xmlport["to"] = 65535
        spb_xmlport["from"] = 1024
        spb_xmlport["state"] = self.xmlstate
        spb_xmlport["textvariable"] = self.var_xmlport
        spb_xmlport.grid(**cpadwe)

        # Buttons
        btn_save = tkinter.Button(self)
        btn_save["command"] = self._setappdata
        btn_save["state"] = self.xmlstate
        btn_save["text"] = _("Save")
        btn_save.grid(column=0, row=3)

        btn_close = tkinter.Button(self)
        btn_close["command"] = self._checkclose
        btn_close["text"] = _("Close")
        btn_close.grid(column=1, row=3)

    def _loadappdata(self):
        u"""Läd aktuelle Einstellungen vom RevPi."""
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
        self.var_xmlmod3.set(self.dc.get("xmlrpc", 0) >= 3)

        self.var_xmlport.set(self.dc.get("xmlrpcport", "55123"))

    def _setappdata(self):
        u"""Speichert geänderte Einstellungen auf RevPi."""
        dc = {}
        dc["autostart"] = int(self.var_start.get())
        dc["autoreload"] = int(self.var_reload.get())
        dc["zeroonexit"] = int(self.var_zexit.get())
        dc["zeroonerror"] = int(self.var_zerr.get())

        dc["plcprogram"] = self.var_startpy.get()
        dc["plcarguments"] = self.var_startargs.get()
        dc["pythonversion"] = self.var_pythonver.get()
        dc["plcslave"] = int(self.var_slave.get())

        dc["xmlrpc"] = 0
        if self.var_xmlon.get():
            dc["xmlrpc"] += 1
            if self.var_xmlmod2.get():
                dc["xmlrpc"] += 1
                if self.var_xmlmod3.get():
                    dc["xmlrpc"] += 1

        dc["xmlrpcport"] = self.var_xmlport.get()
        self.xmlmode = dc["xmlrpc"]

        ask = tkmsg.askyesnocancel(
            _("Question"),
            _("The settings are now saved on the Revolution Pi. \n\n"
                "Should the new settings take effect immediately? \nThis "
                "means a restart of the service and the PLC program!"),
            parent=self.master
        )
        if ask is not None:
            if self.xmlcli.set_config(dc, ask):
                tkmsg.showinfo(
                    _("Information"),
                    _("Settings saved"),
                    parent=self.master
                )
            else:
                tkmsg.showerror(
                    _("Error"),
                    _("The settings could not be saved. This can happen if "
                        "values are wrong!"),
                    parent=self.master
                )

    def askxmlon(self):
        u"""Fragt Nuter, ob wirklicht abgeschaltet werden soll."""
        if not self.var_xmlon.get():
            ask = tkmsg.askyesno(
                _("Question"),
                _("Are you sure you want to deactivate the XML-RPC server? "
                    "You will NOT be able to access the Revolution Pi with "
                    "this program."),
                parent=self.master
            )
            if not ask:
                self.var_xmlon.set(True)

        self.xmlmods()

    def xmlmods(self):
        u"""Passt XML-Optionszugriff an."""
        self.ckb_xmlmod2["state"] = \
            "normal" if self.var_xmlon.get() else "disabled"
        self.ckb_xmlmod3["state"] = \
            "normal" if self.var_xmlmod2.get() else "disabled"
