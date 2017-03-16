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
        self.pack(expand=True, fill="both")

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
        ckb_zexit["text"] = "Prozessabbild auf NULL setzen, wenn " \
            "Programm\nerfolgreich beendet wird"
        ckb_zexit["variable"] = self.var_zexit
        ckb_zexit.grid(**cpadw)
        ckb_zerr = tkinter.Checkbutton(stst, justify="left")
        ckb_zerr["text"] = "Prozessabbild auf NULL setzen, wenn " \
            "Programm\ndurch Absturz beendet wird"
        ckb_zerr["variable"] = self.var_zerr
        ckb_zerr.grid(**cpadw)

        # Gruppe Programm
        prog = tkinter.LabelFrame(self)
        prog["text"] = "PLC Programm"
        prog.grid(columnspan=2, pady=2, sticky="we")

        self.var_pythonver = tkinter.IntVar(prog)
        self.var_startpy = tkinter.StringVar(prog)
        self.var_slave = tkinter.BooleanVar(prog)
        
        self.var_pythonver.set(3)

        lbl = tkinter.Label(prog)
        lbl["text"] = "Python Version"
        lbl.grid(columnspan=2, row=0, **cpadw)
        rbn = tkinter.Radiobutton(prog)
        rbn["text"] = "Python2"
        rbn["value"] = 2
        rbn["variable"] = self.var_pythonver
        rbn.grid(column=0, row=1, **cpadw)
        rbn = tkinter.Radiobutton(prog)
        rbn["text"] = "Python3"
        rbn["value"] = 3
        rbn["variable"] = self.var_pythonver
        rbn.grid(column=1, row=1, **cpadw)
        lbl = tkinter.Label(prog)
        lbl["text"] = "Python PLC Programname"
        lbl.grid(columnspan=2, **cpadw)
        lst = self.xmlcli.get_filelist()
        if len(lst) == 0:
            lst.append("none")
        opt_startpy = tkinter.OptionMenu(
            prog, self.var_startpy, *lst)
        opt_startpy.grid(columnspan=2, **cpadwe)
        ckb_slave = tkinter.Checkbutton(prog, justify="left")
        ckb_slave["text"] = "RevPi als PLC-Slave verwenden"
        ckb_slave["state"] = "disabled"
        ckb_slave["variable"] = self.var_slave
        ckb_slave.grid(columnspan=2, **cpadw)

        # Gruppe XMLRPC
        xmlrpc = tkinter.LabelFrame(self)
        xmlrpc["text"] = "XML-RPC Server"
        xmlrpc.grid(columnspan=2, pady=2, sticky="we")

        self.var_xmlon = tkinter.BooleanVar(xmlrpc)
        self.var_xmlmod2 = tkinter.BooleanVar(xmlrpc)
        self.var_xmlmod3 = tkinter.BooleanVar(xmlrpc)
        self.var_xmlport = tkinter.StringVar(xmlrpc)
        self.var_xmlport.set("55123")

        ckb_xmlon = tkinter.Checkbutton(xmlrpc)
        ckb_xmlon["command"] = self.askxmlon
        ckb_xmlon["text"] = "XML-RPC Server aktiv auf RevPi"
        ckb_xmlon["variable"] = self.var_xmlon
        ckb_xmlon.grid(**cpadw)
        self.ckb_xmlmod2 = tkinter.Checkbutton(xmlrpc, justify="left")
        self.ckb_xmlmod2["command"] = self.xmlmods
        self.ckb_xmlmod2["text"] = \
            "Download von piCtory Konfiguration und\nPLC Programm zulassen"
        self.ckb_xmlmod2["variable"] = self.var_xmlmod2
        self.ckb_xmlmod2.grid(**cpadw)
        self.ckb_xmlmod3 = tkinter.Checkbutton(xmlrpc, justify="left")
        self.ckb_xmlmod3["text"] = \
            "Upload von piCtory Konfiguration und\nPLC Programm zualssen"
        self.ckb_xmlmod3["variable"] = self.var_xmlmod3
        self.ckb_xmlmod3.grid(**cpadw)
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
        self.var_pythonver.set(dc["pythonversion"])
        self.var_slave.set(dc["plcslave"])

        self.var_xmlon.set(dc["xmlrpc"] >= 1)
        self.var_xmlmod2.set(dc["xmlrpc"] >= 2)
        self.var_xmlmod3.set(dc["xmlrpc"] >= 3)

        self.var_xmlport.set(dc["xmlrpcport"])

    def _setappdata(self):
        dc = {}
        dc["autostart"] = int(self.var_start.get())
        dc["autoreload"] = int(self.var_reload.get())
        dc["zeroonexit"] = int(self.var_zexit.get())
        dc["zeroonerror"] = int(self.var_zerr.get())

        dc["plcprogram"] = self.var_startpy.get()
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

        ask = tkmsg.askyesnocancel(
            "Frage", "Die Einstellungen werden jetzt auf den Revolution Pi "
            "gespeichert. \n\nSollen die neuen Einstellungen sofort in Kraft "
            "treten? \nDies bedeutet einen Neustart des Dienstes und des ggf. "
            "laufenden PLC-Programms!", parent=self.master
        )
        if ask is not None:
            if self.xmlcli.set_config(dc, ask):
                tkmsg.showinfo(
                    "Information", "Einstellungen gespeichert.", parent=self.master
                )
            else:
                tkmsg.showerror(
                    "Fehler", "Die Einstellungen konnten nicht gesichert"
                    "werden. Dies kann passieren, wenn Werte falsch sind!",
                    parent=self.master
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

        self.xmlmods()
    
    def xmlmods(self):
        self.ckb_xmlmod2["state"] = \
            "normal" if self.var_xmlon.get() else "disabled"
        self.ckb_xmlmod3["state"] = \
            "normal" if self.var_xmlmod2.get() else "disabled"
