<img width="365" height="562" alt="a" src="https://github.com/user-attachments/assets/2b8542a0-bd44-43f4-b42d-46047c1ab9b5" />
<img width="757" height="885" alt="b" src="https://github.com/user-attachments/assets/69a9836d-dd81-44d2-b101-764aa1ecf860" />
# Seo-SuMinRPC

A native Linux GUI app for setting a fully custom Discord Rich Presence
status, built with GTK3 and `pypresence`. It talks to Discord's local IPC
socket (`$XDG_RUNTIME_DIR/discord-ipc-0`) directly, no game required.

> This project is not affiliated with Discord Inc. and is not an official
> Discord product.

## Features

- Details / State fields with optional clickable URLs
- Playing / Listening / Watching / Competing activity types
- Large and small images (asset key **or** a direct image URL) with
  clickable links
- Party size display (e.g. `6 / 9`)
- 6 timestamp modes: since last connection, since last presence update,
  since the app started, your local time, a custom start/end range, or none
- `{time}` and `{date}` placeholders (used in Details/State, refreshed on
  every update)
- Two clickable buttons (label + URL)
- Connect / Disconnect / Update Presence, plus automatic refresh (every 15s)
- Saves your settings to `~/.config/seosuminrpc/config.json`, and lets you
  save/load presets as files

## Installation

This section assumes no prior experience with Git or the command line —
just copy each command exactly as shown.

### Step 1: Get the code onto your computer

Open a terminal and run:

```bash
git clone https://github.com/zvalacka/Seo-SuMinRPC.git
cd Seo-SuMinRPC
```

This downloads the project into a new folder called `Seo-SuMinRPC` and
moves you into it. If you don't have `git` installed yet, install it
first:

```bash
# Arch / CachyOS / Manjaro
sudo pacman -S git

# Debian / Ubuntu
sudo apt install git

# Fedora
sudo dnf install git
```

then run the `git clone` command above again.

### Step 2: Install the system dependencies (GTK3 + PyGObject)

Pick the command matching your distro:

```bash
# Arch / CachyOS / Manjaro
sudo pacman -S python-gobject gtk3 python-pip

# Debian / Ubuntu
sudo apt install python3-gi gir1.2-gtk-3.0 python3-pip

# Fedora
sudo dnf install python3-gobject gtk3 python3-pip
```

### Step 3: Install the Python dependency

```bash
pip install --break-system-packages -r requirements.txt
```

### Step 4: Run it

```bash
python3 seosuminrpc.py
```

A window should open. That's it — you're running the app.

## Usage

For a full explanation of every field (especially the Large/Small Image
keys, the URL boxes, and the Timestamp modes), see [USAGE.md](USAGE.md).

## Getting a Discord Application ID

1. Go to https://discord.com/developers/applications
2. Click **New Application** and give it a name (this name is what shows up
   in Discord as **"Playing `<name>`"**)
3. Copy the **Application ID** from the **General Information** page and
   paste it into the app's **Application ID** field
4. For images, either upload art to **Rich Presence → Art Assets** in the
   Developer Portal and use that asset's key, or just paste a direct image
   URL straight into the **Key** field.

## Adding it to your app menu (optional)

```bash
chmod +x seosuminrpc.py
mkdir -p ~/.local/bin
ln -s "$(pwd)/seosuminrpc.py" ~/.local/bin/seosuminrpc
cp seosuminrpc.desktop ~/.local/share/applications/
```

## Known limitations

- The "Name" field (overriding the displayed app name) only works for
  certain approved Discord applications; it's not guaranteed to work
  everywhere.
- Party/Join/Spectate are cosmetic only — there's no real game server
  join/invite mechanism behind them.
- The Discord desktop client must be open and running (Rich Presence
  doesn't show through the web or mobile clients).

## License

MIT — see `LICENSE`.
