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
from os import environ
from os import makedirs
from shutil import rmtree
from sys import platform
from tempfile import mkstemp, mkdtemp
from xmlrpc.client import Binary


# Systemwerte
if platform == "linux":
    homedir = environ["HOME"]
else:
    homedir = environ["APPDATA"]
savefile = os.path.join(homedir, ".revpipyplc", "programpath.dat")


class RevPiProgram(tkinter.Frame):

    def __init__(self, master, xmlcli, xmlmode, revpi):
        u"""Init RevPiProgram-Class."""
        if xmlmode < 2:
            return None

        super().__init__(master)
#        master.protocol("WM_DELETE_WINDOW", self._checkclose)
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

#    def _checkclose(self):
#        if self.uploaded:
#            tkmsg.showinfo("Ein PLC Programm wurde hochgeladen. "
#            "Bitte die PLC options prüfen ob dort das neue Programm"
#            "eingestellt werden muss.")
#        self.master.destroy()

    def _createwidgets(self):
        self.master.wm_title("RevPi Python PLC Programm")
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
        prog["text"] = "PLC Python programm"
        prog.grid(columnspan=2, pady=2, sticky="we")

        # Variablen vorbereiten
        self.var_picdown = tkinter.BooleanVar(prog)
        self.var_picup = tkinter.BooleanVar(prog)
        self.var_cleanup = tkinter.BooleanVar(prog)
        self.var_typedown = tkinter.StringVar(prog)
        self.var_typeup = tkinter.StringVar(prog)

        self.lst_typedown = ["Dateien", "Zip Archiv", "TGZ Archiv"]
        self.lst_typeup = ["Dateien", "Ordner", "Zip Archiv", "TGZ Archiv"]
        self.var_picdown.set(self.opt.get("picdown", False))
        self.var_picup.set(self.opt.get("picup", False))
        self.var_typedown.set(self.opt.get("typedown", self.lst_typedown[0]))
        self.var_typeup.set(self.opt.get("typeup", self.lst_typeup[0]))

        r = 0
        lbl = tkinter.Label(prog)
        lbl["text"] = "PLC Programm herunterladen als:"
        lbl.grid(column=0, row=r, **cpadw)
        opt = tkinter.OptionMenu(
            prog, self.var_typedown, *self.lst_typedown,
            command=self._evt_optdown)
        opt["width"] = 10
        opt.grid(column=1, row=r, **cpad)

        r = 1
        self.ckb_picdown = tkinter.Checkbutton(prog)
        self.ckb_picdown["text"] = "inkl. piCtory Konfiguration"
        self.ckb_picdown["variable"] = self.var_picdown
        self.ckb_picdown.grid(column=0, row=r, **cpadw)
        btn = tkinter.Button(prog)
        btn["command"] = self.plcdownload
        btn["text"] = "Download"
        btn.grid(column=1, row=r, **cpad)

        r = 2
        lbl = tkinter.Label(prog)
        lbl["text"] = "PLC Programm hochladen als:"
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
        ckb["text"] = "vorher alles im Uploadverzeichnis löschen"
        ckb["variable"] = self.var_cleanup
        ckb.grid(column=0, row=r, columnspan=2, **cpadw)

        r = 4
        self.ckb_picup = tkinter.Checkbutton(prog)
        self.ckb_picup["state"] = self.xmlstate
        self.ckb_picup["text"] = "enthält piCtory Konfiguration"
        self.ckb_picup["variable"] = self.var_picup
        self.ckb_picup.grid(column=0, row=r, **cpadw)
        btn = tkinter.Button(prog)
        btn["command"] = self.plcupload
        btn["state"] = self.xmlstate
        btn["text"] = "Upload"
        btn.grid(column=1, row=r, **cpad)

        # Gruppe piCtory
        picto = tkinter.LabelFrame(self)
        picto.columnconfigure(0, weight=1)
        picto["text"] = "piCtory Konfiguration"
        picto.grid(columnspan=2, pady=2, sticky="we")

        lbl = tkinter.Label(picto)
        lbl["text"] = "piCtory Konfiguration herunterladen"
        lbl.grid(column=0, row=0, **cpadw)
        btn = tkinter.Button(picto)
        btn["command"] = self.getpictoryrsc
        btn["text"] = "Download"
        btn.grid(column=1, row=0, **cpad)
        lbl = tkinter.Label(picto)
        lbl["text"] = "piCtory Konfiguration hochladen"
        lbl.grid(column=0, row=1, **cpadw)
        btn = tkinter.Button(picto)
        btn["command"] = self.setpictoryrsc
        btn["state"] = self.xmlstate
        btn["text"] = "Upload"
        btn.grid(column=1, row=1, **cpad)

        # Gruppe ProcImg
        proc = tkinter.LabelFrame(self)
        proc.columnconfigure(0, weight=1)
        proc["text"] = "piControl0 Prozessabbild"
        proc.grid(columnspan=2, pady=2, sticky="we")
        lbl = tkinter.Label(proc)
        lbl["text"] = "Prozessabbild-Dump herunterladen"
        lbl.grid(column=0, row=0, **cpadw)
        btn = tkinter.Button(proc)
        btn["command"] = self.getprocimg
        btn["text"] = "Download"
        btn.grid(column=1, row=0, **cpad)

        # Gruppe piControlReset
        picon = tkinter.LabelFrame(self)
        picon.columnconfigure(0, weight=1)
        picon["text"] = "piControl Reset"
        picon.grid(columnspan=2, pady=2, sticky="we")
        lbl = tkinter.Label(picon)
        lbl["text"] = "piControlReset ausführen"
        lbl.grid(column=0, row=0, **cpadw)
        btn = tkinter.Button(picon)
        btn["command"] = self.picontrolreset
        btn["text"] = "ausführen"
        btn.grid(column=1, row=0, **cpad)

        # Beendenbutton
        btn = tkinter.Button(self)
        btn["command"] = self.master.destroy
        btn["text"] = "Beenden"
        btn.grid()

    def _evt_optdown(self, text=""):
        if self.lst_typedown.index(self.var_typedown.get()) == 0:
            self.var_picdown.set(False)
            self.ckb_picdown["state"] = "disable"
        else:
            self.ckb_picdown["state"] = "normal"

    def _evt_optup(self, text=""):
        if self.lst_typeup.index(self.var_typeup.get()) <= 1:
            self.var_picup.set(False)
            self.ckb_picup["state"] = "disable"
        else:
            self.ckb_picup["state"] = "normal"

    def _loaddefault(self, full=False):
        """Uebernimmt fuer den Pi die letzen Pfade."""
        if os.path.exists(savefile):
            fh = open(savefile, "rb")
            dict_all = pickle.load(fh)
            if full:
                return dict_all
            else:
                return dict_all.get(self.revpi, {})
        return {}

    def _savedefaults(self):
        u"""Schreibt fuer den Pi die letzen Pfade."""
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
        @param rootdir: Verzeichnis fuer das eine Liste erstellt werden soll
        @returns: Dateiliste"""
        filelist = []
        for tup_dir in os.walk(rootdir):
            for fname in tup_dir[2]:
                filelist.append(os.path.join(tup_dir[0], fname))
        return filelist

    def check_replacedir(self, rootdir):
        """Gibt das rootdir von einem entpackten Verzeichnis zurueck.

        Dabei wird geprueft, ob es sich um einen einzelnen Ordner handelt
        und ob es eine piCtory Konfiguration im rootdir gibt.
        @param rootdir: Verzeichnis fuer Pruefung
        @returns: Abgeaendertes rootdir

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
            title="Speichern als...",
            initialdir=self.opt.get("getpictoryrsc_dir", ""),
            initialfile=self.revpi + ".rsc",
            filetypes=(("piCtory Config", "*.rsc"), ("All Files", "*.*"))
        )
        if fh is not None:
            try:
                fh.write(self.xmlcli.get_pictoryrsc().data)
            except:
                tkmsg.showerror(
                    parent=self.master, title="Fehler",
                    message="Datei konnte nicht geladen und gespeichert "
                    "werden!"
                )
            else:
                tkmsg.showinfo(
                    parent=self.master, title="Erfolgreich",
                    message="Datei erfolgreich vom Revolution Pi geladen "
                    "und gespeichert.",
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
            title="Speichern als...",
            initialdir=self.opt.get("getprocimg_dir", ""),
            initialfile=self.revpi + ".img",
            filetypes=(("Imagefiles", "*.img"), ("All Files", "*.*"))
        )
        if fh is not None:
            try:
                fh.write(self.xmlcli.get_procimg().data)
            except:
                tkmsg.showerror(
                    parent=self.master, title="Fehler",
                    message="Datei konnte nicht geladen und gespeichert"
                    "werden!"
                )
            else:
                tkmsg.showinfo(
                    parent=self.master, title="Erfolgreich",
                    message="Datei erfolgreich vom Revolution Pi geladen "
                    "und gespeichert.",
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
                title="piCtory Datei öffnen...",
                initialdir=self.opt.get("setpictoryrsc_dir", ""),
                initialfile=self.revpi + ".rsc",
                filetypes=(("piCtory Config", "*.rsc"), ("All Files", "*.*"))
            )
        else:
            fh = open(filename, "rb")

        if fh is not None:
            ask = tkmsg.askyesno(
                parent=self.master, title="Frage",
                message="Soll nach dem Hochladen der piCtory Konfiguration "
                "ein Reset am piControl Treiber durchgeführt werden?"
            )

            ec = self.xmlcli.set_pictoryrsc(Binary(fh.read()), ask)
            print(ec)
            if ec == 0:
                if ask:
                    tkmsg.showinfo(
                        parent=self.master, title="Erfolgreich",
                        message="Die Übertragung der piCtory Konfiguration "
                        "und der Reset von piControl wurden erfolgreich "
                        "ausgeführt")
                else:
                    tkmsg.showinfo(
                        parent=self.master, title="Erfolgreich",
                        message="Die Übertragung der piCtory Konfiguration "
                        "wurde erfolgreich ausgeführt")

                # Einstellungen speichern
                self.opt["setpictoryrsc_dir"] = os.path.dirname(fh.name)
                self._savedefaults()
            elif ec < 0:
                tkmsg.showerror(
                    parent=self.master, title="Fehler",
                    message="Die piCtory Konfiguration konnte auf dem "
                    "Revolution Pi nicht geschrieben werden.")
            elif ec > 0:
                tkmsg.showwarning(
                    parent=self.master, title="Warnung",
                    message="Die piCtroy Konfiguration wurde erfolgreich "
                    "gespeichert. \nBeim piControl Reset trat allerdings ein "
                    "Fehler auf!")

            fh.close()

    def picontrolreset(self):
        u"""Fürt ein Reset der piBridge durch."""
        ask = tkmsg.askyesno(
            parent=self.master, title="Frage...",
            message="Soll piControlReset wirklich durchgeführt werden? \n"
            "Das Prozessabbild und die Steuerung werden dann unterbrochen!!!"
        )
        if ask:
            ec = self.xmlcli.resetpicontrol()
            if ec == 0:
                tkmsg.showinfo(
                    parent=self.master, title="Erfolgreich",
                    message="piControlReset erfolgreich durchgeführt"
                )
            else:
                tkmsg.showerror(
                    parten=self.master, title="Fehler",
                    message="piControlReset konnte nicht erfolgreich "
                    "durchgeführt werden"
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
                title="Verzeichnis zum Ablegen",
                mustexist=False,
                initialdir=self.opt.get("plcdownload_dir", self.revpi)
            )

            if type(dirselect) == str and dirselect != "":
                fh = open(mkstemp(), "wb")

        elif tdown == 1:
            # Zip
            fh = tkfd.asksaveasfile(
                mode="wb", parent=self.master,
                confirmoverwrite=True,
                title="Speichern als...",
                initialdir=self.opt.get("plcdownload_file", ""),
                initialfile=self.revpi + ".zip",
                filetypes=(("Zip Archiv", "*.zip"), ("All Files", "*.*"))
            )

        elif tdown == 2:
            # TarGz
            fh = tkfd.asksaveasfile(
                mode="wb", parent=self.master,
                confirmoverwrite=True,
                title="Speichern als...",
                initialdir=self.opt.get("plcdownload_file", ""),
                initialfile=self.revpi + ".tar.gz",
                filetypes=(("Tar Archiv", "*.tar.gz"), ("All Files", "*.*"))
            )

        if fh is not None:
            if tdown == 1:
                plcfile = self.xmlcli.plcdownload(
                    "zip", self.var_picdown.get())
            else:
                plcfile = self.xmlcli.plcdownload(
                    "tar", self.var_picdown.get())

            try:
                fh.write(plcfile.data)
                # Optional entpacken
                if tdown == 0:
                    fh.close()
                    os.makedirs(dirselect, exist_ok=True)
                    fh_pack = tarfile.open(fh.name)

                    # Unterverzeichnis streichen
                    rootname = ""
                    for taritem in fh_pack.getmembers():
                        print(rootname)
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
                    parent=self.master, title="Fehler",
                    message="Datei konnte nicht geladen und gespeichert "
                    "werden!"
                )
            else:
                tkmsg.showinfo(
                    parent=self.master, title="Erfolgreich",
                    message="Datei erfolgreich vom Revolution Pi geladen "
                    "und gespeichert.",
                )

                # Einstellungen speichern
                self._savedefaults()
            finally:
                fh.close()

    def plcupload(self):
        u"""Lädt das angegebene Projekt auf den RevPi."""
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
                title="Python Programm übertragen...",
                initialdir=self.opt.get("plcupload_dir", ""),
                filetypes=(("Python", "*.py"), ("All Files", "*.*"))
            )
            if type(fileselect) == tuple and len(fileselect) > 0:
                for file in fileselect:
                    filelist.append(file)

        elif tup == 1:
            # Ordner
            dirselect = tkfd.askdirectory(
                parent=self.master,
                title="Verzeichnis zum Hochladen",
                mustexist=True,
                initialdir=self.opt.get("plcupload_dir", self.revpi)
            )
            if type(dirselect) == str and dirselect != "":
                filelist = self.create_filelist(dirselect)

        elif tup == 2:
            # Zip
            fileselect = tkfd.askopenfilename(
                parent=self.master,
                title="Zip-Archive übertragen...",
                initialdir=self.opt.get("plcupload_file", ""),
                initialfile=self.revpi + ".zip",
                filetypes=(("Zip Archiv", "*.zip"), ("All Files", "*.*"))
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
                        parent=self.master, title="Fehler",
                        message="Die angegebene Datei ist kein ZIP-Archiv.")
                    return False

        elif tup == 3:
            # TarGz
            fileselect = tkfd.askopenfilename(
                parent=self.master,
                title="TarGz-Archiv übertragen...",
                initialdir=self.opt.get("plcupload_file", ""),
                initialfile=self.revpi + ".tar.gz",
                filetypes=(("Tar Archiv", "*.tar.gz"), ("All Files", "*.*"))
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
                        parent=self.master, title="Fehler",
                        message="Die angegebene Datei ist kein TAR-Archiv.")
                    return False

        # Wenn keine Dateien gewählt
        if len(filelist) == 0:
            return True

        # Vor Übertragung aufräumen wenn ausgewählt
        if self.var_cleanup.get() and not self.xmlcli.plcuploadclean():
            tkmsg.showerror(
                parent=self.masger, title="Fehler",
                message="Beim Löschen der Dateien auf dem Revolution Pi ist "
                "ein Fehler aufgetreten.")
            return False

        # Flag setzen, weil ab hier Veränderungen existieren
        self.uploaded = True
        ec = 0

        for fname in filelist:

            if fname == rscfile:
                continue

            # TODO: Fehlerabfang bei Dateilesen
            with open(fname, "rb") as fh:

                # Dateinamen ermitteln
                if dirselect == "":
                    sendname = os.path.basename(fname)
                else:
                    sendname = fname.replace(dirselect, "")[1:]

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
                parent=self.master, title="Erfolgreich",
                message="Die Übertragung war erfolgreich.")

            if self.var_picup.get():
                if rscfile is not None:
                    self.setpictoryrsc(rscfile)
                else:
                    tkmsg.showerror(
                        parent=self.master, title="Fehler",
                        message="Es wurde im Archiv keine piCtory "
                        "Konfiguration gefunden")

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
                parent=self.master, title="Fehler",
                message="Der Revoluton Pi konnte Teile der Übertragung nicht "
                "verarbeiten.")

        elif ec == -2:
            tkmsg.showerror(
                parent=self.master, title="Fehler",
                message="Bei der Übertragung traten Fehler auf")

        # Temp-Dir aufräumen
        if dirtmp is not None:
            rmtree(dirtmp)


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiProgram(root, None, "test")
    root.mainloop()
