#
# RevPiPyControl
#
# Webpage: https://revpimodio.org/revpipyplc/
# (c) Sven Sager, License: LGPLv3
#
# -*- coding: utf-8 -*-
import os.path
import pickle
import tkinter
import tkinter.messagebox as tkmsg
from os import environ
from os import makedirs
from sys import platform

# Systemwerte
if platform == "linux":
    homedir = environ["HOME"]
else:
    homedir = environ["APPDATA"]
savefile = os.path.join(homedir, ".revpipyplc", "connections.dat")

def get_connections():
    if os.path.exists(savefile):
        fh = open(savefile, "rb")
        connections = pickle.load(fh)
    return connections


class RevPiPlcList(tkinter.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.pack()

        # Daten laden
        self._connections = {}

        # Fenster bauen
        self._createwidgets()
        self._loadappdata()

    def _createwidgets(self):
        self.master.wm_title("RevPi Python PLC Connections")
        self.master.wm_resizable(width=False, height=False)

        # Listbox mit vorhandenen Verbindungen
        self.scr_conn = tkinter.Scrollbar(self)
        self.scr_conn.grid(column=1, row=0, rowspan=10, sticky="ns")
        self.list_conn = tkinter.Listbox(self, width=20, heigh=15)
        self.list_conn.bind("<<ListboxSelect>>", self.evt_listconn)
        self.list_conn.grid(column=0, row=0, rowspan=10)
        self.list_conn["yscrollcommand"] = self.scr_conn.set
        self.scr_conn["command"] = self.list_conn.yview

        # Variablen und Defaultwerte
        self.var_address = tkinter.StringVar(self)
        self.var_port = tkinter.StringVar(self)
        self.var_name = tkinter.StringVar(self)
        self.var_port.set("55123")

        # Eingabefelder für Adresse und Namen
        tkinter.Label(self, text="Name").grid(
            column=2, row=0, sticky="wn", padx=5, pady=5)
        self.txt_name = tkinter.Entry(self, textvariable=self.var_name)
        self.txt_name.bind("<KeyRelease>", self.evt_keypress)
        self.txt_name.grid(
            column=3, row=0, columnspan=3, sticky="n", padx=5, pady=5)        

        tkinter.Label(self, text="IP-Adresse").grid(
            column=2, row=1, sticky="wn", padx=5, pady=5
        )
        self.txt_address = tkinter.Entry(self, textvariable=self.var_address)
        self.txt_address.bind("<KeyRelease>", self.evt_keypress)
        self.txt_address.grid(
            column=3,  row=1, columnspan=3, sticky="n", padx=5, pady=5)

        tkinter.Label(self, text="Port").grid(
            column=2, row=2, sticky="wn", padx=5, pady=5)
        self.txt_port = tkinter.Entry(self, textvariable=self.var_port)
        self.txt_port.bind("<KeyRelease>", self.evt_keypress)
        self.txt_port.grid(
            column=3, row=2, columnspan=3, sticky="n", padx=5, pady=5)

        # Listenbutton
        self.btn_new = tkinter.Button(
            self, text="Neu", command=self.evt_btnnew)
        self.btn_new.grid(column=2, row=3, sticky="s")
        self.btn_add = tkinter.Button(
            self, text="Übernehmen", command=self.evt_btnadd, state="disabled")
        self.btn_add.grid(column=3, row=3, sticky="s")
        self.btn_remove = tkinter.Button(
            self, text="Entfernen", command=self.evt_btnremove, state="disabled")
        self.btn_remove.grid(column=4, row=3, sticky="s")

        # Fensterbuttons
        self.btn_save = tkinter.Button(
            self, text="Speichern", command=self.evt_btnsave)
        self.btn_save.grid(column=3, row=9, sticky="se")
        self.btn_close = tkinter.Button(
            self, text="Schließen", command=self.evt_btnclose)
        self.btn_close.grid(column=4, row=9, sticky="se")

    def _loadappdata(self):
        if os.path.exists(savefile):
            fh = open(savefile, "rb")
            self._connections = pickle.load(fh)
        self.build_listconn()

    def _saveappdata(self):
        try:
            makedirs(os.path.dirname(savefile), exist_ok=True)
            fh = open(savefile, "wb")
            pickle.dump(self._connections, fh)
        except:
            return False
        return True

    def build_listconn(self):
        self.list_conn.delete(0, "end")
        lst_conns = sorted(self._connections.keys(), key=lambda x: x.lower())
        self.list_conn.insert("end",*lst_conns)

    def evt_btnadd(self):
        # TODO: Daten prüfen
        self._connections[self.var_name.get()] = \
            (self.var_address.get(), self.var_port.get())

        self.build_listconn()
        self.evt_btnnew()

    def evt_btnclose(self):
        ask = tkmsg.askyesno(
            "Frage...",
            "Wollen Sie wirklich beenden?\n"
            "Nicht gespeicherte Änderungen gehen verloren",
            parent=self.master
        )
        if ask:
            self.master.destroy()

    def evt_btnnew(self):
        self.list_conn.select_clear(0, "end")
        self.evt_listconn()

        self.btn_add["state"] = "disabled"
        self.var_address.set("")
        self.var_name.set("")
        self.var_port.set("55123")

    def evt_btnremove(self):
        item_index = self.list_conn.curselection()
        if len(item_index) == 1:
            item = self.list_conn.get(item_index[0])
            ask = tkmsg.askyesno(
                "Frage",
                "Wollen Sie die Ausgewählte Verbindung '{}' wirklich "
                "löschen?".format(item),
                parent=self.master
            )
            if ask:
                # Daten löschen
                del self._connections[item]
                self.build_listconn()
                self.evt_btnnew()

    def evt_btnsave(self):
        if self._saveappdata():
            ask = tkmsg.askyesno(
                "Information", "Verbindungen erfolgreich gespeichert.\n"
                "Möchten Sie dieses Fenster jetzt schließen?",
                parent=self.master
            )
            if ask:
                self.master.destroy()
        else:
            tkmsg.showerror(
                "Fehler", "Verbindungen konnten nicht gespeichert werden",
                parent=self.master
            )

    def evt_listconn(self, evt=None):

        item_index = self.list_conn.curselection()
        if len(item_index) == 1:

            # Daten lesen
            item = self.list_conn.get(item_index[0])
            self.var_name.set(item)
            self.var_address.set(self._connections[item][0])
            self.var_port.set(self._connections[item][1])

            self.btn_add["state"] == "normal"

            self.btn_remove["state"] = "normal"
        else:
            self.btn_remove["state"] = "disabled"

    def evt_keypress(self, evt=None):
        okvalue = "normal" if (self.var_address.get() != ""
            and self.var_name.get() != ""
            and self.var_port.get() != ""
        ) else "disabled"
        self.btn_add["state"] = okvalue


if __name__ == "__main__":
    root = tkinter.Tk()
    myapp = RevPiPlcList(root)
    myapp.mainloop()
