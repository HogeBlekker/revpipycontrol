# -*- coding: utf-8 -*-
u"""Manager für ACL Einträge."""

__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2018 Sven Sager"
__license__ = "GPLv3"

import tkinter
import tkinter.messagebox as tkmsg
from mytools import gettrans
from shared.ipaclmanager import IpAclManager
from tkinter import ttk

# Übersetzung laden
_ = gettrans()


class AclManager(ttk.Frame):

    u"""Hauptfenster des ACL-Managers."""

    def __init__(self, master, minlevel, maxlevel, acl_str="", readonly=False):
        u"""Init AclManger-Class.
        @return None"""
        super().__init__(master)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.master.protocol("WM_DELETE_WINDOW", self._checkclose)
        self.pack(expand=True, fill="both")

        # Daten laden
        self.__acl = IpAclManager(minlevel, maxlevel, acl_str)
        self.__dict_acltext = {}
        self.__oldacl = self.__acl.acl
        self.__ro = "disabled" if readonly else "normal"
        self.maxlevel = maxlevel
        self.minlevel = minlevel

        # Fenster bauen
        self._createwidgets()

    def __get_acltext(self):
        """Getter fuer Leveltexte.
        @return Leveltexte als <class 'dict'>"""
        return self.__dict_acltext.copy()

    def __set_acltext(self, value):
        """Setter fuer Leveltexte.
        @param value Leveltexte als <class 'dict'>"""
        if type(value) != dict:
            raise ValueError("value must be <class 'dict'>")
        self.__dict_acltext = value.copy()

        # Infotexte aufbauen
        self.aclinfo.destroy()
        self.aclinfo = ttk.Frame(self)
        for acltext in self.__dict_acltext:
            lbl = ttk.Label(self.aclinfo)
            lbl["text"] = _("Level") + " {id}: {text}".format(
                id=acltext, text=self.__dict_acltext[acltext]
            )
            lbl.pack(anchor="w")

        self.aclinfo.pack(anchor="w", padx=4, pady=4)

    def _changesdone(self):
        u"""Prüft ob sich die Einstellungen geändert haben.
        @return True, wenn min. eine Einstellung geändert wurde"""
        return not self.__acl.acl == self.__oldacl

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
        self.master.wm_title(_("IP access control list"))
        self.master.wm_resizable(width=False, height=False)

        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}

        # Gruppe Bestehende ACL ######################################
        gb_acl = ttk.LabelFrame(self)
        gb_acl["text"] = _("Existing ACLs")
        gb_acl.columnconfigure(0, weight=1)
        gb_acl.columnconfigure(1, weight=1)
        gb_acl.pack(expand=True, fill="both", padx=4, pady=4)

        row = 0
        frame = ttk.Frame(gb_acl)
        frame.columnconfigure(0, weight=1)

        scb_acl = ttk.Scrollbar(frame)

        self.trv_acl = ttk.Treeview(frame)
        self.trv_acl["columns"] = ("level")
        self.trv_acl["yscrollcommand"] = scb_acl.set
        self.trv_acl.heading("level", text=_("Access level"))
        self.trv_acl.column("level", width=100)
        self.trv_acl.bind("<<TreeviewSelect>>", self._status_editremove)
        self._refreshacls()
        self.trv_acl.grid(row=0, column=0, sticky="we")

        scb_acl["command"] = self.trv_acl.yview
        scb_acl.grid(row=0, column=1, sticky="ns")

        frame.grid(row=row, columnspan=2, sticky="we")

        row = 1

        # Edit / Remove button
        self.btn_edit = ttk.Button(gb_acl)
        self.btn_edit["command"] = self._loadfields
        self.btn_edit["text"] = _("load entry")
        self.btn_edit["state"] = "disabled"
        self.btn_edit.grid(row=row, column=0, pady=4)

        self.btn_remove = ttk.Button(gb_acl)
        self.btn_remove["command"] = self._ask_delete
        self.btn_remove["text"] = _("remove entry")
        self.btn_remove["state"] = "disabled"
        self.btn_remove.grid(row=row, column=1, pady=4)

        # ############################################################

        # Gruppe Bearbeiten ##########################################
        gb_edit = ttk.LabelFrame(self)
        gb_edit["text"] = _("Edit acess control list")
        gb_edit.pack(expand=True, fill="both", padx=4, pady=4)

        frame = ttk.Frame(gb_edit)
        frame.grid()

        row = 0
        lbl = ttk.Label(frame)
        lbl["text"] = _("IP address") + ": "
        lbl.grid(row=row, column=0, **cpadw)

        # Variablen IP / Level
        self.var_ip1 = tkinter.StringVar(frame)
        self.var_ip2 = tkinter.StringVar(frame)
        self.var_ip3 = tkinter.StringVar(frame)
        self.var_ip4 = tkinter.StringVar(frame)
        self.var_acl = tkinter.StringVar(frame, self.minlevel)

        ip_block1 = ttk.Entry(frame, width=4)
        ip_block2 = ttk.Entry(frame, width=4)
        ip_block3 = ttk.Entry(frame, width=4)
        ip_block4 = ttk.Entry(frame, width=4)

        ip_block1.bind(
            "<KeyRelease>",
            lambda event, tkvar=self.var_ip1: self._checkdot(
                event, tkvar, ip_block2
            )
        )
        ip_block1["state"] = self.__ro
        ip_block1["textvariable"] = self.var_ip1
        ip_block1.grid(row=row, column=1)

        ip_block2.bind(
            "<KeyRelease>",
            lambda event, tkvar=self.var_ip2: self._checkdot(
                event, tkvar, ip_block3
            )
        )
        ip_block2.bind(
            "<Key>",
            lambda event, tkvar=self.var_ip2: self._checkback(
                event, tkvar, ip_block1
            )
        )
        ip_block2["state"] = self.__ro
        ip_block2["textvariable"] = self.var_ip2
        ip_block2.grid(row=row, column=3)

        ip_block3.bind(
            "<KeyRelease>",
            lambda event, tkvar=self.var_ip3: self._checkdot(
                event, tkvar, ip_block4
            )
        )
        ip_block3.bind(
            "<Key>",
            lambda event, tkvar=self.var_ip3: self._checkback(
                event, tkvar, ip_block2
            )
        )
        ip_block3["state"] = self.__ro
        ip_block3["textvariable"] = self.var_ip3
        ip_block3.grid(row=row, column=5)

        ip_block4.bind(
            "<KeyRelease>",
            lambda event, tkvar=self.var_ip4: self._checkdot(
                event, tkvar, None
            )
        )
        ip_block4.bind(
            "<Key>",
            lambda event, tkvar=self.var_ip4: self._checkback(
                event, tkvar, ip_block3
            )
        )
        ip_block4["state"] = self.__ro
        ip_block4["textvariable"] = self.var_ip4
        ip_block4.grid(row=row, column=7)

        # Punkte zwischen IP-Feldern
        for i in range(2, 7, 2):
            lbl = ttk.Label(frame, text=".")
            lbl.grid(row=row, column=i)

        row = 1
        lbl = ttk.Label(frame)
        lbl["text"] = _("Access level") + ": "
        lbl.grid(row=row, column=0, **cpadw)

        self.sb_level = tkinter.Spinbox(frame, width=4)
        self.sb_level["from_"] = self.minlevel
        self.sb_level["to"] = self.maxlevel
        self.sb_level["state"] = self.__ro
        self.sb_level["textvariable"] = self.var_acl
        self.sb_level.grid(row=row, column=1, columnspan=8, sticky="w")

        # Buttons neben IP-Eintrag
        self.btn_add = ttk.Button(gb_edit)
        self.btn_add["command"] = self._savefields
        self.btn_add["state"] = self.__ro
        self.btn_add["text"] = _("add to list")
        self.btn_add.grid(column=0, row=1, sticky="e", padx=4, pady=4)
        self.btn_clear = ttk.Button(gb_edit)
        self.btn_clear["command"] = self._clearfields
        self.btn_clear["state"] = self.__ro
        self.btn_clear["text"] = _("clear")
        self.btn_clear.grid(column=1, row=1, padx=4, pady=4)

        # ############################################################

        frame = ttk.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.pack(expand=True, fill="both", pady=4)

        # Buttons
        btn_save = ttk.Button(frame)
        btn_save["command"] = self._save
        btn_save["state"] = self.__ro
        btn_save["text"] = _("Save")
        btn_save.grid(column=0, row=0)

        btn_close = ttk.Button(frame)
        btn_close["command"] = self._checkclose
        btn_close["text"] = _("Close")
        btn_close.grid(column=1, row=0)

        # Infotexte vorbereiten
        self.aclinfo = ttk.Frame(self)

    def _ask_delete(self):
        u"""Löscht ein Eintrag der Liste."""
        str_acl = self.trv_acl.focus()
        if str_acl != "":
            lst_ipacl = str_acl.split()
            ask = tkmsg.askyesno(
                _("Question"),
                _("Do you really want to delete the following item? \n"
                    "\nIP: {0} / Level: {1}").format(*lst_ipacl),
                parent=self.master, default="no"
            )
            if ask:
                new_acl = self.__acl.acl.replace(
                    "{0},{1}".format(*lst_ipacl), ""
                ).replace("  ", " ")

                if self.__acl.loadacl(new_acl.strip()):
                    # Liste neu aufbauen
                    self._refreshacls()
                else:
                    tkmsg.showerror(
                        _("Error"),
                        _("Can not delete ACL! Check format."),
                        parent=self.master
                    )

    def _checkback(self, event, tkvar, pretxt):
        u"""Springt bei Backspace in vorheriges Feld.

        @param event TK Event
        @param tkvar TK Variable zum prüfen
        @param nexttxt Vorheriges IP Feld für Fokus

        """
        if pretxt is not None and event.keycode == 22 and tkvar.get() == "":
            pretxt.focus_set()

    def _checkdot(self, event, tkvar, nexttxt):
        u"""Prüft auf . und geht weiter.

        @param event TK Event
        @param tkvar TK Variable zum prüfen
        @param nexttxt Nächstes IP Feld für Fokus

        """
        val = tkvar.get()
        if val.find(".") >= 0:
            tkvar.set(val[:-1])
            if nexttxt is not None:
                nexttxt.focus_set()

    def _clearfields(self):
        u"""Leert die Eingabefelder."""
        self.var_ip1.set("")
        self.var_ip2.set("")
        self.var_ip3.set("")
        self.var_ip4.set("")
        self.var_acl.set(self.minlevel)

    def _loadfields(self):
        u"""Übernimmt Listeneintrag in Editfelder."""
        str_acl = self.trv_acl.focus()
        if str_acl != "":
            lst_ip, acl = str_acl.split()
            lst_ip = lst_ip.split(".")
            self.var_ip1.set(lst_ip[0])
            self.var_ip2.set(lst_ip[1])
            self.var_ip3.set(lst_ip[2])
            self.var_ip4.set(lst_ip[3])
            self.var_acl.set(acl)

    def _refreshacls(self):
        u"""Leert die ACL Liste und füllt sie neu."""
        self.trv_acl.delete(*self.trv_acl.get_children())
        for tup_acl in self.__acl:
            self.trv_acl.insert(
                "", "end", tup_acl, text=tup_acl[0], values=tup_acl[1]
            )

    def _save(self):
        u"""Übernimt die Änderungen."""
        self.__oldacl = self.__acl.acl
        self._checkclose()

    def _savefields(self):
        u"""Übernimmt neuen ACL Eintrag."""
        new_acl = "{0}.{1}.{2}.{3},{4}".format(
            self.var_ip1.get(),
            self.var_ip2.get(),
            self.var_ip3.get(),
            self.var_ip4.get(),
            self.var_acl.get()
        )
        if self.__acl.loadacl((self.__acl.acl + " " + new_acl).strip()):
            self._refreshacls()
        else:
            tkmsg.showerror(
                _("Error"),
                _("Can not load new ACL! Check format."),
                parent=self.master
            )

    def _status_editremove(self, tkevt):
        u"""Setzt state der Buttons."""
        if self.__ro == "normal":
            status = "disabled" if self.trv_acl.focus() == "" else "normal"
            self.btn_edit["state"] = status
            self.btn_remove["state"] = status

    def get_acl(self):
        u"""Gibt die Konfigurierten ACL zurück.
        @return ACL als <class 'str'>"""
        return self.__oldacl

    acl = property(get_acl)
    acltext = property(__get_acltext, __set_acltext)


# Debugging
if __name__ == "__main__":
    root = AclManager(tkinter.Tk(), 0, 9, " 192.168.50.100,2 127.0.0.*,1")
    root.acltext = {0: "Keine Rechte", 1: "Hohe Rechte"}
    root.mainloop()
