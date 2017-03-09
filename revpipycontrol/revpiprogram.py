#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import tarfile
import tkinter
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmsg
from os import makedirs
from tempfile import mktemp
from xmlrpc.client import Binary


class RevPiProgram(tkinter.Frame):

    def __init__(self, master, xmlcli, revpi):
        super().__init__(master)
#        master.protocol("WM_DELETE_WINDOW", self._checkclose)
        self.pack(expand=True, fill="both")

        self.uploaded = False
        self.revpi = revpi
        self.xmlcli = xmlcli

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
        cpade = {"padx": 4, "pady": 2, "sticky": "e"}
        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}
        cpadwe = {"padx": 4, "pady": 2, "sticky": "we"}

        # Gruppe Programm
        prog = tkinter.LabelFrame(self)
        prog.columnconfigure(0, weight=1)
        prog["text"] = "PLC Pythonprogramm"
        prog.grid(columnspan=2, pady=2, sticky="we")

        # Variablen vorbereiten
        self.var_picdown = tkinter.BooleanVar(prog)
        self.var_picup = tkinter.BooleanVar(prog)
        self.var_cleanup = tkinter.BooleanVar(prog)
        self.var_typedown = tkinter.StringVar(prog)
        self.var_typeup = tkinter.StringVar(prog)

        self.lst_typedown = ["Dateien", "Zip Archiv", "TGZ Archiv"]
        self.lst_typeup = ["Datei", "Ordner", "Zip Archiv", "TGZ Archiv"]
        self.var_typedown.set(self.lst_typedown[0])
        self.var_typeup.set(self.lst_typeup[0])

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
        opt["width"] = 10
        opt.grid(column=1, row=r, **cpad)

        r = 3
        self.ckb_picup = tkinter.Checkbutton(prog)
        self.ckb_picup["text"] = "enthält piCtory Konfiguration"
        self.ckb_picup["variable"] = self.var_picup
        self.ckb_picup.grid(column=0, row=r, **cpadw)
        btn = tkinter.Button(prog)
        btn["command"] = self.plcupload
        btn["text"] = "Upload"
        btn.grid(column=1, row=r, **cpad)

        r = 4
        ckb = tkinter.Checkbutton(prog)
        ckb["text"] = "vorher alles im Uploadverzeichnis löschen"
        ckb["variable"] = self.var_cleanup
        ckb.grid(column=0, row=r, columnspan=2, **cpadw)

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
        btn["text"] = "Upload"
        btn.grid(column=1, row=1, **cpad)

        # Gruppe ProcImg
        proc = tkinter.LabelFrame(self)
        proc.columnconfigure(0, weight=1)
        proc["text"] = "piControl0 Prozessabbild"
        proc.grid(columnspan=2, pady=2, sticky="we")
        lbl = tkinter.Label(proc)
        lbl["text"] = "Prozessabbild herunterladen"
        lbl.grid(column=0, row=0, **cpadw)
        btn = tkinter.Button(proc)
        btn["command"] = self.getprocimg
        btn["text"] = "Download"
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
        if self.lst_typeup.index(self.var_typeup.get()) == 0:
            self.var_picup.set(False)
            self.ckb_picup["state"] = "disable"
        else:
            self.ckb_picup["state"] = "normal"

    def getpictoryrsc(self):
        fh = tkfd.asksaveasfile(
            mode="wb", parent=self.master,
            confirmoverwrite=True,
            title="Speichern als...",
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
            finally:
                fh.close()

    def getprocimg(self):
        fh = tkfd.asksaveasfile(
            mode="wb", parent=self.master,
            confirmoverwrite=True,
            title="Speichern als...",
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
            finally:
                fh.close()

    def setpictoryrsc(self):
        print("setpictoryrsc")
        fh = tkfd.askopenfile(
            mode="rb", parent=self.master,
            title="piCtory Datei öffnen...",
            initialfile=self.revpi + ".rsc",
            filetypes=(("piCtory Config", "*.rsc"), ("All Files", "*.*"))
        )
        if fh is not None:
            # TODO: Test, ob es wirklich piCtory ist

            ask = tkmsg.askyesno(
                parent=self.master, title="Frage",
                message="Soll nach dem Hochladen ein reset am piControl "
                "Treiber durchgeführt werden?",
            )

            ec = self.xmlcli.set_pictoryrsc(Binary(fh.read()), ask)
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

    def plcdownload(self):
        tdown = self.lst_typedown.index(self.var_typedown.get())
        fh = None
        dir = ""

        if tdown == 0:
            # Ordner
            dir = tkfd.askdirectory(
                parent=self.master, title="Verzeichnis zum Ablegen",
                mustexist=False, initialdir=self.revpi)

            if type(dir) == str and dir != "":
                fh = open(mktemp(), "wb")

        elif tdown == 1:
            # Zip
            fh = tkfd.asksaveasfile(
                mode="wb", parent=self.master,
                confirmoverwrite=True,
                title="Speichern als...",
                initialfile=self.revpi + ".zip",
                filetypes=(("Zip Archiv", "*.zip"), ("All Files", "*.*"))
            )

        elif tdown == 2:
            # TarGz
            fh = tkfd.asksaveasfile(
                mode="wb", parent=self.master,
                confirmoverwrite=True,
                title="Speichern als...",
                initialfile=self.revpi + ".tar.gz",
                filetypes=(("Tar Archiv", "*.tar.gz"), ("All Files", "*.*"))
            )

        if fh is not None:
            if tdown == 1:
                plcfile = self.xmlcli.plcdownload("zip")
            else:
                plcfile = self.xmlcli.plcdownload("tar")

            try:
                fh.write(plcfile.data)
                # Optional entpacken
                if tdown == 0:
                    fh.close()
                    makedirs(dir, exist_ok=True)
                    fh_pack = tarfile.open(fh.name)
                    fh_pack.extractall(dir)
                    fh_pack.close()

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
            finally:
                fh.close()

        print("plcdownload", tdown)

    def plcupload(self):
        tup = self.lst_typeup.index(self.var_typeup.get())

        print("plcupload", tup)
        self.uploaded = True


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiProgram(root, None, "test")
    root.mainloop()
