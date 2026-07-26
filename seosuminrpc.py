#!/usr/bin/env python3
# Seo SuMinRPC - custom Discord Rich Presence tool, no GTK4/Electron needed.
# GTK3 + pypresence, talks to Discord over its local IPC socket.

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

import os
import json
import time
import threading
import traceback
from datetime import datetime

from pypresence import Presence
from pypresence.exceptions import PyPresenceException
from pypresence.types import ActivityType

APP_NAME = "Seo SuMinRPC"
APP_VERSION = "1.0"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "seosuminrpc")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

UPDATE_INTERVAL_SECONDS = 15  # Discord rate-limits presence updates; 15s is safe.

ACTIVITY_TYPES = {
    "Playing": ActivityType.PLAYING,
    "Listening": ActivityType.LISTENING,
    "Watching": ActivityType.WATCHING,
    "Competing": ActivityType.COMPETING,
}

TIMESTAMP_MODES = [
    "since_connection",
    "since_update",
    "since_started",
    "local_time",
    "custom",
    "none",
]

TIMESTAMP_LABELS = {
    "since_connection": "Since last connection",
    "since_update": "Since last presence update",
    "since_started": "Since program started",
    "local_time": "Your local time (no elapsed timer)",
    "custom": "Custom start/end timestamp",
    "none": "No timestamp",
}


def now_ts():
    return int(time.time())


class SeoSuMinRPCWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title=APP_NAME)
        self.set_default_size(560, 640)
        self.set_border_width(10)
        self.connect("destroy", self.on_quit)

        self.entries = {}
        self.combos = {}
        self.rpc = None
        self.connected = False
        self.app_started_at = now_ts()
        self.connected_at = None
        self.last_update_at = None
        self.discord_user = None
        self.update_thread = None
        self.stop_event = threading.Event()

        self.build_ui()
        self.load_config()
        GLib.timeout_add_seconds(1, self.tick_clock)

    # -- UI --

    def build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add(root)

        root.add(self.build_menubar())

        grid = Gtk.Grid(column_spacing=8, row_spacing=6)
        root.add(grid)
        row = 0

        # ID / Type / Display
        row = self.add_row(grid, row, "Application ID", self.entry("client_id"), extra_widgets=[
            self.labeled(self.combo("activity_type", list(ACTIVITY_TYPES.keys()), "Playing"), "Type"),
        ])

        self.entries["name"] = Gtk.Entry(placeholder_text="Overrides displayed name (optional)")
        row = self.add_row(grid, row, "Name", self.entries["name"])

        row = self.add_row(grid, row, "Details", self.entry("details"), url_key="details_url")
        row = self.add_row(grid, row, "State", self.entry("state"), url_key="state_url")

        # Party
        party_box = Gtk.Box(spacing=6)
        self.spin_party_current = Gtk.SpinButton.new_with_range(0, 999, 1)
        self.spin_party_max = Gtk.SpinButton.new_with_range(0, 999, 1)
        self.check_party = Gtk.CheckButton(label="Show party")
        party_box.pack_start(self.check_party, False, False, 0)
        party_box.pack_start(self.spin_party_current, False, False, 0)
        party_box.pack_start(Gtk.Label(label="of"), False, False, 0)
        party_box.pack_start(self.spin_party_max, False, False, 0)
        grid.attach(Gtk.Label(label="Party", halign=Gtk.Align.START), 0, row, 1, 1)
        grid.attach(party_box, 1, row, 2, 1)
        row += 1

        # Timestamp
        grid.attach(Gtk.Label(label="Timestamp", halign=Gtk.Align.START, valign=Gtk.Align.START), 0, row, 1, 1)
        ts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.ts_radios = {}
        first_radio = None
        for key in TIMESTAMP_MODES:
            rb = Gtk.RadioButton.new_with_label_from_widget(first_radio, TIMESTAMP_LABELS[key])
            if first_radio is None:
                first_radio = rb
            self.ts_radios[key] = rb
            ts_box.pack_start(rb, False, False, 0)
        self.ts_radios["local_time"].set_active(True)

        custom_box = Gtk.Box(spacing=6)
        self.entry_custom_start = Gtk.Entry(placeholder_text="YYYY-MM-DD HH:MM:SS")
        self.entry_custom_end = Gtk.Entry(placeholder_text="YYYY-MM-DD HH:MM:SS (optional)")
        custom_box.pack_start(Gtk.Label(label="Start"), False, False, 0)
        custom_box.pack_start(self.entry_custom_start, True, True, 0)
        custom_box.pack_start(Gtk.Label(label="End"), False, False, 0)
        custom_box.pack_start(self.entry_custom_end, True, True, 0)
        ts_box.pack_start(custom_box, False, False, 0)

        grid.attach(ts_box, 1, row, 2, 1)
        row += 1

        # Large / small image
        row = self.image_block(grid, row, "Large Image", "large_image", "large_text", "large_url")
        row = self.image_block(grid, row, "Small Image", "small_image", "small_text", "small_url")

        # Buttons
        row = self.button_block(grid, row, 1)
        row = self.button_block(grid, row, 2)

        # Action buttons
        action_box = Gtk.Box(spacing=6)
        self.btn_connect = Gtk.Button(label="Connect")
        self.btn_connect.connect("clicked", self.on_connect)
        self.btn_disconnect = Gtk.Button(label="Disconnect")
        self.btn_disconnect.connect("clicked", self.on_disconnect)
        self.btn_disconnect.set_sensitive(False)
        self.btn_update = Gtk.Button(label="Update Presence")
        self.btn_update.connect("clicked", self.on_update_clicked)
        self.check_autoupdate = Gtk.CheckButton(label=f"Auto-refresh every {UPDATE_INTERVAL_SECONDS}s")
        self.check_autoupdate.set_active(True)
        action_box.pack_start(self.btn_connect, False, False, 0)
        action_box.pack_start(self.btn_disconnect, False, False, 0)
        action_box.pack_end(self.btn_update, False, False, 0)
        action_box.pack_end(self.check_autoupdate, False, False, 0)
        root.add(action_box)

        # Status bar
        self.status_label = Gtk.Label(label="Not connected", halign=Gtk.Align.START)
        root.add(self.status_label)

        self.show_all()

    def build_menubar(self):
        menubar = Gtk.MenuBar()

        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)

        save_item = Gtk.MenuItem(label="Save Preset As…")
        save_item.connect("activate", self.on_save_preset_as)
        load_item = Gtk.MenuItem(label="Load Preset…")
        load_item.connect("activate", self.on_load_preset)
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.on_quit)
        for item in (save_item, load_item, Gtk.SeparatorMenuItem(), quit_item):
            file_menu.append(item)

        settings_menu = Gtk.Menu()
        settings_item = Gtk.MenuItem(label="Settings")
        settings_item.set_submenu(settings_menu)
        autoconnect_item = Gtk.CheckMenuItem(label="Connect automatically on launch")
        self.autoconnect_check = autoconnect_item
        settings_menu.append(autoconnect_item)

        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)
        about_item = Gtk.MenuItem(label="About")
        about_item.connect("activate", self.on_about)
        help_menu.append(about_item)

        menubar.append(file_item)
        menubar.append(settings_item)
        menubar.append(help_item)
        return menubar

    # -- UI helpers --

    def entry(self, key):
        e = Gtk.Entry()
        self.entries[key] = e
        return e

    def combo(self, key, options, default=None):
        c = Gtk.ComboBoxText()
        for opt in options:
            c.append_text(opt)
        if default and default in options:
            c.set_active(options.index(default))
        else:
            c.set_active(0)
        self.combos[key] = c
        return c

    def labeled(self, widget, text):
        box = Gtk.Box(spacing=4)
        box.pack_start(Gtk.Label(label=text), False, False, 0)
        box.pack_start(widget, False, False, 0)
        return box

    def add_row(self, grid, row, label_text, main_widget, url_key=None, extra_widgets=None):
        grid.attach(Gtk.Label(label=label_text, halign=Gtk.Align.START), 0, row, 1, 1)
        main_widget.set_hexpand(True)
        grid.attach(main_widget, 1, row, 1, 1)
        if url_key:
            url_entry = self.entry(url_key)
            url_entry.set_placeholder_text("Click-through URL (optional)")
            grid.attach(Gtk.Label(label="URL", halign=Gtk.Align.START), 2, row, 1, 1)
            grid.attach(url_entry, 3, row, 1, 1)
        if extra_widgets:
            box = Gtk.Box(spacing=6)
            for w in extra_widgets:
                box.pack_start(w, False, False, 0)
            grid.attach(box, 2, row, 2, 1)
        return row + 1

    def image_block(self, grid, row, title, key_field, text_field, url_field):
        grid.attach(Gtk.Label(label=f"<b>{title}</b>", use_markup=True, halign=Gtk.Align.START), 0, row, 4, 1)
        row += 1
        grid.attach(Gtk.Label(label="Key", halign=Gtk.Align.START), 0, row, 1, 1)
        key_entry = self.entry(key_field)
        key_entry.set_placeholder_text("asset key or direct image URL")
        grid.attach(key_entry, 1, row, 1, 1)
        grid.attach(Gtk.Label(label="Text", halign=Gtk.Align.START), 2, row, 1, 1)
        text_entry = self.entry(text_field)
        grid.attach(text_entry, 3, row, 1, 1)
        row += 1
        grid.attach(Gtk.Label(label="URL", halign=Gtk.Align.START), 0, row, 1, 1)
        url_entry = self.entry(url_field)
        url_entry.set_placeholder_text("click-through link (optional)")
        grid.attach(url_entry, 1, row, 3, 1)
        row += 1
        return row

    def button_block(self, grid, row, n):
        grid.attach(Gtk.Label(label=f"Button {n}", halign=Gtk.Align.START), 0, row, 1, 1)
        text_entry = self.entry(f"button{n}_text")
        text_entry.set_placeholder_text("Label")
        grid.attach(text_entry, 1, row, 1, 1)
        url_entry = self.entry(f"button{n}_url")
        url_entry.set_placeholder_text("https://…")
        grid.attach(url_entry, 2, row, 2, 1)
        return row + 1

    # -- discord --

    def get_timestamp_mode(self):
        for key, rb in self.ts_radios.items():
            if rb.get_active():
                return key
        return "none"

    def compute_start_end(self):
        mode = self.get_timestamp_mode()
        if mode == "since_connection":
            return self.connected_at, None
        if mode == "since_update":
            return self.last_update_at, None
        if mode == "since_started":
            return self.app_started_at, None
        if mode == "custom":
            start = self.parse_dt(self.entry_custom_start.get_text())
            end = self.parse_dt(self.entry_custom_end.get_text())
            return start, end
        return None, None  # local_time / none

    @staticmethod
    def parse_dt(text):
        text = text.strip()
        if not text:
            return None
        try:
            return int(datetime.strptime(text, "%Y-%m-%d %H:%M:%S").timestamp())
        except ValueError:
            return None

    def substitute_tokens(self, text):
        if not text:
            return text
        now = datetime.now()
        return (
            text.replace("{time}", now.strftime("%H:%M:%S"))
            .replace("{date}", now.strftime("%Y-%m-%d"))
        )

    def build_payload(self):
        get = lambda k: self.entries[k].get_text().strip() or None
        details = self.substitute_tokens(get("details"))
        state = self.substitute_tokens(get("state"))
        start, end = self.compute_start_end()

        buttons = []
        for n in (1, 2):
            label = get(f"button{n}_text")
            url = get(f"button{n}_url")
            if label and url:
                buttons.append({"label": label, "url": url})

        party_size = None
        if self.check_party.get_active():
            party_size = [int(self.spin_party_current.get_value()), int(self.spin_party_max.get_value())]

        activity_name = self.combos["activity_type"].get_active_text()
        payload = dict(
            activity_type=ACTIVITY_TYPES.get(activity_name, ActivityType.PLAYING),
            state=state,
            state_url=get("state_url"),
            details=details,
            details_url=get("details_url"),
            name=get("name"),
            start=start,
            end=end,
            large_image=get("large_image"),
            large_text=get("large_text"),
            large_url=get("large_url"),
            small_image=get("small_image"),
            small_text=get("small_text"),
            small_url=get("small_url"),
            party_size=party_size,
            buttons=buttons or None,
        )
        return payload

    def on_connect(self, _btn=None):
        client_id = self.entries["client_id"].get_text().strip()
        if not client_id:
            self.set_status("Enter a Discord Application ID first.")
            return
        try:
            self.rpc = Presence(client_id)
            self.rpc.connect()
            self.connected = True
            self.connected_at = now_ts()
            self.discord_user = getattr(self.rpc, "user", None)
            self.btn_connect.set_sensitive(False)
            self.btn_disconnect.set_sensitive(True)
            self.set_status("Connected. Click 'Update Presence' or wait for auto-refresh.")
            self.on_update_clicked()
            self.start_background_loop()
        except Exception as exc:
            self.connected = False
            self.set_status(f"Connection failed: {exc}")

    def on_disconnect(self, _btn=None):
        self.stop_background_loop()
        if self.rpc:
            try:
                self.rpc.close()
            except Exception:
                pass
        self.rpc = None
        self.connected = False
        self.btn_connect.set_sensitive(True)
        self.btn_disconnect.set_sensitive(False)
        self.set_status("Disconnected.")

    def _filter_supported_kwargs(self, payload):
        # old pypresence versions don't have state_url/details_url/large_url/etc,
        # so drop whatever the installed version doesn't accept instead of crashing
        import inspect
        accepted = set(inspect.signature(self.rpc.update).parameters.keys())
        dropped = [k for k in payload if k not in accepted and payload[k] is not None]
        filtered = {k: v for k, v in payload.items() if k in accepted}
        return filtered, dropped

    def on_update_clicked(self, _btn=None):
        if not self.connected or not self.rpc:
            self.set_status("Not connected - click Connect first.")
            return
        try:
            payload = self.build_payload()
            payload, dropped = self._filter_supported_kwargs(payload)
            self.rpc.update(**payload)
            if dropped:
                self.set_status(
                    "Updated (some fields ignored - upgrade pypresence for full support: "
                    + ", ".join(dropped) + ")"
                )
                return
            self.last_update_at = now_ts()
            self.set_status(f"Presence updated at {datetime.now().strftime('%H:%M:%S')}")
        except PyPresenceException as exc:
            self.set_status(f"Update failed: {exc}")
        except Exception:
            self.set_status("Update failed - see terminal for details.")
            traceback.print_exc()

    def start_background_loop(self):
        self.stop_event.clear()

        def loop():
            while not self.stop_event.wait(UPDATE_INTERVAL_SECONDS):
                if self.connected and self.check_autoupdate.get_active():
                    GLib.idle_add(self.on_update_clicked)

        self.update_thread = threading.Thread(target=loop, daemon=True)
        self.update_thread.start()

    def stop_background_loop(self):
        self.stop_event.set()

    def tick_clock(self):
        # Keeps {time}/{date} tokens meaningful even without forcing extra
        # Discord updates; the actual RPC push still respects the interval.
        return True

    def set_status(self, text):
        prefix = "Connected" if self.connected else "Not connected"
        GLib.idle_add(self.status_label.set_text, f"{prefix} - {text}")

    # -- config --

    def collect_config(self):
        cfg = {k: e.get_text() for k, e in self.entries.items()}
        cfg["activity_type"] = self.combos["activity_type"].get_active_text()
        cfg["timestamp_mode"] = self.get_timestamp_mode()
        cfg["party_enabled"] = self.check_party.get_active()
        cfg["party_current"] = self.spin_party_current.get_value()
        cfg["party_max"] = self.spin_party_max.get_value()
        cfg["autoupdate"] = self.check_autoupdate.get_active()
        return cfg

    def apply_config(self, cfg):
        for k, v in cfg.items():
            if k in self.entries:
                self.entries[k].set_text(str(v))
        if "activity_type" in cfg and cfg["activity_type"] in ACTIVITY_TYPES:
            self.combos["activity_type"].set_active(list(ACTIVITY_TYPES.keys()).index(cfg["activity_type"]))
        if cfg.get("timestamp_mode") in self.ts_radios:
            self.ts_radios[cfg["timestamp_mode"]].set_active(True)
        self.check_party.set_active(bool(cfg.get("party_enabled", False)))
        self.spin_party_current.set_value(float(cfg.get("party_current", 0)))
        self.spin_party_max.set_value(float(cfg.get("party_max", 0)))
        self.check_autoupdate.set_active(bool(cfg.get("autoupdate", True)))

    def save_config(self, path=CONFIG_FILE):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.collect_config(), f, indent=2)

    def load_config(self, path=CONFIG_FILE):
        if os.path.exists(path):
            try:
                with open(path) as f:
                    self.apply_config(json.load(f))
            except Exception:
                pass

    def on_save_preset_as(self, _item):
        dialog = Gtk.FileChooserDialog(
            title="Save Preset", parent=self, action=Gtk.FileChooserAction.SAVE)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        dialog.set_current_name("preset.json")
        if dialog.run() == Gtk.ResponseType.OK:
            self.save_config(dialog.get_filename())
        dialog.destroy()

    def on_load_preset(self, _item):
        dialog = Gtk.FileChooserDialog(
            title="Load Preset", parent=self, action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if dialog.run() == Gtk.ResponseType.OK:
            self.load_config(dialog.get_filename())
        dialog.destroy()

    def on_about(self, _item):
        dialog = Gtk.AboutDialog(transient_for=self)
        dialog.set_program_name(APP_NAME)
        dialog.set_version(APP_VERSION)
        dialog.set_comments("Set a fully custom Discord Rich Presence status without running a game.")
        dialog.set_website("https://github.com/")
        dialog.run()
        dialog.destroy()

    def on_quit(self, *_args):
        self.save_config()
        self.on_disconnect()
        Gtk.main_quit()


def main():
    GLib.set_prgname("seosuminrpc")
    win = SeoSuMinRPCWindow()
    win.connect("delete-event", Gtk.main_quit)
    Gtk.main()


if __name__ == "__main__":
    main()
