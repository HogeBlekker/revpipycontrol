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
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from xmlrpc.client import ServerProxy, Binary, MultiCall


class RevPiCheckClient(tkinter.Frame):

    def __init__(self, master, xmlcli):
        """Instantiiert MyApp-Klasse."""
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.cli = xmlcli

        self.lst_devices = self.cli.get_devicenames()
        self.lst_group = []
        self.dict_inpvar = {}
        self.dict_outvar = {}

        self.autorw = tkinter.BooleanVar()
        self.fut_autorw = None

        # Fenster aufbauen
        self._createwidgets()

        # Aktuelle Werte einlesen
        self.readvalues()

    def _autorw(self):
        dict_inp = {}
        dict_out = {}

        while self.autorw.get():
            for dev in self.lst_devices:
                try:
                    dict_out[dev] = [
                        value[8].get() for value in self.dict_outvar[dev]
                    ]
                except:
                    print("lasse {} aus".format(dev))

            dict_inp = self.cli.refreshvalues(
                Binary(pickle.dumps(dict_out, 3))
            )
            dict_inp = pickle.loads(dict_inp.data)

            for dev in dict_inp:
                for io in self.dict_inpvar[dev]:
                    try:
                        io[8].set(dict_inp[dev].pop(0))
                    except:
                        print("lasse {} aus".format(io[0]))

            sleep(0.1)

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
        for io in self.cli.get_iolist(device, iotype):
            # io = [name,default,anzbits,adressbyte,export,adressid,bmk,bitaddress,tkinter_var]

            tkinter.Label(s_frame, text=io[0]).grid(
                column=0, row=rowcount, sticky="w"
            )

            if io[7] >= 0:
                var = tkinter.BooleanVar()
                check = tkinter.Checkbutton(s_frame)
                check["state"] = "disabled" if iotype == "inp" else "normal"
                check["text"] = ""
                check["variable"] = var
                check.grid(column=1, row=rowcount)
            else:
                var = tkinter.IntVar()
                txt = tkinter.Spinbox(s_frame, to=256)
                txt["state"] = "disabled" if iotype == "inp" else "normal"
                txt["width"] = 4
                txt["textvariable"] = var
                txt.grid(column=1, row=rowcount)

            # Steuerelementvariable in IO übernehmen
            io.append(var)
            if iotype == "inp":
                self.dict_inpvar[device].append(io)
            elif iotype == "out":
                self.dict_outvar[device].append(io)

            rowcount += 1

    def _createwidgets(self):
        """Erstellt den Fensterinhalt."""
        # Hauptfenster
        self.master.wm_title("RevPi Onlineview")

        for dev in self.lst_devices:
            # Variablen vorbereiten
            self.dict_inpvar[dev] = []
            self.dict_outvar[dev] = []

            # Devicegruppe erstellen
            group = tkinter.LabelFrame(self)
            group["text"] = dev
            group.pack(side="left", fill="both", expand=True)
            self.lst_group.append(group)

            for iotype in ["inp", "out"]:
                frame = tkinter.Frame(group)
                frame.pack(side="left", fill="both", expand=True)
                self._createiogroup(dev, frame, iotype)

#        self.btn_update = tkinter.Button(self)
#        self.btn_update["text"] = "UPDATE"
#        self.btn_update["command"] = self._autorw
#        self.btn_update.pack(anchor="s", side="bottom", fill="x")

        self.btn_write = tkinter.Button(self)
        self.btn_write["text"] = "SCHREIBEN"
        self.btn_write["command"] = self.writevalues
        self.btn_write.pack(side="bottom", fill="x")

        self.btn_read = tkinter.Button(self)
        self.btn_read["text"] = "LESEN"
        self.btn_read["command"] = self.readvalues
        self.btn_read.pack(side="bottom", fill="x")

        check = tkinter.Checkbutton(self)
        check["command"] = self.toggleauto
        check["text"] = "autoupdate"
        check["variable"] = self.autorw
        check.pack(side="bottom")

    def _readvaluesdev(self, device, iotype):
        """Ruft alle aktuellen Werte fuer das Device ab."""
        # Multicall vorbereiten
        mc_values = MultiCall(self.cli)

        if iotype == "inp":
            lst_ios = self.dict_inpvar[device]
        elif iotype == "out":
            lst_ios = self.dict_outvar[device]

        for io in lst_ios:
            mc_values.get_iovalue(device, io[0])

        i = 0
        for value in mc_values():
            value = pickle.loads(value.data)
            if type(value) == bytes:
                value = int.from_bytes(value, byteorder="little")

            lst_ios[i][8].set(value)
            i += 1

    def _writevaluesdev(self, device):
        """Sendet Werte der Outputs fuer ein Device."""
        # Multicall vorbereiten
        mc_values = MultiCall(self.cli)
        lst_ios = lst_ios = self.dict_outvar[device]

        for io in lst_ios:
            mc_values.set_iovalue(device, io[0], pickle.dumps(io[8].get(), 3))

        # Multicall ausführen
        mc_values()

    def readvalues(self):
        """Alle Werte der Inputs und Outputs abrufen."""
        # Werte aus Prozessabbild einlesen
        self.cli.readprocimg()

        for dev in self.lst_devices:
            self._readvaluesdev(dev, "inp")
            self._readvaluesdev(dev, "out")

    def toggleauto(self):
        self.btn_read["state"] = "disabled" if self.autorw.get() else "normal"
        self.btn_write["state"] = "disabled" if self.autorw.get() else "normal"
        if self.autorw.get() \
                and (self.fut_autorw is None or self.fut_autorw.done()):
            e = ThreadPoolExecutor(max_workers=1)
            self.fut_autorw = e.submit(self._autorw)

    def writevalues(self):
        """Alle Outputs senden."""
        pass
        #for dev in self.lst_devices:
            #self._writevaluesdev(dev)

        # Werte in Prozessabbild schreiben
        #self.cli.writeprocimg()

if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiCheckClient(root)
    myapp.mainloop()
