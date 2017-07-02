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
import tkinter.messagebox as tkmsg
from mytools import gettrans
from threading import Lock
from xmlrpc.client import MultiCall

# Übersetzung laden
_ = gettrans()


class RevPiCheckClient(tkinter.Frame):

    def __init__(self, master, xmlcli, xmlmode=0):
        """Instantiiert MyApp-Klasse."""
        super().__init__(master)

        # XML-Daten abrufen
        self.xmlmode = xmlmode
        self.cli = xmlcli
        self.cli.psstart()
        self.lst_devices = self.cli.ps_devices()
        self.dict_devices = {v[0]: v[1] for v in self.lst_devices}
        self.lst_devices = [d[0] for d in self.lst_devices]
        self.dict_inps = pickle.loads(self.cli.ps_inps().data)
        self.dict_outs = pickle.loads(self.cli.ps_outs().data)

        self.lk = Lock()
        self.dict_wins = {}
        self.__checkwrite = True
        self.__lockedvar = None
        self.__oldvalue = None

        self.autorw = tkinter.BooleanVar()
        self.dowrite = tkinter.BooleanVar()

        # Fenster aufbauen
        self._createwidgets()

        # Aktuelle Werte einlesen
        self.refreshvalues()

    def __chval(self, device, io, event=None):
        u"""Schreibt neuen Output Wert auf den RevPi."""
        if self.dowrite.get() and self._warnwrite():
            with self.lk:
                self.validatereturn(
                    self.cli.ps_setvalue(device, io[0], io[5].get())
                )

            # Alles neu einlesen wenn nicht AutoRW aktiv ist
            if not self.autorw.get():
                self.refreshvalues()

        self.__lockedvar = None

    def __hidewin(self, win, event=None):
        u"""Verbergt übergebenes Fenster.
        @param win Fenster zum verbergen
        @param event Tkinter Event"""
        win.withdraw()

    def __saveoldvalue(self, event, tkvar):
        u"""Speichert bei Keypress aktuellen Wert für wiederherstellung."""
        if self.__lockedvar is None:
            self.__lockedvar = tkvar
            try:
                self.__oldvalue = tkvar.get()
            except Exception:
                pass

    def __showwin(self, win):
        u"""Zeigt oder verbergt übergebenes Fenster.
        @param win Fenster zum anzeigen/verbergen"""
        if win.winfo_viewable():
            win.withdraw()
        else:
            win.deiconify()

    def __spinboxkey(self, device, io, event=None):
        u"""Prüft die Eingabe auf plausibilität.
        @param event tkinter Event
        @param io IO Liste mit tkinter Variable"""
        # io = [name,bytelen,byteaddr,bmk,bitaddress,(tkinter_var)]
        try:
            newvalue = io[5].get()
            # Wertebereich prüfen
            if newvalue < 0 or newvalue > 255 * io[1]:
                raise ValueError("too big")

            self.__chval(device, io)

        except Exception:
            io[5].set(self.__oldvalue)
            tkmsg.showerror(
                _("Error"),
                _("Given value for Output '{}' is not valid! \nReset to ""'{}'"
                    "").format(self.dict_devices[device], self.__oldvalue),
                parent=self.dict_wins[device]
            )

            # Focus zurücksetzen
            event.widget.focus_set()

    def _createiogroup(self, device, frame, iotype):
        u"""Erstellt IO-Gruppen.

        @param device Deviceposition
        @param frame tkinter Frame
        @param iotype 'inp' oder 'out' als str()

        """
        # IO-Typen festlegen
        if iotype == "inp":
            lst_io = self.dict_inps[device]
        else:
            lst_io = self.dict_outs[device]

        # Fensterinhalt aufbauen
        calc_heigh = len(lst_io) * 21
        canvas = tkinter.Canvas(
            frame,
            borderwidth=0,
            width=180,
            heigh=calc_heigh if calc_heigh <= 600 else 600
        )
        s_frame = tkinter.Frame(canvas)
        vsb = tkinter.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        # Scrollrad Linux
        canvas.bind(
            "<ButtonPress-4>",
            lambda x: canvas.yview_scroll(-1, "units")
        )
        canvas.bind(
            "<ButtonPress-5>",
            lambda x: canvas.yview_scroll(1, "units")
        )

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        canvas.create_window((4, 4), window=s_frame, anchor="nw")
        s_frame.bind(
            "<Configure>", lambda event, canvas=canvas: self._onfrmconf(canvas)
        )

        # IOs generieren
        rowcount = 0
        for io in lst_io:
            # io = [name,bytelen,byteaddr,bmk,bitaddress,(tkinter_var)]

            tkinter.Label(s_frame, text=io[0]).grid(
                column=0, row=rowcount, sticky="w"
            )

            if io[4] >= 0:
                var = tkinter.BooleanVar()
                check = tkinter.Checkbutton(s_frame)
                check["command"] = \
                    lambda device=device, io=io: self.__chval(device, io)
                check["state"] = "disabled" if iotype == "inp" else "normal"
                check["text"] = ""
                check["variable"] = var
                check.grid(column=1, row=rowcount)
            else:
                var = tkinter.IntVar()
                txt = tkinter.Spinbox(s_frame, to=255 * io[1])
                txt.bind(
                    "<Key>",
                    lambda event, tkvar=var: self.__saveoldvalue(event, tkvar)
                )
                txt.bind(
                    "<FocusOut>",
                    lambda event, device=device, io=io:
                    self.__spinboxkey(device, io, event)
                )
                txt["command"] = \
                    lambda device=device, io=io: self.__chval(device, io)
                txt["state"] = "disabled" if iotype == "inp" else "normal"
                txt["width"] = 4
                txt["textvariable"] = var
                txt.grid(column=1, row=rowcount)

            # Steuerelementvariable in IO übernehmen (mutabel)
            io.append(var)

            rowcount += 1

    def _createwidgets(self):
        """Erstellt den Fensterinhalt."""
        cFxPxy53 = {"fill": "x", "padx": 5, "pady": 3}

        devgrp = tkinter.LabelFrame(self)
        devgrp["text"] = _("Devices of RevPi")
        devgrp.pack(expand=True, fill="both", side="left")

        for dev in self.lst_devices:
            win = tkinter.Toplevel(self)
            win.wm_title(self.dict_devices[dev])
            win.protocol(
                "WM_DELETE_WINDOW",
                lambda win=win: self.__hidewin(win)
            )
            win.resizable(False, True)
            win.withdraw()
            self.dict_wins[dev] = win

            # Devicegruppe erstellen
            group = tkinter.LabelFrame(win)
            group["text"] = self.dict_devices[dev]
            group.pack(side="left", fill="both", expand=True)

            for iotype in ["inp", "out"]:
                frame = tkinter.Frame(group)
                frame.pack(side="left", fill="both", expand=True)
                self._createiogroup(dev, frame, iotype)

            # Button erstellen
            btn = tkinter.Button(devgrp)
            btn["command"] = lambda win=win: self.__showwin(win)
            btn["text"] = self.dict_devices[dev]
            btn.pack(**cFxPxy53)

        # Steuerungsfunktionen
        cntgrp = tkinter.LabelFrame(self)
        cntgrp["text"] = _("Control")
        cntgrp.pack(expand=True, fill="both", side="right")

        self.btn_refresh = tkinter.Button(cntgrp)
        self.btn_refresh["text"] = _("Read all IOs")
        self.btn_refresh["command"] = self.refreshvalues
        self.btn_refresh.pack(**cFxPxy53)

        self.btn_read = tkinter.Button(cntgrp)
        self.btn_read["text"] = _("Read just Inputs")
        self.btn_read["command"] = self.readvalues
        self.btn_read.pack(**cFxPxy53)

        self.btn_write = tkinter.Button(cntgrp)
        self.btn_write["state"] = "normal" if self.xmlmode >= 3 \
            else "disabled"
        self.btn_write["text"] = _("Write Outputs")
        self.btn_write["command"] = self.writevalues
        self.btn_write.pack(**cFxPxy53)

        self.chk_auto = tkinter.Checkbutton(cntgrp)
        self.chk_auto["command"] = self.toggleauto
        self.chk_auto["text"] = _("Autorefresh values")
        self.chk_auto["variable"] = self.autorw
        self.chk_auto.pack(anchor="w")

        self.chk_dowrite = tkinter.Checkbutton(cntgrp)
        self.chk_dowrite["command"] = self.togglewrite
        self.chk_dowrite["state"] = "normal" if self.xmlmode >= 3 \
            and self.autorw.get() else "disabled"
        self.chk_dowrite["text"] = _("Write values to RevPi")
        self.chk_dowrite["variable"] = self.dowrite
        self.chk_dowrite.pack(anchor="w")

    def _onfrmconf(self, canvas):
        u"""Erstellt Fenster in einem Canvas.
        @param canvas Canvas in dem Objekte erstellt werden sollen"""
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _warnwrite(self):
        u"""Warnung für Benutzer über Schreibfunktion einmal fragen.
        @return True, wenn Warnung einmal mit OK bestätigt wurde"""
        if self.__checkwrite:
            self.__checkwrite = not tkmsg.askokcancel(
                _("Warning"),
                _("You want to set outputs on the RevPi! Note that these are "
                    "set IMMEDIATELY!!! \nIf another control program is "
                    "running on the RevPi, it could interfere and reset the "
                    "outputs."),
                icon=tkmsg.WARNING,
                parent=self.master
            )
        return not self.__checkwrite

    def _workvalues(self, io_dicts=None, writeout=False):
        u"""Alle Werte der Inputs und Outputs abrufen.
        @param io_dicts Arbeit nur für dieses Dict()
        @param writeout Änderungen auf RevPi schreiben"""

        # Abfragelisten vorbereiten
        if io_dicts is None:
            io_dicts = [self.dict_inps, self.dict_outs]

        # Werte abrufen
        with self.lk:
            ba_values = bytearray(self.cli.ps_values().data)

        # Multicall zum Schreiben vorbereiten
        if writeout:
            xmlmc = MultiCall(self.cli)

        for dev in self.dict_devices:
            # io = [name,bytelen,byteaddr,bmk,bitaddress,(tkinter_var)]

            # IO Typ verarbeiten
            for iotype in io_dicts:
                # ios verarbeiten
                for io in iotype[dev]:

                    # Gesperrte Variable überspringen
                    if io[5] == self.__lockedvar:
                        continue

                    # Bytes umwandeln
                    int_byte = int.from_bytes(
                        ba_values[io[2]:io[2] + io[1]], byteorder="little"
                    )
                    if io[4] >= 0:
                        # Bit-IO
                        new_val = bool(int_byte & 1 << io[4])
                        if writeout and new_val != io[5].get():
                            xmlmc.ps_setvalue(dev, io[0], io[5].get())
                        else:
                            io[5].set(new_val)
                    else:
                        # Byte-IO
                        if writeout and int_byte != io[5].get():
                            xmlmc.ps_setvalue(dev, io[0], io[5].get())
                        else:
                            io[5].set(int_byte)

        # Werte per Multicall schreiben
        if writeout:
            with self.lk:
                self.validatereturn(xmlmc())

    def hideallwindows(self):
        u"""Versteckt alle Fenster."""
        for win in self.dict_wins:
            self.dict_wins[win].withdraw()

    def readvalues(self):
        u"""Ruft nur Input Werte von RevPi ab und aktualisiert Fenster."""
        if not self.autorw.get():
            self._workvalues([self.dict_inps])

    def refreshvalues(self):
        u"""Ruft alle IO Werte von RevPi ab und aktualisiert Fenster."""
        if not self.autorw.get():
            self._workvalues()

    def tmr_workvalues(self):
        u"""Timer für zyklische Abfrage.
        @return None"""
        # Verbleibener Timer könnte schon ungültig sein
        if not self.autorw.get():
            try:
                self.chk_auto["state"] = "normal"
                self._workvalues()
            except:
                pass
            return None

        self.master.after(200, self.tmr_workvalues)

    def toggleauto(self):
        u"""Schaltet zwischen Autorefresh um und aktualisiert Widgets."""
        stateval = "disabled" if self.autorw.get() else "normal"
        self.btn_refresh["state"] = stateval
        self.btn_read["state"] = stateval
        self.btn_write["state"] = stateval if self.xmlmode >= 3 \
            else "disabled"

        self.chk_dowrite["state"] = "normal" if self.xmlmode >= 3 \
            and self.autorw.get() else "disabled"

        if self.autorw.get():
            self.tmr_workvalues()
        else:
            self.chk_auto["state"] = "disabled"
            self.dowrite.set(False)

    def togglewrite(self):
        u"""Schaltet zwischen DoWrite um und aktiviert Schreibfunktion."""
        if self._warnwrite():
            self.refreshvalues()
        else:
            self.dowrite.set(False)

    def validatereturn(self, returnlist):
        u"""Überprüft die Rückgaben der setvalue Funktion.
        @param returnlist list() der xml Rückgabe"""
        if type(returnlist[0]) != list:
            returnlist = [returnlist]

        str_errmsg = ""
        for lst_result in returnlist:
            # [device, io, status, msg]

            if not lst_result[2]:
                # Fehlermeldungen erstellen
                devicename = self.dict_devices[lst_result[0]]
                str_errmsg += _(
                    "Error set value of device '{}' Output '{}': {} \n"
                ).format(devicename, lst_result[1], lst_result[3])
        if str_errmsg != "":
            tkmsg.showerror(_("Error"), str_errmsg)

    def writevalues(self):
        u"""Schreibt geänderte Outputs auf den RevPi."""
        if self._warnwrite() and not self.autorw.get():
            self._workvalues([self.dict_outs], True)
