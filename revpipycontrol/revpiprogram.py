#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import gzip
import os
import pickle
import tarfile
import tkinter
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmsg
import zipfile
from mytools import gettrans
from os import environ
from os import makedirs
from shutil import rmtree
from sys import platform
from tempfile import mkstemp, mkdtemp
from xmlrpc.client import Binary

# Übersetzung laden
_ = gettrans()

# Systemwerte
if platform == "linux":
    homedir = environ["HOME"]
else:
    homedir = environ["APPDATA"]
savefile = os.path.join(homedir, ".revpipyplc", "programpath.dat")


class RevPiProgram(tkinter.Frame):

    def __init__(self, master, xmlcli, xmlmode, revpi):
        u"""Init RevPiProgram-Class.
        @return None"""
        if xmlmode < 2:
            return None

        super().__init__(master)
        self.master.protocol("WM_DELETE_WINDOW", self._checkclose)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.pack(expand=True, fill="both")

        self.uploaded = False
        self.revpi = revpi
        self.xmlcli = xmlcli
        self.xmlmode = xmlmode
        self.xmlstate = "normal" if xmlmode == 3 else "disabled"

        # Letzte Einstellungen übernehmen
        self.opt = self._loaddefault()

        # Fenster bauen
        self._createwidgets()

        self._evt_optdown()
        self._evt_optup()

    def _checkclose(self, event=None):
        u"""Prüft ob Fenster beendet werden soll.
        @param event tkinter-Event"""
        if self.uploaded:
            tkmsg.showinfo(
                _("Information"),
                _("A PLC program has been uploaded. Please check the "
                    "PLC options to see if the correct program is specified "
                    "as the start program."),
                parent=self.master
            )
        self.master.destroy()

    def _createwidgets(self):
        u"""Erstellt alle Widgets."""
        self.master.wm_title(_("RevPi Python PLC program"))
        self.master.wm_resizable(width=False, height=False)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        cpad = {"padx": 4, "pady": 2}
        # cpade = {"padx": 4, "pady": 2, "sticky": "e"}
        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}
        # cpadwe = {"padx": 4, "pady": 2, "sticky": "we"}

        # Gruppe Programm
        prog = tkinter.LabelFrame(self)
        prog.columnconfigure(0, weight=1)
        prog["text"] = _("PLC python program")
        prog.grid(columnspan=2, pady=2, sticky="we")

        # Variablen vorbereiten
        self.var_picdown = tkinter.BooleanVar(prog)
        self.var_picup = tkinter.BooleanVar(prog)
        self.var_cleanup = tkinter.BooleanVar(prog)
        self.var_typedown = tkinter.StringVar(prog)
        self.var_typeup = tkinter.StringVar(prog)

        self.lst_typedown = [_("Files"), _("Zip archive"), _("TGZ archive")]
        self.lst_typeup = [
            _("Files"), _("Folder"), _("Zip archive"), _("TGZ archive")
        ]
        self.var_picdown.set(self.opt.get("picdown", False))
        self.var_picup.set(self.opt.get("picup", False))

        # Gespeicherte Werte übernehmen
        saved_val = self.opt.get("typedown", self.lst_typedown[0])
        self.var_typedown.set(
            saved_val if saved_val in self.lst_typedown else _("Files")
        )
        saved_val = self.opt.get("typeup", self.lst_typeup[0])
        self.var_typeup.set(
            saved_val if saved_val in self.lst_typeup else _("Files")
        )

        r = 0
        lbl = tkinter.Label(prog)
        lbl["text"] = _("Download PLC program as:")
        lbl.grid(column=0, row=r, **cpadw)
        opt = tkinter.OptionMenu(
            prog, self.var_typedown, *self.lst_typedown,
            command=self._evt_optdown)
        opt["width"] = 10
        opt.grid(column=1, row=r, **cpad)

        r = 1
        self.ckb_picdown = tkinter.Checkbutton(prog)
        self.ckb_picdown["text"] = _("include piCtory configuration")
        self.ckb_picdown["variable"] = self.var_picdown
        self.ckb_picdown.grid(column=0, row=r, **cpadw)
        btn = tkinter.Button(prog)
        btn["command"] = self.plcdownload
        btn["text"] = _("Download")
        btn.grid(column=1, row=r, **cpad)

        r = 2
        lbl = tkinter.Label(prog)
        lbl["text"] = _("Upload PLC program as:")
        lbl.grid(column=0, row=r, **cpadw)
        opt = tkinter.OptionMenu(
            prog, self.var_typeup, *self.lst_typeup,
            command=self._evt_optup)
        opt["state"] = self.xmlstate
        opt["width"] = 10
        opt.grid(column=1, row=r, **cpad)

        r = 3
        ckb = tkinter.Checkbutton(prog)
        ckb["state"] = self.xmlstate
        ckb["text"] = _("clean upload folder before upload")
        ckb["variable"] = self.var_cleanup
        ckb.grid(column=0, row=r, columnspan=2, **cpadw)

        r = 4
        self.ckb_picup = tkinter.Checkbutton(prog)
        self.ckb_picup["state"] = self.xmlstate
        self.ckb_picup["text"] = _("includes piCtory configuration")
        self.ckb_picup["variable"] = self.var_picup
        self.ckb_picup.grid(column=0, row=r, **cpadw)
        btn = tkinter.Button(prog)
        btn["command"] = self.plcupload
        btn["state"] = self.xmlstate
        btn["text"] = _("Upload")
        btn.grid(column=1, row=r, **cpad)

        # Gruppe piCtory
        picto = tkinter.LabelFrame(self)
        picto.columnconfigure(0, weight=1)
        picto["text"] = _("piCtory configuration")
        picto.grid(columnspan=2, pady=2, sticky="we")

        lbl = tkinter.Label(picto)
        lbl["text"] = _("Download piCtory configuration")
        lbl.grid(column=0, row=0, **cpadw)
        btn = tkinter.Button(picto)
        btn["command"] = self.getpictoryrsc
        btn["text"] = _("Download")
        btn.grid(column=1, row=0, **cpad)
        lbl = tkinter.Label(picto)
        lbl["text"] = _("Upload piCtory configuration")
        lbl.grid(column=0, row=1, **cpadw)
        btn = tkinter.Button(picto)
        btn["command"] = self.setpictoryrsc
        btn["state"] = self.xmlstate
        btn["text"] = _("Upload")
        btn.grid(column=1, row=1, **cpad)

        # Gruppe ProcImg
        proc = tkinter.LabelFrame(self)
        proc.columnconfigure(0, weight=1)
        proc["text"] = _("piControl0 process image")
        proc.grid(columnspan=2, pady=2, sticky="we")
        lbl = tkinter.Label(proc)
        lbl["text"] = _("Download process image dump")
        lbl.grid(column=0, row=0, **cpadw)
        btn = tkinter.Button(proc)
        btn["command"] = self.getprocimg
        btn["text"] = _("Download")
        btn.grid(column=1, row=0, **cpad)

        # Gruppe piControlReset
        picon = tkinter.LabelFrame(self)
        picon.columnconfigure(0, weight=1)
        picon["text"] = _("Reset piControl")
        picon.grid(columnspan=2, pady=2, sticky="we")
        lbl = tkinter.Label(picon)
        lbl["text"] = _("Execute piControlReset")
        lbl.grid(column=0, row=0, **cpadw)
        btn = tkinter.Button(picon)
        btn["command"] = self.picontrolreset
        btn["text"] = _("execute")
        btn.grid(column=1, row=0, **cpad)

        # Beendenbutton
        btn = tkinter.Button(self)
        btn["command"] = self._checkclose
        btn["text"] = _("Exit")
        btn.grid()

    def _evt_optdown(self, text=""):
        u"""Passt je nach gewählter Option den Status der Widgets an."""
        if self.lst_typedown.index(self.var_typedown.get()) == 0:
            self.var_picdown.set(False)
            self.ckb_picdown["state"] = "disable"
        else:
            self.ckb_picdown["state"] = "normal"

    def _evt_optup(self, text=""):
        u"""Passt je nach gewählter Option den Status der Widgets an."""
        if self.lst_typeup.index(self.var_typeup.get()) <= 1:
            self.var_picup.set(False)
            self.ckb_picup["state"] = "disable"
        else:
            self.ckb_picup["state"] = "normal"

    def _loaddefault(self, full=False):
        u"""Übernimmt für den Pi die letzen Pfade.
        @param full Einstellungen für alle Verbindungen laden
        @return dict() mit Einstellungen"""
        if os.path.exists(savefile):
            fh = open(savefile, "rb")
            dict_all = pickle.load(fh)
            if full:
                return dict_all
            else:
                return dict_all.get(self.revpi, {})
        return {}

    def _savedefaults(self):
        u"""Schreibt fuer den Pi die letzen Pfade.
        @return True, bei erfolgreicher Verarbeitung"""
        try:
            makedirs(os.path.dirname(savefile), exist_ok=True)
            dict_all = self._loaddefault(full=True)
            dict_all[self.revpi] = self.opt
            fh = open(savefile, "wb")
            pickle.dump(dict_all, fh)
            self.changes = False
        except:
            return False
        return True

    def create_filelist(self, rootdir):
        u"""Erstellt eine Dateiliste von einem Verzeichnis.
        @param rootdir Verzeichnis fuer das eine Liste erstellt werden soll
        @return Dateiliste"""
        filelist = []
        for tup_dir in os.walk(rootdir):
            for fname in tup_dir[2]:
                filelist.append(os.path.join(tup_dir[0], fname))
        return filelist

    def check_replacedir(self, rootdir):
        """Gibt das rootdir von einem entpackten Verzeichnis zurueck.

        Dabei wird geprueft, ob es sich um einen einzelnen Ordner handelt
        und ob es eine piCtory Konfiguration im rootdir gibt.
        @param rootdir Verzeichnis fuer Pruefung
        @return Abgeaendertes rootdir

        """
        lst_dir = os.listdir(rootdir)
        if len(lst_dir) == 1 and \
                os.path.isdir(os.path.join(rootdir, lst_dir[0])):
            return (os.path.join(rootdir, lst_dir[0]), None)

        if len(lst_dir) == 2:
            rscfile = None
            for fname in lst_dir:
                if fname.find(".rsc"):
                    rscfile = os.path.join(rootdir, fname)
            return (os.path.join(rootdir, lst_dir[0]), rscfile)

        else:
            return (rootdir, None)

    def getpictoryrsc(self):
        u"""Läd die piCtory Konfiguration herunter."""
        fh = tkfd.asksaveasfile(
            mode="wb", parent=self.master,
            confirmoverwrite=True,
            title=_("Save as..."),
            initialdir=self.opt.get("getpictoryrsc_dir", ""),
            initialfile=self.revpi + ".rsc",
            filetypes=((_("piCtory config"), "*.rsc"), (_("All files"), "*.*"))
        )
        if fh is not None:
            try:
                fh.write(self.xmlcli.get_pictoryrsc().data)
            except:
                tkmsg.showerror(
                    _("Error"),
                    _("Could not load and save file!"),
                    parent=self.master,
                )
            else:
                tkmsg.showinfo(
                    _("Success"),
                    _("File successfully loaded and saved."),
                    parent=self.master
                )
                # Einstellungen speichern
                self.opt["getpictoryrsc_dir"] = os.path.dirname(fh.name)
                self._savedefaults()
            finally:
                fh.close()

    def getprocimg(self):
        u"""Läd das aktuelle Prozessabbild herunter."""
        fh = tkfd.asksaveasfile(
            mode="wb", parent=self.master,
            confirmoverwrite=True,
            title=_("Save as..."),
            initialdir=self.opt.get("getprocimg_dir", ""),
            initialfile=self.revpi + ".img",
            filetypes=((_("Imagefiles"), "*.img"), (_("All files"), "*.*"))
        )
        if fh is not None:
            try:
                fh.write(self.xmlcli.get_procimg().data)
            except:
                tkmsg.showerror(
                    _("Error"),
                    _("Could not load and save file!"),
                    parent=self.master
                )
            else:
                tkmsg.showinfo(
                    _("Success"),
                    _("File successfully loaded and saved."),
                    parent=self.master
                )
                # Einstellungen speichern
                self.opt["getprocimg_dir"] = os.path.dirname(fh.name)
                self._savedefaults()
            finally:
                fh.close()

    def setpictoryrsc(self, filename=None):
        u"""Überträgt die angegebene piCtory-Konfiguration."""
        if filename is None:
            fh = tkfd.askopenfile(
                mode="rb", parent=self.master,
                title=_("Open piCtory file..."),
                initialdir=self.opt.get("setpictoryrsc_dir", ""),
                initialfile=self.revpi + ".rsc",
                filetypes=(
                    (_("piCtory config"), "*.rsc"), (_("All files"), "*.*")
                )
            )
        else:
            fh = open(filename, "rb")

        if fh is not None:
            ask = tkmsg.askyesno(
                _("Question"),
                _("Should the piControl driver be reset after "
                    "uploading the piCtory configuration?"),
                parent=self.master
            )

            ec = self.xmlcli.set_pictoryrsc(Binary(fh.read()), ask)

            if ec == 0:
                if ask:
                    tkmsg.showinfo(
                        _("Success"),
                        _("The transfer of the piCtory configuration "
                            "and the reset of piControl have been "
                            "successfully executed."),
                        parent=self.master
                    )
                else:
                    tkmsg.showinfo(
                        _("Success"),
                        _("The piCtory configuration was "
                            "successfully transferred."),
                        parent=self.master
                    )

                # Einstellungen speichern
                self.opt["setpictoryrsc_dir"] = os.path.dirname(fh.name)
                self._savedefaults()
            elif ec == -1:
                tkmsg.showerror(
                    _("Error"),
                    _("Can not process the transferred file."),
                    parent=self.master
                )
            elif ec == -2:
                tkmsg.showerror(
                    _("Error"),
                    _("Can not find main elements in piCtory file."),
                    parent=self.master
                )
            elif ec == -4:
                tkmsg.showerror(
                    _("Error"),
                    _("Contained devices could not be found on Revolution "
                        "Pi. The configuration may be from a newer piCtory "
                        "version!"),
                    parent=self.master
                )
            elif ec == -5:
                tkmsg.showerror(
                    _("Error"),
                    _("Could not load RAP catalog on Revolution Pi."),
                    parent=self.master
                )
            elif ec < 0:
                tkmsg.showerror(
                    _("Error"),
                    _("The piCtory configuration could not be "
                        "written on the Revolution Pi."),
                    parent=self.master
                )
            elif ec > 0:
                tkmsg.showwarning(
                    _("Warning"),
                    _("The piCtroy configuration has been saved successfully."
                        " \nAn error occurred on piControl reset!"),
                    parent=self.master
                )

            fh.close()

    def picontrolreset(self):
        u"""Fürt ein Reset der piBridge durch."""
        ask = tkmsg.askyesno(
            _("Question"),
            _("Are you sure to reset piControl? \nThe process image "
                "and the piBridge are interrupted !!!"),
            parent=self.master
        )
        if ask:
            ec = self.xmlcli.resetpicontrol()
            if ec == 0:
                tkmsg.showinfo(
                    _("Success"),
                    _("piControl reset executed successfully"),
                    parent=self.master
                )
            else:
                tkmsg.showerror(
                    _("Error"),
                    _("piControl reset could not be executed successfully"),
                    parten=self.master
                )

    def plcdownload(self):
        u"""Läd das aktuelle Projekt herunter."""
        tdown = self.lst_typedown.index(self.var_typedown.get())
        fh = None
        dirselect = ""

        if tdown == 0:
            # Ordner
            dirselect = tkfd.askdirectory(
                parent=self.master,
                title=_("Directory to save"),
                mustexist=False,
                initialdir=self.opt.get("plcdownload_dir", self.revpi)
            )

            if type(dirselect) == str and dirselect != "":
                fh = open(mkstemp()[1], "wb")

        elif tdown == 1:
            # Zip
            fh = tkfd.asksaveasfile(
                mode="wb", parent=self.master,
                confirmoverwrite=True,
                title=_("Save as..."),
                initialdir=self.opt.get("plcdownload_file", ""),
                initialfile=self.revpi + ".zip",
                filetypes=(
                    (_("Zip archive"), "*.zip"), (_("All files"), "*.*")
                )
            )

        elif tdown == 2:
            # TarGz
            fh = tkfd.asksaveasfile(
                mode="wb", parent=self.master,
                confirmoverwrite=True,
                title=_("Save as..."),
                initialdir=self.opt.get("plcdownload_file", ""),
                initialfile=self.revpi + ".tar.gz",
                filetypes=(
                    (_("TGZ archive"), "*.tar.gz"), (_("All files"), "*.*")
                )
            )

        if fh is not None:
            if tdown == 1:
                plcfile = self.xmlcli.plcdownload(
                    "zip", self.var_picdown.get()
                )
            else:
                plcfile = self.xmlcli.plcdownload(
                    "tar", self.var_picdown.get()
                )

            try:
                fh.write(plcfile.data)
                # Optional entpacken
                if tdown == 0:
                    fh.close()
                    os.makedirs(dirselect, exist_ok=True)
                    fh_pack = tarfile.open(fh.name)

                    # Unterverzeichnis streichen
                    for taritem in fh_pack.getmembers():
                        if not taritem.name == "revpipyload":
                            taritem.name = \
                                taritem.name.replace("revpipyload/", "")
                            fh_pack.extract(taritem, dirselect)

                    fh_pack.close()
                    self.opt["plcdownload_dir"] = dirselect
                else:
                    self.opt["plcdownload_file"] = os.path.dirname(fh.name)
                self.opt["typedown"] = self.var_typedown.get()
                self.opt["picdown"] = self.var_picdown.get()

            except:
                raise
                tkmsg.showerror(
                    _("Error"),
                    _("Could not load and save file!"),
                    parent=self.master
                )
            else:
                tkmsg.showinfo(
                    _("Success"),
                    _("File successfully loaded and saved."),
                    parent=self.master
                )

                # Einstellungen speichern
                self._savedefaults()
            finally:
                fh.close()

    def plcupload(self):
        u"""Lädt das angegebene Projekt auf den RevPi.
        @return True, bei erfolgreicher Verarbeitung"""
        tup = self.lst_typeup.index(self.var_typeup.get())
        dirselect = ""
        dirtmp = None
        filelist = []
        fileselect = None
        rscfile = None

        if tup == 0:
            # Datei
            fileselect = tkfd.askopenfilenames(
                parent=self.master,
                title="Upload Python program...",
                initialdir=self.opt.get("plcupload_dir", ""),
                filetypes=(("Python", "*.py"), (_("All files"), "*.*"))
            )
            if type(fileselect) == tuple and len(fileselect) > 0:
                for file in fileselect:
                    filelist.append(file)

        elif tup == 1:
            # Ordner
            dirselect = tkfd.askdirectory(
                parent=self.master,
                title=_("Folder to upload"),
                mustexist=True,
                initialdir=self.opt.get("plcupload_dir", self.revpi)
            )
            if type(dirselect) == str and dirselect != "":
                filelist = self.create_filelist(dirselect)

        elif tup == 2:
            # Zip
            fileselect = tkfd.askopenfilename(
                parent=self.master,
                title=_("Upload Zip archive..."),
                initialdir=self.opt.get("plcupload_file", ""),
                initialfile=self.revpi + ".zip",
                filetypes=(
                    (_("Zip archive"), "*.zip"), (_("All files"), "*.*")
                )
            )
            if type(fileselect) == str and fileselect != "":
                # Zipdatei prüfen
                if zipfile.is_zipfile(fileselect):
                    dirtmp = mkdtemp()
                    fhz = zipfile.ZipFile(fileselect)
                    fhz.extractall(dirtmp)
                    fhz.close()

                    filelist = self.create_filelist(dirtmp)
                    dirselect, rscfile = self.check_replacedir(dirtmp)

                else:
                    tkmsg.showerror(
                        _("Error"),
                        _("The specified file is not a ZIP archive."),
                        parent=self.master
                    )
                    return False

        elif tup == 3:
            # TarGz
            fileselect = tkfd.askopenfilename(
                parent=self.master,
                title=_("Upload TarGz archiv..."),
                initialdir=self.opt.get("plcupload_file", ""),
                initialfile=self.revpi + ".tar.gz",
                filetypes=(
                    (_("TGZ archive"), "*.tar.gz"), (_("All files"), "*.*")
                )
            )
            if type(fileselect) == str and fileselect != "":

                # Tar-Datei prüfen
                if tarfile.is_tarfile(fileselect):
                    dirtmp = mkdtemp()
                    fht = tarfile.open(fileselect)
                    fht.extractall(dirtmp)
                    fht.close()

                    filelist = self.create_filelist(dirtmp)
                    dirselect, rscfile = self.check_replacedir(dirtmp)

                else:
                    tkmsg.showerror(
                        _("Error"),
                        _("The specified file is not a TAR archive."),
                        parent=self.master
                    )
                    return False

        # Wenn keine Dateien gewählt
        if len(filelist) == 0:
            return True

        # Vor Übertragung aufräumen wenn ausgewählt
        if self.var_cleanup.get() and not self.xmlcli.plcuploadclean():
            tkmsg.showerror(
                _("Error"),
                _("There was an error deleting the files on the "
                    "Revolution Pi."),
                parent=self.master
            )
            return False

        # Aktuell konfiguriertes Programm lesen (für uploaded Flag)
        opt_program = self.xmlcli.get_config()
        opt_program = opt_program.get("plcprogram", "none.py")
        self.uploaded = True
        ec = 0

        for fname in filelist:

            if fname == rscfile:
                continue

            # FIXME: Fehlerabfang bei Dateilesen
            with open(fname, "rb") as fh:

                # Dateinamen ermitteln
                if dirselect == "":
                    sendname = os.path.basename(fname)
                else:
                    sendname = fname.replace(dirselect, "")[1:]

                # Prüfen ob Dateiname bereits als Startprogramm angegeben ist
                if sendname == opt_program:
                    self.uploaded = False

                # Datei übertragen
                try:
                    ustatus = self.xmlcli.plcupload(
                        Binary(gzip.compress(fh.read())), sendname)
                except:
                    ec = -2
                    break

                if not ustatus:
                    ec = -1
                    break

        if ec == 0:
            tkmsg.showinfo(
                _("Success"),
                _("The PLC program was transferred successfully."),
                parent=self.master
            )

            if self.var_picup.get():
                if rscfile is not None:
                    self.setpictoryrsc(rscfile)
                else:
                    tkmsg.showerror(
                        _("Error"),
                        _("There is no piCtory configuration in this "
                            "archive."),
                        parent=self.master
                    )

            # Einstellungen speichern
            if tup == 0:
                self.opt["plcupload_dir"] = os.path.dirname(fileselect[0])
            elif tup == 1:
                self.opt["plcupload_dir"] = dirselect
            else:
                self.opt["plcupload_file"] = os.path.dirname(fileselect)

            self.opt["typeup"] = self.var_typeup.get()
            self.opt["picup"] = self.var_picup.get()
            self._savedefaults()

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

        # Temp-Dir aufräumen
        if dirtmp is not None:
            rmtree(dirtmp)

        return True
