#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import tkinter
import tkinter.messagebox as tkmsg


class RevPiOption(tkinter.Frame):

    def __init__(self, master, xmlcli):
        super().__init__(master)
        self.pack()

        self.xmlcli = xmlcli

        # Fenster bauen
        self._createwidgets()
        self._loadappdata()

    def _createwidgets(self):
        self.master.wm_title("RevPi Python PLC Connections")
        self.master.wm_resizable(width=False, height=False)

        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}
        cpadwe = {"padx": 4, "pady": 2, "sticky": "we"}

        # Gruppe Start/Stop
        stst = tkinter.LabelFrame(self)
        stst["text"] = "Start / Stopp Verhalten"
        stst.grid(columnspan=2, pady=2, sticky="we")

        self.var_start = tkinter.BooleanVar(stst)
        self.var_reload = tkinter.BooleanVar(stst)
        self.var_zexit = tkinter.BooleanVar(stst)
        self.var_zerr = tkinter.BooleanVar(stst)

        ckb_start = tkinter.Checkbutton(stst)
        ckb_start["text"] = "Programm automatisch starten"
        ckb_start["variable"] = self.var_start
        ckb_start.grid(**cpadw)
        ckb_reload = tkinter.Checkbutton(stst)
        ckb_reload["text"] = "Programm nach Absturz neustarten"
        ckb_reload["variable"] = self.var_reload
        ckb_reload.grid(**cpadw)
        ckb_zexit = tkinter.Checkbutton(stst, justify="left")
        ckb_zexit["text"] = "Prozessabbild auf NULL setzen, wenn "
        "Programm\nerfolgreich beendet wird"
        ckb_zexit["variable"] = self.var_zexit
        ckb_zexit.grid(**cpadw)
        ckb_zerr = tkinter.Checkbutton(stst, justify="left")
        ckb_zerr["text"] = "Prozessabbild auf NULL setzen, wenn "
        "Programm\ndurch Absturz beendet wird"
        ckb_zerr["variable"] = self.var_zerr
        ckb_zerr.grid(**cpadw)

        # Gruppe Programm
        prog = tkinter.LabelFrame(self)
        prog["text"] = "Programm"
        prog.grid(columnspan=2, pady=2, sticky="we")

        self.var_startpy = tkinter.StringVar(prog)
        self.var_slave = tkinter.BooleanVar(prog)

        lbl = tkinter.Label(prog)
        lbl["text"] = "Python PLC Programname"
        lbl.grid(**cpadw)
        txt_startpy = tkinter.Entry(prog)
        txt_startpy["textvariable"] = self.var_startpy
        txt_startpy.grid(**cpadwe)
        ckb_slave = tkinter.Checkbutton(prog, justify="left")
        ckb_slave["text"] = "RevPi als PLC-Slave verwenden"
        ckb_slave["state"] = "disabled"
        ckb_slave["variable"] = self.var_slave
        ckb_slave.grid(**cpadw)

        # Gruppe XMLRPC
        xmlrpc = tkinter.LabelFrame(self)
        xmlrpc["text"] = "XML-RPC Server"
        xmlrpc.grid(columnspan=2, pady=2, sticky="we")

        self.var_xmlon = tkinter.BooleanVar(xmlrpc)
        self.var_xmlport = tkinter.StringVar(xmlrpc)
        self.var_xmlport.set("55123")

        ckb_xmlon = tkinter.Checkbutton(xmlrpc)
        ckb_xmlon["command"] = self.askxmlon
        ckb_xmlon["text"] = "XML-RPC Server aktiv auf RevPi"
        ckb_xmlon["variable"] = self.var_xmlon
        ckb_xmlon.grid(**cpadw)
        lbl = tkinter.Label(xmlrpc)
        lbl["text"] = "XML-RPC Serverport"
        lbl.grid(**cpadw)
        spb_xmlport = tkinter.Spinbox(xmlrpc)
        spb_xmlport["to"] = 65535
        spb_xmlport["from"] = 1024
        spb_xmlport["textvariable"] = self.var_xmlport
        spb_xmlport.grid(**cpadwe)

        # Buttons
        btn_save = tkinter.Button(self)
        btn_save["command"] = self._setappdata
        btn_save["text"] = "Speichern"
        btn_save.grid(column=0, row=3)

        btn_close = tkinter.Button(self)
        btn_close["command"] = self.master.destroy
        btn_close["text"] = "Schließen"
        btn_close.grid(column=1, row=3)

    def _loadappdata(self):
        dc = self.xmlcli.get_config()

        self.var_start.set(dc["autostart"])
        self.var_reload.set(dc["autoreload"])
        self.var_zexit.set(dc["zeroonexit"])
        self.var_zerr.set(dc["zeroonerror"])

        self.var_startpy.set(dc["plcprogram"])
        self.var_slave.set(dc["plcslave"])

        self.var_xmlon.set(dc["xmlrpc"])
        self.var_xmlport.set(dc["xmlrpcport"])

    def _setappdata(self):
        dc = {}
        dc["autostart"] = int(self.var_start.get())
        dc["autoreload"] = int(self.var_reload.get())
        dc["zeroonexit"] = int(self.var_zexit.get())
        dc["zeroonerror"] = int(self.var_zerr.get())

        dc["plcprogram"] = self.var_startpy.get()
        dc["plcslave"] = int(self.var_slave.get())

        dc["xmlrpc"] = int(self.var_xmlon.get())
        dc["xmlrpcport"] = self.var_xmlport.get()

        ask = tkmsg.askyesnocancel(
            "Frage", "Die Einstellungen werden jetzt auf den Revolution Pi "
            "gespeichert.\nSollen die neuen Einstellungen sofort in Kraft "
            "treten? Dies bedeutet einen Neustart des Dienstes und des ggf. "
            "laufenden PLC-Programms!", parent=self.master
        )
        if ask is not None:
            self.xmlcli.set_config(dc, ask)
            tkmsg.showinfo(
                "Information", "Einstellungen gespeichert.", parent=self.master
            )

    def askxmlon(self):
        if not self.var_xmlon.get():
            ask = tkmsg.askyesno(
                "Frage", "Soll der XML-RPC Server wirklich beendet werden? "
                "Sie können dann mit diesem Programm NICHT mehr auf den "
                "Revolution Pi zugreifen.", parent=self.master
            )
            if not ask:
                self.var_xmlon.set(True)
