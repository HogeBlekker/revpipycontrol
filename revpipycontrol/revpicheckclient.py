#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# Thranks to: http://stackoverflow.com/questions/3085696/adding-a-
# scrollbar-to-a-group-of-widgets-in-tkinter

import pickle
import tkinter
from threading import Lock
from xmlrpc.client import ServerProxy


class RevPiCheckClient(tkinter.Frame):

    def __init__(self, master, xmlcli, xmlmode=0):
        """Instantiiert MyApp-Klasse."""
        super().__init__(master)
        self.pack(fill="both", expand=True)

        # XML-Daten abrufen
        self.xmlmode = xmlmode
        self.cli = xmlcli
        self.cli.psstart()
        self.lst_devices = self.cli.ps_devices()
        self.dict_inps = pickle.loads(self.cli.ps_inps().data)
        self.dict_outs = pickle.loads(self.cli.ps_outs().data)

        self.lk = Lock()

        self.autorw = tkinter.BooleanVar()
        self.dowrite = tkinter.BooleanVar()

        # Fenster aufbauen
        self._createwidgets()

        # Aktuelle Werte einlesen
        self.readvalues()

    def onfrmconf(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _createiogroup(self, device, frame, iotype):
        """Erstellt IO-Gruppen."""
        # IOs generieren
        canvas = tkinter.Canvas(frame, borderwidth=0, width=180, heigh=800)
        s_frame = tkinter.Frame(canvas)
        vsb = tkinter.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        canvas.create_window((4, 4), window=s_frame, anchor="nw")
        s_frame.bind(
            "<Configure>", lambda event, canvas=canvas: self.onfrmconf(canvas)
        )

        rowcount = 0

        if iotype == "inp":
            lst_io = self.dict_inps[device]
        else:
            lst_io = self.dict_outs[device]

        for io in lst_io:
            # io = [name,bytelen,byteaddr,bmk,bitaddress,(tkinter_var)]

            tkinter.Label(s_frame, text=io[0]).grid(
                column=0, row=rowcount, sticky="w"
            )

            if io[4] >= 0:
                var = tkinter.BooleanVar()
                check = tkinter.Checkbutton(s_frame)
                check["command"] = \
                    lambda device=device, io=io: self.chval(device, io)
                check["state"] = "disabled" if iotype == "inp" else "normal"
                check["text"] = ""
                check["variable"] = var
                check.grid(column=1, row=rowcount)
            else:
                var = tkinter.IntVar()
                # FIXME: Mehrere Bytes möglich
                txt = tkinter.Spinbox(s_frame, to=255 * io[1])
                txt["command"] = \
                    lambda device=device, io=io: self.chval(device, io)
                txt["state"] = "disabled" if iotype == "inp" else "normal"
                txt["width"] = 4
                txt["textvariable"] = var
                txt.grid(column=1, row=rowcount)

            # Steuerelementvariable in IO übernehmen
            io.append(var)

            rowcount += 1

    def __hidewin(self, win, event=None):
        win.withdraw()

    def __showwin(self, win):
        if win.winfo_viewable():
            win.withdraw()
        else:
            win.deiconify()

    def _createwidgets(self):
        """Erstellt den Fensterinhalt."""
        # Hauptfenster
        self.master.wm_title("RevPi Onlineview")

        devgrp = tkinter.LabelFrame(self)
        devgrp["text"] = "Devices of RevPi"
        devgrp.pack(fill="y", side="left")

        for dev in self.lst_devices:
            win = tkinter.Toplevel(self)
            win.wm_title(dev[1])
            win.protocol(
                "WM_DELETE_WINDOW",
                lambda win=win: self.__hidewin(win)
            )
            win.withdraw()

            # Devicegruppe erstellen
            group = tkinter.LabelFrame(win)
            group["text"] = dev[1]
            group.pack(side="left", fill="both", expand=True)

            for iotype in ["inp", "out"]:
                frame = tkinter.Frame(group)
                frame.pack(side="left", fill="both", expand=True)
                self._createiogroup(dev[0], frame, iotype)

            # Button erstellen
            btn = tkinter.Button(devgrp)
            btn["command"] = lambda win=win: self.__showwin(win)
            btn["text"] = dev[1]
            btn.pack(fill="x", padx=10, pady=5)

        # Steuerungsfunktionen
        cntgrp = tkinter.LabelFrame(self)
        cntgrp["text"] = "Control"
        cntgrp.pack(fill="y", side="right")

        self.btn_read = tkinter.Button(cntgrp)
        self.btn_read["text"] = "LESEN"
        self.btn_read["command"] = self.readvalues
        self.btn_read.pack(fill="x")

        check = tkinter.Checkbutton(cntgrp)
        check["command"] = self.toggleauto
        check["text"] = "autorefresh processimage"
        check["variable"] = self.autorw
        check.pack(anchor="w")

        check = tkinter.Checkbutton(cntgrp)
        check["state"] = "disabled" if self.xmlmode < 3 else "normal"
        check["text"] = "write values to processimage"
        check["variable"] = self.dowrite
        check.pack(anchor="w")

    def chval(self, device, io):
        if self.dowrite.get():
            with self.lk:
                self.cli.ps_setvalue(device, io[0], io[5].get())

            # Alles neu einlesen wenn nicht AutoRW aktiv ist
            if not self.autorw.get():
                self.readvalues()

    def _readvalues(self):
        """Alle Werte der Inputs und Outputs abrufen."""

        # Werte abrufen
        with self.lk:
            ba_values = bytearray(self.cli.ps_values().data)

        for dev in self.lst_devices:
            # io = [name,bytelen,byteaddr,bmk,bitaddress,(tkinter_var)]

            # IO Typ verarbeiten
            for iotype in [self.dict_inps, self.dict_outs]:
                # ios verarbeiten
                for io in iotype[dev[0]]:

                    # Bytes umwandeln
                    int_byte = int.from_bytes(
                        ba_values[io[2]:io[2] + io[1]], byteorder="little"
                    )
                    if io[4] >= 0:
                        # Bit-IO
                        io[5].set(bool(int_byte & 1 << io[4]))
                    else:
                        # Byte-IO
                        io[5].set(int_byte)

        if self.autorw.get():
            self.master.after(200, self._readvalues)

    def readvalues(self):
        if not self.autorw.get():
            self._readvalues()

    def toggleauto(self):
        self.btn_read["state"] = "disabled" if self.autorw.get() else "normal"
        if self.autorw.get():
            self._readvalues()


# Testdrive
if __name__ == "__main__":
    cli = ServerProxy("http://192.168.50.35:55123")
    cli.psstart()

    tk = tkinter.Tk()
    RevPiCheckClient(tk, cli, 3)
    tk.mainloop()
