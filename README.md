# Seo SuMinRPC

Linux masaüstünde çalışan, GTK3 tabanlı bir Discord Rich Presence
düzenleyicisi. `pypresence` kütüphanesi üzerinden Discord'un yerel IPC
soketiyle (`$XDG_RUNTIME_DIR/discord-ipc-0`) konuşur, Details/State,
resimler, buton ve zaman damgası gibi her şeyi arayüzden ayarlamana izin
verir.

> Bu proje Discord Inc. ile bağlantılı değildir, resmi bir Discord ürünü
> değildir.

## Özellikler

- Details / State alanları ve tıklanabilir URL'ler
- Playing / Listening / Watching / Competing aktivite tipleri
- Büyük ve küçük resim (asset key **veya** doğrudan görsel URL'si) + tıklanabilir linkler
- Parti boyutu gösterimi (ör. `6 / 9`)
- 6 farklı zaman damgası modu: son bağlantıdan beri, son güncellemeden beri,
  program başladığından beri, yerel saat, özel başlangıç/bitiş, veya hiçbiri
- `{time}` ve `{date}` yer tutucuları (Details/State içinde kullanılırsa her
  güncellemede güncel saat/tarihle değiştirilir)
- İki adet tıklanabilir buton (etiket + URL)
- Connect / Disconnect / Update Presence ve otomatik yenileme (15 sn)
- Ayarları `~/.config/seosuminrpc/config.json` içine kaydeder, önceden
  hazırlanmış presetleri dosya olarak kaydedip yükleyebilirsiniz

## Kurulum

### 1. Sistem bağımlılıkları (GTK3 + PyGObject)

Debian/Ubuntu ve türevleri:
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 python3-pip
```

Fedora:
```bash
sudo dnf install python3-gobject gtk3 python3-pip
```

Arch:
```bash
sudo pacman -S python-gobject gtk3 python-pip
```

### 2. Python bağımlılığı

```bash
pip install --break-system-packages -r requirements.txt
```
(veya bir sanal ortam içinde `pip install -r requirements.txt`)

### 3. Çalıştırma

```bash
python3 seosuminrpc.py
```

## Kullanım

Her alanın ne işe yaradığını (özellikle Large/Small Image, URL kutuları ve
Timestamp seçenekleri) merak ediyorsan [USAGE.md](USAGE.md) dosyasına bak.

## Discord Application ID nasıl alınır?

1. https://discord.com/developers/applications adresine git
2. **New Application** ile bir uygulama oluştur (adı, Discord profilinde
   "Playing **<isim>**" kısmında görünecek isimdir)
3. **General Information** sayfasındaki **Application ID**'yi kopyala ve
   programdaki **Application ID** kutusuna yapıştır
4. Büyük/küçük resim için Discord Developer Portal'daki **Rich Presence →
   Art Assets** kısmına görsel yükleyip o görsele verdiğin ismi (key) "Key"
   alanına yazabilirsin — veya doğrudan bir görsel URL'si de girebilirsin.

## Masaüstü menüsüne ekleme (isteğe bağlı)

```bash
chmod +x seosuminrpc.py
mkdir -p ~/.local/bin
ln -s "$(pwd)/seosuminrpc.py" ~/.local/bin/seosuminrpc

mkdir -p ~/.local/share/icons/hicolor/256x256/apps
cp assets/icon.png ~/.local/share/icons/hicolor/256x256/apps/seosuminrpc.png
gtk-update-icon-cache ~/.local/share/icons/hicolor 2>/dev/null

cp seosuminrpc.desktop ~/.local/share/applications/
```

## Bilinen sınırlamalar

- "Name" alanı (görünen uygulama adını override etme) Discord tarafında
  yalnızca belirli onaylı uygulamalarda çalışır; her koşulda garanti değildir.
- Parti/Join/Spectate özellikleri sadece kozmetik gösterim sağlar; gerçek
  bir oyun sunucusuna bağlanma/davet mekanizması içermez.
- Discord masaüstü istemcisinin açık ve çalışıyor olması gerekir (web/mobil
  Discord üzerinden Rich Presence görünmez).

## Lisans

MIT — `LICENSE` dosyasına bakın.
