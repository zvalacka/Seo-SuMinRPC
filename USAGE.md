# Kullanım Kılavuzu

Bu doküman, uygulamadaki her alanın ne işe yaradığını ve nasıl
doldurulacağını anlatır.

## 1. Discord Application ID nasıl alınır

Programın çalışması için önce Discord'un geliştirici panelinde kendi
"uygulamanı" oluşturman gerekiyor (ücretsiz, 2 dakika sürer).

1. https://discord.com/developers/applications adresine git, Discord hesabınla giriş yap
2. Sağ üstten **New Application** butonuna bas
3. Uygulamaya bir isim ver — bu isim, Discord profilinde
   **"Playing `<isim>`"** yazısında görünecek isimdir (istediğin gibi
   değiştirebilirsin, örn. "maximmax42.ru")
4. Oluşturduktan sonra açılan **General Information** sayfasında
   **APPLICATION ID** yazan yerdeki uzun sayıyı kopyala
5. Programdaki **Application ID** kutusuna bu sayıyı yapıştır

Bu ID, programın "hangi kimlikle" Discord'a bağlanacağını belirler. Herkese
açık paylaşılabilir, gizli bir bilgi değildir.

## 2. Type (aktivite tipi)

Discord profilinde durumun nasıl başlayacağını belirler:

| Seçim | Discord'da görünüm |
|---|---|
| Playing | "Oynuyor: ..." |
| Listening | "Dinliyor: ..." |
| Watching | "İzliyor: ..." |
| Competing | "Yarışıyor: ..." |

## 3. Details / State

Bunlar Discord profilinde görünen iki satırlık metin. Details üstte, State
altta çıkar.

Her ikisinin yanındaki **URL** kutusu isteğe bağlıdır — doldurursan, o
satırın yazısı Discord'da tıklanabilir bir link olur. Boş bırakırsan sadece
düz yazı olarak görünür.

İçlerine `{time}` yazarsan güncel saatle, `{date}` yazarsan güncel tarihle
otomatik değiştirilir (her 15 saniyede bir program bunu tazeler).

## 4. Large Image / Small Image — en çok karıştırılan kısım

Bu bölümde üç kutu var, her birinin görevi farklı:

- **Key**: Gösterilecek resmin kendisi. İki şekilde doldurabilirsin:
  - **En kolay yol:** Doğrudan bir görsel linki yapıştır, örn:
    `https://i.imgur.com/xxxxx.png` (imgur, kendi sitendeki bir görsel,
    her yerden olabilir — sadece linkin sonunun `.png`/`.jpg`/`.gif` gibi
    bir görsele çıkması yeterli)
  - **Alternatif yol:** Discord Developer Portal'da uygulamanın
    **Rich Presence → Art Assets** sekmesine görsel yükleyip, o görsele
    verdiğin ismi (key) buraya yaz
- **Text**: Kullanıcı fareyle o resmin üzerine gelince çıkan küçük yazı
  (tooltip). Zorunlu değil.
- **URL**: Kullanıcı o resme **tıklarsa** açılacak link. Zorunlu değil, boş
  bırakılabilir — o zaman resim sadece görsel olarak durur, tıklanamaz.

Yani "URL kısmına ne yazayım" sorusunun cevabı: **eğer resme tıklandığında
bir siteye gitmesini istemiyorsan, boş bırak.** Resmin kendisini Key
kutusuna yazman yeterli.

## 5. Party

"6 / 9 kişi" gibi bir grup göstergesi eklemek istersen "Show party" kutusunu
işaretle, iki sayıyı gir. Gerçek bir oyun sunucusuna bağlanma/davet
özelliği yoktur, sadece görsel bir sayaçtır.

## 6. Timestamp (zaman damgası)

Discord'da durumun yanında "X dakikadır" gibi bir sayaç göstermek
istiyorsan seçeneklerden birini seç:

- **Since last connection**: Connect'e bastığın andan itibaren sayar
- **Since last presence update**: Update Presence'a en son bastığın andan itibaren sayar
- **Since program started**: Programı açtığın andan itibaren sayar
- **Your local time**: Sayaç göstermez, sadece Details/State'teki `{time}` gibi yer tutucular çalışır
- **Custom start/end timestamp**: Kendi belirlediğin tarih/saat aralığını kullanır (`YYYY-MM-DD HH:MM:SS` formatında)
- **No timestamp**: Hiçbir zaman bilgisi gösterilmez

## 7. Button 1 / Button 2

Discord profilinde durumun altında tıklanabilir buton(lar) gösterir.
**Label** butonun üzerindeki yazı, **URL** tıklanınca açılacak adres.
İkisi de doluysa buton görünür; biri boşsa o buton hiç gösterilmez.

## 8. Connect / Disconnect / Update Presence

1. **Connect**'e bas — program Discord masaüstü istemcisine bağlanır
   (Discord'un açık ve çalışıyor olması gerekir)
2. Alanları doldur
3. **Update Presence**'a bas — Discord profilindeki durumun anında güncellenir
4. "Auto-refresh every 15s" işaretliyse, alanlarını her değiştirdiğinde
   tekrar Update Presence'a basmana gerek kalmaz, program otomatik tazeler
5. Bitirince **Disconnect**'e bas, durumun Discord'dan kalkar

## Sık karşılaşılan durumlar

**"Resim görünmüyor"** → Key kutusuna yazdığın link gerçekten bir görsele
mi çıkıyor kontrol et (linki tarayıcıda aç, direkt resim açılmalı, bir web
sayfası değil). Ayrıca Discord istemcisini bir kere kapatıp açmak bazen
görselin önbellekten güncellenmesini sağlar.

**"URL'ye tıklayınca bir şey olmuyor"** → URL kutusunu boş bıraktıysan bu
normal, resim/yazı tıklanabilir olmaz.

**"Update Presence'a basınca hata veriyor"** → Discord masaüstü uygulamasının
açık olduğundan emin ol; kapalıysa program bağlanamaz.
