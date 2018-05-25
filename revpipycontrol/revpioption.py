# -*- coding: utf-8 -*-
#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
u"""Optionsfenster."""
import tkinter
import tkinter.messagebox as tkmsg
from aclmanager import AclManager
from mytools import gettrans

# Übersetzung laden
_ = gettrans()


class RevPiOption(tkinter.Frame):

    u"""Zeigt Optionen von RevPiPyLoad an."""

    def __init__(self, master, xmlcli):
        u"""Init RevPiOption-Class.
        @return None"""
        try:
            self.dc = xmlcli.get_config()
        except:
            self.dc = None
            return None

        super().__init__(master)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.master.protocol("WM_DELETE_WINDOW", self._checkclose)
        self.pack(expand=True, fill="both")

        # XML-RPC Server konfigurieren
        self.xmlcli = xmlcli
        self.xmlmodus = self.xmlcli.xmlmodus()

        self.mrk_xmlmodask = False
        self.dorestart = False

        # Fenster bauen
        self._createwidgets()
        self._loadappdata()

    def _changesdone(self):
        u"""Prüft ob sich die Einstellungen geändert haben.
        @return True, wenn min. eine Einstellung geändert wurde"""
        return (
            self.var_start.get() != self.dc.get("autostart", 1)
            or self.var_reload.get() != self.dc.get("autoreload", 1)
            or self.var_reload_delay.get() !=
            str(self.dc.get("autoreloaddelay", 5))
            or self.var_zexit.get() != self.dc.get("zeroonexit", 0)
            or self.var_zerr.get() != self.dc.get("zeroonerror", 0)
            # TODO: rtlevel (0)
            or self.var_startpy.get() != self.dc.get("plcprogram", "none.py")
            or self.var_startargs.get() != self.dc.get("plcarguments", "")
            or self.var_pythonver.get() != self.dc.get("pythonversion", 3)
            or self.var_slave.get() != self.dc.get("plcslave", 0)
            or self.var_slaveacl.get() != self.dc.get("plcslaveacl", "")
            or self.var_mqtton.get() != self.dc.get("mqtt", 0)
            or self.var_xmlon.get() != self.dc.get("xmlrpc", 0)
            or self.var_xmlacl.get() != self.dc.get("xmlrpcacl", "")
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

    def _checkvalues(self):
        u"""Prüft alle Werte auf Gültigkeit.
        @return True, wenn alle Werte gültig sind"""
        if not self.var_reload_delay.get().isdigit():
            tkmsg.showerror(
                _("Error"),
                _("The value of 'restart delay' ist not valid."),
                parent=self.master
            )
            return False

        return True

    def _createwidgets(self):
        u"""Erstellt Widgets."""
        self.master.wm_title(_("RevPi Python PLC Options"))
        self.master.wm_resizable(width=False, height=False)

        xmlstate = "normal" if self.xmlmodus >= 4 else "disabled"

        cpade = {"padx": 4, "pady": 2, "sticky": "e"}
        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}
        cpadwe = {"padx": 4, "pady": 2, "sticky": "we"}

        # Gruppe Start/Stop
        stst = tkinter.LabelFrame(self)
        stst["text"] = _("Start / Stop behavior")
        stst.grid(columnspan=2, pady=2, sticky="we")

        self.var_start = tkinter.BooleanVar(stst)
        self.var_reload = tkinter.BooleanVar(stst)
        self.var_reload_delay = tkinter.StringVar(stst)
        self.var_zexit = tkinter.BooleanVar(stst)
        self.var_zerr = tkinter.BooleanVar(stst)

        ckb_start = tkinter.Checkbutton(stst)
        ckb_start["text"] = _("Start program automatically")
        ckb_start["state"] = xmlstate
        ckb_start["variable"] = self.var_start
        ckb_start.grid(columnspan=2, **cpadw)

        ckb_reload = tkinter.Checkbutton(stst)
        ckb_reload["text"] = _("Restart program after exit")
        ckb_reload["state"] = xmlstate
        ckb_reload["variable"] = self.var_reload
        ckb_reload.grid(columnspan=2, **cpadw)

        lbl = tkinter.Label(stst)
        lbl["text"] = _("Restart after n seconds of delay")
        lbl.grid(**cpadw)
        sbx = tkinter.Spinbox(stst)
        sbx["to"] = 60
        sbx["from_"] = 5
        sbx["textvariable"] = self.var_reload_delay
        sbx["width"] = 4
        sbx.grid(column=1, row=2, **cpade)

        lbl = tkinter.Label(stst)
        lbl["text"] = _("Set process image to NULL if program terminates...")
        lbl.grid(columnspan=2, **cpadw)

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
        prog.columnconfigure(0, weight=1)
        prog.columnconfigure(1, weight=1)
        prog["text"] = _("PLC program")
        prog.grid(columnspan=2, pady=2, sticky="we")

        self.var_pythonver = tkinter.IntVar(prog)
        self.var_startpy = tkinter.StringVar(prog)
        self.var_startargs = tkinter.StringVar(prog)

        self.var_pythonver.set(3)

        lbl = tkinter.Label(prog)
        lbl["text"] = _("Python version") + ":"
        lbl.grid(columnspan=2, row=0, **cpadw)

        rbn = tkinter.Radiobutton(prog)
        rbn["state"] = xmlstate
        rbn["text"] = "Python2"
        rbn["value"] = 2
        rbn["variable"] = self.var_pythonver
        rbn.grid(column=0, row=1, **cpade)

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

        # Gruppe Services
        services = tkinter.LabelFrame(self)
        services["text"] = _("RevPiPyLoad server services")
        services.grid(columnspan=2, pady=2, sticky="we")

        # RevPiSlave Service
        self.var_slave = tkinter.BooleanVar(services)
        self.var_slaveacl = tkinter.StringVar(services)
        row = 0
        ckb_slave = tkinter.Checkbutton(services, justify="left")
        ckb_slave["state"] = xmlstate
        ckb_slave["text"] = _("Use RevPi as PLC-Slave")
        ckb_slave["variable"] = self.var_slave
        ckb_slave.grid(column=0, **cpadw)

        btn_slaveacl = tkinter.Button(services, justify="center")
        btn_slaveacl["command"] = self.btn_slaveacl
        btn_slaveacl["text"] = _("Edit ACL")
        btn_slaveacl.grid(column=1, row=row, **cpadwe)

        row = 1
        lbl = tkinter.Label(services)
        lbl["text"] = _("RevPi-Slave service is:")
        lbl.grid(column=0, **cpade)

        status = self.xmlcli.plcslaverunning()
        lbl = tkinter.Label(services)
        lbl["fg"] = "green" if status else "red"
        lbl["text"] = _("running") if status else _("stopped")
        lbl.grid(column=1, row=row, **cpadwe)

        # MQTT Service
        self.var_mqtton = tkinter.BooleanVar(services)
        try:
            status = self.xmlcli.mqttrunning()
        except:
            pass
        else:
            row = 2
            ckb_slave = tkinter.Checkbutton(services, justify="left")
            ckb_slave["state"] = xmlstate
            ckb_slave["text"] = _("MQTT process image publisher")
            ckb_slave["variable"] = self.var_mqtton
            ckb_slave.grid(column=0, **cpadw)

            btn_slaveacl = tkinter.Button(services, justify="center")
            # TODO: btn_slaveacl["command"] = self.btn_mqttsettings
            btn_slaveacl["text"] = _("Settings")
            btn_slaveacl.grid(column=1, row=row, **cpadwe)

            row = 3
            lbl = tkinter.Label(services)
            lbl["text"] = _("MQTT publish service is:")
            lbl.grid(column=0, **cpade)

            status = self.xmlcli.mqttrunning()
            lbl = tkinter.Label(services)
            lbl["fg"] = "green" if status else "red"
            lbl["text"] = _("running") if status else _("stopped")
            lbl.grid(column=1, row=row, **cpadwe)

        # XML-RPC Service
        self.var_xmlon = tkinter.BooleanVar(services)
        self.var_xmlacl = tkinter.StringVar(services)
        row = 4
        ckb_xmlon = tkinter.Checkbutton(services)
        ckb_xmlon["command"] = self.askxmlon
        ckb_xmlon["state"] = xmlstate
        ckb_xmlon["text"] = _("Activate XML-RPC server on RevPi")
        ckb_xmlon["variable"] = self.var_xmlon
        ckb_xmlon.grid(**cpadw)

        btn_slaveacl = tkinter.Button(services, justify="center")
        btn_slaveacl["command"] = self.btn_xmlacl
        btn_slaveacl["text"] = _("Edit ACL")
        btn_slaveacl.grid(column=1, row=row, **cpadwe)

        # Buttons am Ende
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

        self.var_start.set(self.dc.get("autostart", 1))
        self.var_reload.set(self.dc.get("autoreload", 1))
        self.var_reload_delay.set(self.dc.get("autoreloaddelay", 5))
        self.var_zexit.set(self.dc.get("zeroonexit", 0))
        self.var_zerr.set(self.dc.get("zeroonerror", 0))
        # TODO: rtlevel (0)

        self.var_startpy.set(self.dc.get("plcprogram", "none.py"))
        self.var_startargs.set(self.dc.get("plcarguments", ""))
        self.var_pythonver.set(self.dc.get("pythonversion", 3))

        self.var_mqtton.set(self.dc.get("mqtt", 0))

        self.var_slave.set(self.dc.get("plcslave", 0))
        self.var_slaveacl.set(self.dc.get("plcslaveacl", ""))

        self.var_xmlon.set(self.dc.get("xmlrpc", 0))
        self.var_xmlacl.set(self.dc.get("xmlrpcacl", ""))

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

        # Gültigkeitsprüfung
        if not self._checkvalues():
            return None

        ask = tkmsg.askokcancel(
            _("Question"),
            _("The settings will be set on the Revolution Pi now. \n\n"
                "If you made changes on the 'PCL Program' section, your plc "
                "program will restart! \n"
                "ACL changes and service settings are applied immediately."),
            parent=self.master
        )
        if ask:
            self.dc["autoreload"] = int(self.var_reload.get())
            self.dc["autoreloaddelay"] = int(self.var_reload_delay.get())
            self.dc["autostart"] = int(self.var_start.get())
            self.dc["plcprogram"] = self.var_startpy.get()
            self.dc["plcarguments"] = self.var_startargs.get()
            self.dc["pythonversion"] = self.var_pythonver.get()
            # TODO: rtlevel (0)
            self.dc["zeroonerror"] = int(self.var_zerr.get())
            self.dc["zeroonexit"] = int(self.var_zexit.get())

            self.dc["mqtt"] = int(self.var_mqtton.get())

            self.dc["plcslave"] = int(self.var_slave.get())
            self.dc["plcslaveacl"] = self.var_slaveacl.get()

            self.dc["xmlrpc"] = int(self.var_xmlon.get())
            self.dc["xmlrpcacl"] = self.var_xmlacl.get()

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

    def btn_slaveacl(self):
        u"""Öffnet Fenster für ACL-Verwaltung."""
        win = tkinter.Toplevel(self)
        win.focus_set()
        win.grab_set()
        slaveacl = AclManager(
            win, 0, 1,
            self.var_slaveacl.get(),
            readonly=self.xmlmodus < 4
        )
        slaveacl.acltext = {
            0: _("read only"),
            1: _("read and write")
        }
        self.wait_window(win)
        self.var_slaveacl.set(slaveacl.acl)

    def btn_xmlacl(self):
        u"""Öffnet Fenster für ACL-Verwaltung."""
        win = tkinter.Toplevel(self)
        win.focus_set()
        win.grab_set()
        slaveacl = AclManager(
            win, 0, 4,
            self.var_xmlacl.get(),
            readonly=self.xmlmodus < 4
        )
        slaveacl.acltext = {
            0: _("Start/Stop PLC program and read logs"),
            1: _("+ read IOs in watch modus"),
            2: _("+ read properties and download PLC program"),
            3: _("+ upload PLC program"),
            4: _("+ set properties")
        }
        self.wait_window(win)
        self.var_xmlacl.set(slaveacl.acl)
