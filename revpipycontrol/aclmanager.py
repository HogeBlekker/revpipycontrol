# -*- coding: utf-8 -*-
#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
u"""Manager für ACL Einträge."""
import tkinter
import tkinter.messagebox as tkmsg
from mytools import gettrans
from re import fullmatch
from tkinter import ttk

# Übersetzung laden
_ = gettrans()


class IpAclManager():

    """Verwaltung fuer IP Adressen und deren ACL Level."""

    def __init__(self, minlevel, maxlevel, acl=None):
        """Init IpAclManager class.

        @param minlevel Smallest access level (min. 0)
        @param maxlevel Biggest access level (max. 9)
        @param acl ACL Liste fuer Berechtigungen als <class 'str'>

        """
        if type(minlevel) != int:
            raise ValueError("parameter minlevel must be <class 'int'>")
        if type(maxlevel) != int:
            raise ValueError("parameter maxlevel must be <class 'int'>")
        if minlevel < 0:
            raise ValueError("minlevel must be 0 or more")
        if maxlevel > 9:
            raise ValueError("maxlevel maximum is 9")
        if minlevel > maxlevel:
            raise ValueError("minlevel is smaller than maxlevel")

        self.__dict_acl = {}
        self.__dict_regex = {}
        self.__dict_knownips = {}
        self.__re_ipacl = "(([\\d\\*]{1,3}\\.){3}[\\d\\*]{1,3},[" \
            + str(minlevel) + "-" + str(maxlevel) + "] ?)*"

        # Liste erstellen, wenn übergeben
        if acl is not None:
            self.__set_acl(acl)

    def __iter__(self):
        """Gibt einzelne ACLs als <class 'tuple'> aus."""
        for aclip in sorted(self.__dict_acl):
            yield (aclip, self.__dict_acl[aclip])

    def __get_acl(self):
        """Getter fuer den rohen ACL-String.
        return ACLs als <class 'str'>"""
        str_acl = ""
        for aclip in sorted(self.__dict_acl):
            str_acl += "{},{} ".format(aclip, self.__dict_acl[aclip])
        return str_acl.strip()

    def __get_regex_acl(self):
        """Gibt formatierten RegEx-String zurueck.
        return RegEx Code als <class 'str'>"""
        return self.__re_ipacl

    def __set_acl(self, value):
        """Uebernimmt neue ACL-Liste fuer die Ausertung der Level.
        @param value Neue ACL-Liste als <class 'str'>"""
        if type(value) != str:
            raise ValueError("parameter acl must be <class 'str'>")

        value = value.strip()
        if fullmatch(self.__re_ipacl, value) is None:
            raise ValueError("acl format ist not okay - 1.2.3.4,0 5.6.7.8,1")

        # Klassenwerte übernehmen
        self.__dict_acl = {}
        self.__dict_regex = {}
        self.__dict_knownips = {}

        # Liste neu füllen mit regex Strings
        for ip_level in value.split():
            ip, level = ip_level.split(",", 1)
            self.__dict_acl[ip] = int(level)
            self.__dict_regex[ip] = \
                ip.replace(".", "\\.").replace("*", "\\d{1,3}")

    def get_acllevel(self, ipaddress):
        """Prueft IP gegen ACL List und gibt ACL-Wert aus.
        @param ipaddress zum pruefen
        @return <class 'int'> ACL Wert oder -1 wenn nicht gefunden"""
        # Bei bereits aufgelösten IPs direkt ACL auswerten
        if ipaddress in self.__dict_knownips:
            return self.__dict_knownips[ipaddress]

        for aclip in sorted(self.__dict_acl, reverse=True):
            if fullmatch(self.__dict_regex[aclip], ipaddress) is not None:
                # IP und Level merken
                self.__dict_knownips[ipaddress] = self.__dict_acl[aclip]

                # Level zurückgeben
                return self.__dict_acl[aclip]

        return -1

    def loadacl(self, str_acl):
        """Laed ACL String und gibt erfolg zurueck.
        @param str_acl ACL als <class 'str'>
        @return True, wenn erfolgreich uebernommen"""
        if fullmatch(self.__re_ipacl, str_acl) is None:
            return False
        self.__set_acl(str_acl)
        return True

    acl = property(__get_acl, __set_acl)
    regex_acl = property(__get_regex_acl)


class AclManager(ttk.Frame):

    u"""Hauptfenster des ACL-Managers."""

    def __init__(self, master, minlevel, maxlevel, acl_str="", readonly=False):
        u"""Init RevPiOption-Class.
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
            lbl["text"] = _("Level") + " {}: {}".format(
                acltext, self.__dict_acltext[acltext]
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

        ip_block = ttk.Entry(frame, width=4)
        ip_block["state"] = self.__ro
        ip_block["textvariable"] = self.var_ip1
        ip_block.grid(row=row, column=1)
        ip_block = ttk.Entry(frame, width=4)
        ip_block["state"] = self.__ro
        ip_block["textvariable"] = self.var_ip2
        ip_block.grid(row=row, column=3)
        ip_block = ttk.Entry(frame, width=4)
        ip_block["state"] = self.__ro
        ip_block["textvariable"] = self.var_ip3
        ip_block.grid(row=row, column=5)
        ip_block = ttk.Entry(frame, width=4)
        ip_block["state"] = self.__ro
        ip_block["textvariable"] = self.var_ip4
        ip_block.grid(row=row, column=7)

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
                    "\nIP: {} / Level: {}").format(*lst_ipacl),
                parent=self.master, default="no"
            )
            if ask:
                self.__acl.loadacl(
                    self.__acl.acl.replace(
                        "{},{}".format(*lst_ipacl), ""
                    ).replace("  ", " ")
                )
                self._refreshacls()

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

    def _savefields(self):
        u"""Übernimmt neuen ACL Eintrag."""
        new_acl = "{}.{}.{}.{},{}".format(
            self.var_ip1.get(),
            self.var_ip2.get(),
            self.var_ip3.get(),
            self.var_ip4.get(),
            self.var_acl.get()
        )
        if self.__acl.loadacl(self.__acl.acl + " " + new_acl):
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


if __name__ == "__main__":
    root = AclManager(tkinter.Tk(), 0, 9, " 192.168.50.100,2 127.0.0.*,1")
    root.acltext = {0: "Keine Rechte", 1: "Hohe Rechte"}
    root.mainloop()
    print(root.acl)
