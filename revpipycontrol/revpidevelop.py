# -*- coding: utf-8 -*-
u"""PLC Programm und Konfig hoch und runterladen."""

__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2018 Sven Sager"
__license__ = "GPLv3"

import gzip
import os
import pickle
import tkinter
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmsg
from mytools import homedir
from mytools import gettrans
from mytools import savefile_developer as savefile
from tkinter import ttk
from xmlrpc.client import Binary

# Übersetzung laden
_ = gettrans()


def _loaddefaults(revpiname=None):
    u"""Übernimmt für den Pi die letzen Pfade.
    @param revpiname Einstellungen nur für RevPi laden
    @return <class 'dict'> mit Einstellungen"""
    if os.path.exists(savefile):
        with open(savefile, "rb") as fh:
            dict_all = pickle.load(fh)
        if revpiname is None:
            return dict_all
        else:
            return dict_all.get(revpiname, {})
    return {}


def _savedefaults(revpiname, settings):
    u"""Schreibt fuer den Pi die letzen Pfade.

    @param revpiname Einstellungen sind für diesen RevPi
    @param settings <class 'dict'> mit Einstellungen
    @return True, bei erfolgreicher Verarbeitung

    """
    try:
        os.makedirs(os.path.dirname(savefile), exist_ok=True)
        if revpiname is None:
            dict_all = settings
        else:
            dict_all = _loaddefaults()
            dict_all[revpiname] = settings
        with open(savefile, "wb") as fh:
            pickle.dump(dict_all, fh)
    except Exception:
        return False
    return True


class RevPiDevelop(ttk.Frame):

    u"""Zeigt Debugfenster an."""

    def __init__(self, master, xmlcli, xmlmode, revpi):
        u"""Init RevPiDevelop-Class.
        @return None"""
        if xmlmode < 3:
            return None

        super().__init__(master)
        self.pack(expand=True, fill="both")

        self.revpi = revpi
        self.xmlcli = xmlcli

        # Letzte Einstellungen übernehmen
        self.opt = _loaddefaults(revpi)

        # Einstellungen
        self.pathselected = self.opt.get("pathselected", False)
        self.watchpath = self.opt.get("watchpath", homedir)
        self.watchfiles = self.opt.get("watchfiles", [])

        # Fenster bauen
        self._createwidgets()

        # Alte Einstellungen anwenden
        if self.pathselected:
            self.load_pathfiles(silent=True)

        self.refresh_stats()

    def _checkclose(self, event=None):
        u"""Prüft ob Fenster beendet werden soll.
        @param event tkinter-Event"""

        # Einstellungen speichern
        self.opt["pathselected"] = self.pathselected
        self.opt["watchpath"] = self.watchpath
        self.opt["watchfiles"] = self.watchfiles
        _savedefaults(self.revpi, self.opt)

    def _createwidgets(self):
        u"""Erstellt alle Widgets."""
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # cpad = {"padx": 4, "pady": 2}
        # cpade = {"padx": 4, "pady": 2, "sticky": "e"}
        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}
        cpadwe = {"padx": 4, "pady": 2, "sticky": "we"}

        # Gruppe Develop
        devel = ttk.LabelFrame(self)
        devel.columnconfigure(0, weight=1)
        devel["text"] = _("File watcher for PLC development")
        devel.grid(**cpadwe)

        r = 0
        lbl = ttk.Label(devel)
        lbl["text"] = _("Path to list files:")
        lbl.grid(row=r, **cpadw)

        btn = ttk.Button(devel)
        btn["command"] = self.btn_selectpath
        btn["text"] = _("Select path")
        btn.grid(row=r, column=1, **cpadw)

        r += 1
        self.lbl_path = ttk.Label(devel)
        self.lbl_path["width"] = 50
        self.lbl_path.grid(row=r, column=0, columnspan=2, **cpadw)

        # Listbox
        r += 1
        trv = ttk.Frame(devel)
        trv.columnconfigure(0, weight=1)
        trv.grid(row=r, columnspan=2, sticky="we")
        scb_files = ttk.Scrollbar(trv)
        self.trv_files = ttk.Treeview(trv)
        self.trv_files.bind("<<TreeviewSelect>>", self.select_pathfiles)
        self.trv_files["height"] = 15
        self.trv_files["yscrollcommand"] = scb_files.set
        self.trv_files.grid(row=0, column=0, sticky="we")
        scb_files["command"] = self.trv_files.yview
        scb_files.grid(row=0, column=1, sticky="ns")

        # Uploadbutton
        r += 1
        btnlist = ttk.Frame(devel)
        btnlist.columnconfigure(1, weight=1)
        btnlist.grid(row=r, columnspan=2, sticky="we")

        self.btn_jobs = ttk.Button(btnlist)
        self.btn_jobs["command"] = self.btn_domyjob
        self.btn_jobs["text"] = _("Stop / Upload / Start")
        self.btn_jobs.grid(row=0, column=1, **cpadwe)

    def btn_domyjob(self):
        u"""Hochladen und neu starten."""

        # PLC Programm anhalten
        self.xmlcli.plcstop()

        # Aktuell konfiguriertes Programm lesen (für uploaded Flag)
        opt_program = self.xmlcli.get_config()
        opt_program = opt_program.get("plcprogram", "none.py")
        uploaded = True
        ec = 0

        for fname in self.watchfiles:

            # FIXME: Fehlerabfang bei Dateilesen
            with open(fname, "rb") as fh:

                # Ordnernamen vom System entfernen
                sendname = fname.replace(self.watchpath, "")[1:]

                # Prüfen ob Dateiname bereits als Startprogramm angegeben ist
                if sendname == opt_program:
                    uploaded = False

                # Datei übertragen
                try:
                    ustatus = self.xmlcli.plcupload(
                        Binary(gzip.compress(fh.read())), sendname
                    )
                except Exception:
                    ec = -2
                    break

                if not ustatus:
                    ec = -1
                    break

        if ec == 0:
            # Wenn eines der Dateien nicht das Hauptprogram ist, info
            if uploaded:
                tkmsg.showinfo(
                    _("Information"),
                    _("A PLC program has been uploaded. Please check the "
                        "PLC options to see if the correct program is "
                        "specified as the start program."),
                    parent=self.master
                )

        elif ec == -1:
            tkmsg.showerror(
                _("Error"),
                _("The Revolution Pi could not process some parts of the "
                    "transmission."),
                parent=self.master
            )

        elif ec == -2:
            tkmsg.showerror(
                _("Error"),
                _("Errors occurred during transmission"),
                parent=self.master
            )

        # PLC Programm starten
        self.xmlcli.plcstart()

    def btn_selectpath(self):
        u"""Lässt dem Benuzter ein Verzeichnis auswählen."""
        dirselect = tkfd.askdirectory(
            parent=self.master,
            title=_("Directory to watch"),
            mustexist=False,
            initialdir=self.watchpath
        )
        if not dirselect:
            return

        # Neuen Pfad übernehmen
        if os.path.exists(dirselect):
            self.pathselected = True
            self.watchpath = dirselect
            self.load_pathfiles()

        else:
            tkmsg.showerror(
                _("Error"),
                _("Can not open the selected folder."),
                parent=self.master
            )

        self.refresh_stats()

    def load_pathfiles(self, silent=False):
        u"""Aktualisiert die Dateiliste.
        @param silent Keinen Dialog anzeigen"""
        # Liste leeren
        self.trv_files.delete(*self.trv_files.get_children())

        # Dateiliste erstellen
        filecount = 0
        for tup_walk in os.walk(self.watchpath):
            for filename in sorted(tup_walk[2]):
                fullname = os.path.join(tup_walk[0], filename)
                self.trv_files.insert(
                    "", "end", fullname,
                    text=fullname.replace(self.watchpath, "")[1:],
                    values=fullname
                )

                # Dateiobergrenze
                filecount += 1
                if filecount >= 1000:
                    break

            if filecount >= 1000:
                if not silent:
                    tkmsg.showwarning(
                        _("Warning"),
                        _("Found more than 1000 files! Only 1000 files can be "
                            "shown in this dialog, all other will be ignored."
                            ""),
                        parent=self.master
                    )
                break

        # Alle Elemente für Selection prüfen und anwenden
        for watchfile in self.watchfiles.copy():
            try:
                self.trv_files.item(watchfile)
            except Exception:
                self.watchfiles.remove(watchfile)
        self.trv_files.selection_set(self.watchfiles)

    def select_pathfiles(self, tkevt):
        u"""Setzt state der Buttons."""
        self.watchfiles = list(self.trv_files.selection())
        self.refresh_stats()

    def refresh_stats(self):
        u"""Passt die Widgets an."""
        self.btn_jobs["state"] = "normal" if len(self.watchfiles) > 0 \
            else "disabled"
        self.lbl_path["text"] = self.watchpath


# Debugging
if __name__ == "__main__":
    from xmlrpc.client import ServerProxy
    cli = ServerProxy("http://localhost:55123")
    root = tkinter.Tk()
    app = RevPiDevelop(root, cli, 3, "debugging")
    app.mainloop()
