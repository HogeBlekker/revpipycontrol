# -*- coding: utf-8 -*-
u"""Optionen für das MQTT System."""

__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2018 Sven Sager"
__license__ = "GPLv3"

import tkinter
import tkinter.messagebox as tkmsg
from mytools import gettrans

# Übersetzung laden
_ = gettrans()


class MqttManager(tkinter.Frame):

    u"""Hauptfenster der MQTT-Einstellungen."""

    def __init__(self, master, settings, readonly=False):
        u"""Init MqttManager-Class.
        @return None"""
        if not isinstance(settings, dict):
            raise ValueError("parameter settings must be <class 'dict'>")
        if not isinstance(readonly, bool):
            raise ValueError("parameter readonly must be <class 'bool'>")

        super().__init__(master)
        self.master.bind("<KeyPress-Escape>", self._checkclose)
        self.master.protocol("WM_DELETE_WINDOW", self._checkclose)
        self.pack(expand=True, fill="both")

        # Daten laden
        self.__ro = "disabled" if readonly else "normal"
        self.__settings = settings

        # Fenster bauen
        self._createwidgets()

    def _changesdone(self):
        u"""Prüft ob sich die Einstellungen geändert haben.
        @return True, wenn min. eine Einstellung geändert wurde"""
        return (
            self.var_basetopic.get() != self.__settings["mqttbasetopic"] or
            self.var_send_events.get() != self.__settings["mqttsend_events"] or
            self.var_client_id.get() != self.__settings["mqttclient_id"] or
            self.var_password.get() != self.__settings["mqttpassword"] or
            self.var_port.get() != str(self.__settings["mqttport"]) or
            self.var_tls_set.get() != self.__settings["mqtttls_set"] or
            self.var_username.get() != self.__settings["mqttusername"] or
            self.var_broker_address.get() !=
            self.__settings["mqttbroker_address"] or
            self.var_sendinterval.get() !=
            str(self.__settings["mqttsendinterval"]) or
            self.var_write_outputs.get() !=
            self.__settings["mqttwrite_outputs"]
        )

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
        self.master.wm_title(_("MQTT Settings"))
        self.master.wm_resizable(width=False, height=False)

        # cpade = {"padx": 4, "pady": 2, "sticky": "e"}
        cpadw = {"padx": 4, "pady": 2, "sticky": "w"}
        cpadwe = {"padx": 4, "pady": 2, "sticky": "we"}

        # Gruppe MQTT System ######################################

        # Basetopic
        gb = tkinter.LabelFrame(self)
        gb["text"] = _("MQTT base topic")
        gb.columnconfigure(0, weight=1)
        gb.pack(expand=True, fill="both", padx=4, pady=4)

        self.var_basetopic = tkinter.StringVar(
            gb, self.__settings["mqttbasetopic"])

        row = 0
        lbl = tkinter.Label(gb)
        lbl["text"] = _("Base topic") + ":"
        lbl.grid(row=row, column=0, **cpadw)

        txt = tkinter.Entry(gb)
        txt["state"] = self.__ro
        txt["textvariable"] = self.var_basetopic
        txt["width"] = 34
        txt.grid(row=row, column=1, **cpadwe)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["justify"] = "left"
        lbl["text"] = _(
            """The base topic is the first part of any mqtt topic, the
Revolution Pi will publish. You can use any character
includig '/' to identify the messages and subscribe them
on your broker.

For example: revpi0000/data"""
        )
        lbl.grid(row=row, column=0, columnspan=2, **cpadw)

        # Publish settings
        gb = tkinter.LabelFrame(self)
        gb["text"] = _("MQTT publish settings")
        gb.columnconfigure(0, weight=1)
        gb.pack(expand=True, fill="both", padx=4, pady=4)

        self.var_send_events = tkinter.BooleanVar(
            gb, self.__settings["mqttsend_events"])
        self.var_sendinterval = tkinter.StringVar(
            gb, self.__settings["mqttsendinterval"])
        self.var_write_outputs = tkinter.BooleanVar(
            gb, self.__settings["mqttwrite_outputs"])

        row = 0
        lbl = tkinter.Label(gb)
        lbl["text"] = _("Publish all exported values every n seconds") + ":"
        lbl.grid(row=row, column=0, **cpadw)
        sb = tkinter.Spinbox(gb)
        sb["state"] = self.__ro
        sb["textvariable"] = self.var_sendinterval
        sb["width"] = 5
        sb.grid(row=row, column=1, **cpadw)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["justify"] = "left"
        lbl["text"] = _("Topic: \t[basetopic]/io/[ioname]")
        lbl.grid(row=row, columnspan=2, **cpadw)

        row += 1
        cb = tkinter.Checkbutton(gb)
        cb["state"] = self.__ro
        cb["text"] = _("Send exported values immediately on value change")
        cb["variable"] = self.var_send_events
        cb.grid(row=row, columnspan=2, **cpadw)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["justify"] = "left"
        lbl["text"] = _("Topic: \t[basetopic]/event/[ioname]")
        lbl.grid(row=row, columnspan=2, **cpadw)

        # Subscribe settings
        gb = tkinter.LabelFrame(self)
        gb["text"] = _("MQTT set outputs")
        gb.columnconfigure(0, weight=1)
        gb.pack(expand=True, fill="both", padx=4, pady=4)

        row = 0
        cb = tkinter.Checkbutton(gb)
        cb["state"] = self.__ro
        cb["text"] = _("Allow MQTT to to set outputs on Revolution Pi")
        cb["variable"] = self.var_write_outputs
        cb.grid(row=row, columnspan=2, **cpadw)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["justify"] = "left"
        lbl["text"] = _(
            """The Revolution Pi will subscribe a topic on which your client
can publish messages with the new value as payload.

Publish values with topic: \t[basetopic]/set/[outputname]"""
        )
        lbl.grid(row=row, columnspan=2, **cpadw)

        # ############################################################

        # Gruppe Broker ##########################################
        gb = tkinter.LabelFrame(self)
        gb["text"] = _("MQTT broker settings")
        gb.pack(expand=True, fill="both", padx=4, pady=4)
        gb.columnconfigure(2, weight=1)

        # Variablen
        self.var_client_id = tkinter.StringVar(
            gb, self.__settings["mqttclient_id"])
        self.var_broker_address = tkinter.StringVar(
            gb, self.__settings["mqttbroker_address"])
        self.var_password = tkinter.StringVar(
            gb, self.__settings["mqttpassword"])
        self.var_port = tkinter.StringVar(
            gb, self.__settings["mqttport"])
        self.var_tls_set = tkinter.BooleanVar(
            gb, self.__settings["mqtttls_set"])
        self.var_username = tkinter.StringVar(
            gb, self.__settings["mqttusername"])

        row = 0
        lbl = tkinter.Label(gb)
        lbl["text"] = _("Broker address") + ":"
        lbl.grid(row=row, column=0, **cpadw)
        txt = tkinter.Entry(gb)
        txt["state"] = self.__ro
        txt["textvariable"] = self.var_broker_address
        txt.grid(row=row, column=1, columnspan=2, **cpadw)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["text"] = _("Broker port") + ":"
        lbl.grid(row=row, column=0, **cpadw)
        sb = tkinter.Spinbox(gb)
        sb["state"] = self.__ro
        sb["textvariable"] = self.var_port
        sb["width"] = 6
        sb.grid(row=row, column=1, **cpadw)

        ckb = tkinter.Checkbutton(gb)
        ckb["state"] = self.__ro
        ckb["text"] = _("Use TLS") + ":"
        ckb["variable"] = self.var_tls_set
        ckb.grid(row=row, column=2, **cpadw)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["text"] = _("Username") + ":"
        lbl.grid(row=row, column=0, **cpadw)
        txt = tkinter.Entry(gb)
        txt["state"] = self.__ro
        txt["textvariable"] = self.var_username
        txt.grid(row=row, column=1, columnspan=2, **cpadw)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["text"] = _("Password") + ":"
        lbl.grid(row=row, column=0, **cpadw)
        txt = tkinter.Entry(gb)
        txt["state"] = self.__ro
        txt["textvariable"] = self.var_password
        txt.grid(row=row, column=1, columnspan=2, **cpadw)

        row += 1
        lbl = tkinter.Label(gb)
        lbl["text"] = _("Client ID") + ":"
        lbl.grid(row=row, column=0, **cpadw)
        txt = tkinter.Entry(gb)
        txt["state"] = self.__ro
        txt["textvariable"] = self.var_client_id
        txt["width"] = 30
        txt.grid(row=row, column=1, columnspan=2, **cpadw)

        # ############################################################

        frame = tkinter.Frame(self)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.pack(expand=True, fill="both", pady=4)

        # Buttons
        btn_save = tkinter.Button(frame)
        btn_save["command"] = self._save
        btn_save["state"] = self.__ro
        btn_save["text"] = _("Save")
        btn_save.grid(column=0, row=0)

        btn_close = tkinter.Button(frame)
        btn_close["command"] = self._checkclose
        btn_close["text"] = _("Close")
        btn_close.grid(column=1, row=0)

    def _save(self):
        u"""Übernimt die Änderungen."""

        # TODO: Wertprüfung

        # Wertübernahme
        self.__settings["mqttbasetopic"] = self.var_basetopic.get()
        self.__settings["mqttsendinterval"] = int(self.var_sendinterval.get())
        self.__settings["mqttsend_events"] = int(self.var_send_events.get())
        self.__settings["mqttwrite_outputs"] = \
            int(self.var_write_outputs.get())
        self.__settings["mqttbroker_address"] = self.var_broker_address.get()
        self.__settings["mqtttls_set"] = int(self.var_tls_set.get())
        self.__settings["mqttport"] = int(self.var_port.get())
        self.__settings["mqttusername"] = self.var_username.get()
        self.__settings["mqttpassword"] = self.var_password.get()
        self.__settings["mqttclient_id"] = self.var_client_id.get()

        self._checkclose()

    def get_settings(self):
        u"""Gibt die MQTT Konfiguration zurück.
        @return Settings als <class 'dict'>"""
        return self.__settings

    settings = property(get_settings)


# Debugging
if __name__ == "__main__":
    dict_mqttsettings = {
        "mqttbasetopic": "revpi01",
        "mqttclient_id": "",
        "mqttbroker_address": "127.0.0.1",
        "mqttpassword": "",
        "mqttport": 1883,
        "mqttsend_events": 0,
        "mqttsendinterval": 30,
        "mqtttls_set": 0,
        "mqttusername": "",
        "mqttwrite_outputs": 0,
    }
    root = MqttManager(tkinter.Tk(), dict_mqttsettings)
    root.mainloop()
