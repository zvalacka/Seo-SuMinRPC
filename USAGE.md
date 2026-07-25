# Usage Guide

This document explains what every field in the app does and how to fill
it in.

## 1. Getting a Discord Application ID

Before the app can do anything, you need to create your own "application"
in Discord's developer portal (free, takes about 2 minutes).

1. Go to https://discord.com/developers/applications and log in with your
   Discord account
2. Click **New Application** in the top right
3. Give it a name — this is exactly what will show up in Discord as
   **"Playing `<name>`"** (you can pick anything, e.g. "maximmax42.ru")
4. On the **General Information** page that opens, copy the long number
   next to **APPLICATION ID**
5. Paste that number into the **Application ID** field in the app

This ID is just an identifier for which Discord app you're connecting as.
It's fine to share it publicly — it's not a secret.

## 2. Type (activity type)

Controls how your status is phrased in Discord:

| Choice | Shows up as |
|---|---|
| Playing | "Playing ..." |
| Listening | "Listening to ..." |
| Watching | "Watching ..." |
| Competing | "Competing in ..." |

## 3. Details / State

These are the two lines of text shown on your Discord profile. Details is
the top line, State is the line below it.

The **URL** box next to each one is optional — fill it in and that line
becomes a clickable link in Discord. Leave it empty and it's just plain
text.

You can type `{time}` or `{date}` anywhere in these fields and they'll be
swapped for the current time/date automatically (refreshed every 15
seconds).

## 4. Large Image / Small Image — the part people get stuck on

There are three boxes here, each doing something different:

- **Key**: the actual image to display. Two ways to fill this in:
  - **Easiest:** paste a direct image link, e.g.
    `https://i.imgur.com/xxxxx.png` (imgur, your own site, anywhere works —
    as long as the link points straight to an image file, not a webpage)
  - **Alternative:** upload an image under your app's **Rich Presence →
    Art Assets** tab in the Developer Portal, then type the name (key) you
    gave it here
- **Text**: a small tooltip that appears when someone hovers over the
  image. Optional.
- **URL**: where clicking the image takes you. Optional — leave it blank
  and the image just sits there, not clickable.

So if you're wondering what to put in the URL box: **if you don't want
clicking the image to open a link, leave it empty.** The image itself only
needs the Key field filled in.

## 5. Party

Check "Show party" and enter two numbers if you want a "6 of 9" style
group indicator. There's no actual join/invite mechanism behind it — it's
purely cosmetic.

## 6. Timestamp

If you want a running "X minutes" counter next to your status, pick one of:

- **Since last connection**: counts from the moment you hit Connect
- **Since last presence update**: counts from your last Update Presence click
- **Since program started**: counts from when you launched the app
- **Your local time**: no counter, only `{time}`-style placeholders work
- **Custom start/end timestamp**: set your own date/time range
  (`YYYY-MM-DD HH:MM:SS` format)
- **No timestamp**: no time info shown at all

## 7. Button 1 / Button 2

Adds clickable buttons under your status on Discord. **Label** is the text
on the button, **URL** is where it goes. Both fields need to be filled in
for the button to appear; if either is empty, that button is skipped
entirely.

## 8. Connect / Disconnect / Update Presence

1. Click **Connect** — the app connects to your running Discord desktop
   client
2. Fill in the fields
3. Click **Update Presence** — your Discord status updates immediately
4. With "Auto-refresh every 15s" checked, you don't need to click Update
   Presence again after every change — it refreshes on its own
5. Click **Disconnect** when you're done, and your status clears from
   Discord

## Common issues

**"My image isn't showing up"** — check that the link you put in Key
actually points to an image (open it in your browser, it should load the
image directly, not a webpage). Restarting the Discord client sometimes
helps refresh a cached image too.

**"Nothing happens when I click the URL"** — if the URL box is empty,
that's expected, the image/text won't be clickable.

**"Update Presence throws an error"** — make sure the Discord desktop app
is actually open; the app can't connect if it's closed.
