"""Altı slaytlık, kaynak CSV/JSON verilerine bağlı sunumu üretir."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from PIL import Image


KOK = Path(__file__).resolve().parents[1]
OUT = KOK / "sunum" / "baret_tespiti_sunum.pptx"
FONT = "Arial"  # Windows ve LibreOffice (Liberation Sans) aynı ölçülerle çizer
NAVY = RGBColor(16, 42, 67)
TEAL = RGBColor(10, 122, 138)
AMBER = RGBColor(226, 139, 26)
YELLOW = RGBColor(245, 190, 30)
RED = RGBColor(196, 64, 52)
MUTED = RGBColor(96, 112, 125)
LINE = RGBColor(219, 227, 233)
PALE = RGBColor(244, 247, 249)
CARD = RGBColor(250, 252, 253)
WHITE = RGBColor(255, 255, 255)
ORANGE = AMBER


def csv_rows(path: str) -> list[dict[str, str]]:
    with (KOK / path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


temel = {(r["kimlik"], r["yontem"]): r for r in csv_rows("sonuclar/temel_sonuclar.csv")}
blur = {(r["kimlik"], r["sigma"], r["yontem"]): r
        for r in csv_rows("sonuclar/bulaniklik/bulaniklik_sonuclari.csv")}
olcek = {(r["kimlik"], r["olcek"], r["yontem"]): r
         for r in csv_rows("sonuclar/olcek/olcek_sonuclari.csv")}
geri = {(r["kimlik"], r["olcek"]): r for r in csv_rows("sonuclar/olcek/geri_buyutme.csv")}
ozet = json.loads((KOK / "sonuclar/ozet.json").read_text(encoding="utf-8"))
ayar = json.loads((KOK / "ayarlar/deney_ayarlari.json").read_text(encoding="utf-8"))
tahminler = csv_rows("belgeler/tahminler.csv")
assert {r["uye"] for r in tahminler} == {"Nesli", "Omar", "Derviş", "Ahmet", "Efe", "Murathan"}
assert ayar["renk_araliklari"]["dondurulmus"] and ayar["karar_kurali"]["dondurulmus"]
assert ayar["karar_kurali"]["en_az_renk_alani_yuzde"] == 2.5
assert ayar["karar_kurali"]["en_az_bas_ortusmesi_yuzde"] == 5.0
assert ayar["bulaniklik"]["cekirdek"] == [15, 15]
assert ayar["bulaniklik"]["sigma_degerleri"] == [0, 0.5, 1.5, 3.0]
assert ozet["bulaniklik_sinif_degisimi"] == [] and ozet["olcek_sinif_degisimi"] == []
assert (ozet["RGB"]["sinif_dogru"], ozet["HSV"]["sinif_dogru"]) == (1, 2)
assert tuple(int(ozet["RGB"][k]) for k in ("tp", "fp", "fn")) == (1, 45, 3)
assert tuple(int(ozet["HSV"][k]) for k in ("tp", "fp", "fn")) == (3, 36, 1)
assert [blur["K2", s, "RGB"]["bas_ortusmesi_yuzde"] for s in ("0", "3.0")] == ["17.74", "14.91"]
assert [blur["K2", s, "HSV"]["bas_ortusmesi_yuzde"] for s in ("0", "3.0")] == ["17.88", "22.85"]
assert [(olcek["K2", s, "HSV"]["tp"], olcek["K2", s, "HSV"]["fn"]) for s in ("1.0", "0.5")] == [("1", "1"), ("0", "2")]
assert geri["K2", "0.25"]["psnr_db"] == "27.52"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]
TOPLAM = 6


def shape(slide, kind, x, y, w, h, fill, line=None, radius=None):
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(0.75)
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    sh.shadow.inherit = False
    return sh


def rect(slide, x, y, w, h, color):
    return shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, color)


def card(slide, x, y, w, h, fill=CARD, line=LINE, radius=0.06):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, radius)


def txt(slide, text, x, y, w, h, size=20, color=NAVY, bold=False, align=None, anchor=MSO_ANCHOR.MIDDLE, spacing=3):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    for side in ("left", "right", "top", "bottom"):
        setattr(frame, f"margin_{side}", Inches(0.02))
    frame.vertical_anchor = anchor
    for i, line in enumerate(text.split("\n")):
        para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        para.text = line
        para.space_after = Pt(spacing)
        if align is not None:
            para.alignment = align
        for run in para.runs:
            run.font.name = FONT
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
    return box


def chip(slide, text, x, y, w, fill, color=WHITE, size=13, h=0.38):
    pill = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, None, 0.5)
    tf = pill.text_frame
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    for run in p.runs:
        run.font.name = FONT
        run.font.size = Pt(size)
        run.font.bold = True
        run.font.color.rgb = color
    return pill


def numara(slide, n, x, y, d=0.46, fill=TEAL):
    c = shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill)
    tf = c.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(0))
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = str(n)
    p.alignment = PP_ALIGN.CENTER
    for run in p.runs:
        run.font.name = FONT
        run.font.size = Pt(15)
        run.font.bold = True
        run.font.color.rgb = WHITE
    return c


def stat(slide, deger, etiket, x, y, w, h, renk=TEAL, deger_boyut=30):
    card(slide, x, y, w, h)
    rect(slide, x, y + 0.12, 0.07, h - 0.24, renk)
    txt(slide, deger, x + 0.22, y + 0.08, w - 0.32, h * 0.58, deger_boyut, renk, True, anchor=MSO_ANCHOR.BOTTOM)
    txt(slide, etiket, x + 0.22, y + h * 0.62, w - 0.32, h * 0.32, 12, MUTED, anchor=MSO_ANCHOR.TOP)


def picture(slide, rel, x, y, w, h, cerceve=True):
    path = KOK / rel
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(w / iw, h / ih)
    pw, ph = iw * ratio, ih * ratio
    px, py = x + (w - pw) / 2, y + (h - ph) / 2
    if cerceve:
        card(slide, px - 0.08, py - 0.08, pw + 0.16, ph + 0.16, WHITE, LINE, 0.03)
    return slide.shapes.add_picture(str(path), Inches(px), Inches(py), width=Inches(pw), height=Inches(ph))


def base(ust, title: str, number: int, speaker: str, minutes: int):
    s = prs.slides.add_slide(blank)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    rect(s, 0, 0, 13.333, 0.10, NAVY)
    rect(s, 0, 0.10, 2.2, 0.05, YELLOW)
    txt(s, ust.upper(), 0.60, 0.36, 9.0, 0.30, 12, TEAL, True)
    txt(s, title, 0.60, 0.62, 11.2, 0.62, 30, NAVY, True)
    rect(s, 0.62, 1.27, 0.9, 0.05, AMBER)
    rect(s, 0, 7.02, 13.333, 0.48, PALE)
    txt(s, "YZM 411 Bilgisayarlı Görü  ·  Baret Tespiti ve Sınıflandırması", 0.60, 7.10, 6.6, 0.32, 11, MUTED)
    chip(s, f"{speaker}  ·  {minutes} dk", 8.75, 7.07, 3.0, NAVY, WHITE, 11, 0.34)
    txt(s, f"{number} / {TOPLAM}", 11.95, 7.10, 0.8, 0.32, 11, MUTED, True, align=PP_ALIGN.RIGHT)
    return s


def notes(slide, body: str):
    slide.notes_slide.notes_text_frame.text = body.strip()


SINIF = {"basta_baret": "Başta baret", "baret_var_basta_degil": "Başta değil", "baret_yok": "Baret yok", "belirsiz": "Belirsiz"}

# 1 — Problem ve veri
s = base("01 · Problem ve veri", "Baret var mı? Başta mı?", 1, "Nesli", 4)
picture(s, "sunum/gorseller/alti_goruntu_anotasyon.png", 4.95, 1.55, 7.75, 5.2)
txt(s, "Bir İSG kamerasının “baretsiz çalışan” uyarısı için iki karar:", 0.60, 1.55, 4.1, 0.70, 15, MUTED, anchor=MSO_ANCHOR.TOP)
numara(s, 1, 0.62, 2.30)
txt(s, "Görüntüde baret var mı?", 1.20, 2.27, 3.5, 0.52, 18, NAVY, True)
numara(s, 2, 0.62, 2.95)
txt(s, "Baret başta mı?", 1.20, 2.92, 3.5, 0.52, 18, NAVY, True)
txt(s, "DÖRT SINIF", 0.62, 3.70, 3.0, 0.30, 11, TEAL, True)
chip(s, "Başta baret", 0.62, 4.05, 1.95, TEAL)
chip(s, "Başta değil", 2.65, 4.05, 1.95, AMBER)
chip(s, "Baret yok", 0.62, 4.53, 1.95, RED)
chip(s, "Belirsiz", 2.65, 4.53, 1.95, MUTED)
stat(s, "2 + 4", "geliştirme + kontrol", 0.62, 5.18, 1.95, 1.05, TEAL, 26)
stat(s, "Renk", "tabanlı · dedektör yok", 2.65, 5.18, 1.95, 1.05, AMBER, 26)
notes(s, """NESLİ — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Önce altı görüntüyü G1 ve G2 geliştirme, K1 ile K4 arasını kontrol olarak ayırdım. Baş bölgesini ve gerçek baret kutularını yöntem sonuçlarını görmeden elle işaretledim. Dört sınıfımız başta baret, baret var ama başta değil, baret yok ve baş görünmüyorsa belirsizdir. K4'te baret elde olduğu için “başta değil” etiketledim. Ön tahminimde karanlık ve küçük baretlerin renk yöntemlerini zorlayacağını yazmıştım; o sıradaki eski K2 artık güncel K1, eski küçük baret K3 ise güncel K2. Bu eşlemeyi tahmini değiştirmeden kullanıyorum.

VERİ VE SINIFLAR (kalan süre)
G1 sarı baretli gündüz örneği, G2 kumaş şapkalı ve baretsiz geliştirme örneğidir. Kontrolde K1 loş, K2 küçük ve uzak, K3 sarı iş makinesinin yanlış alarm riski yarattığı baretsiz sahne, K4 ise elde baret örneğidir. Turkuaz kutu hedef baş ROI'sini, sarı kutu gerçek bareti gösterir. K2'nin baş ROI ve iki baret kutusu JSON'daki güncel etiketlerden çizilmiştir. Kaynaklar ve lisanslar veri/kaynaklar.csv içinde kayıtlıdır: dört Pexels fotoğrafı Pexels lisansı, G2 ve K2 Roboflow CHV kaydı CC BY 4.0. Altı görüntü, genelleme için yeterli bir örneklem değildir.

Kaynak: veri/kaynaklar.csv; etiketler/gercek_etiketler.json; belgeler/tahminler.csv (nesli_rgb_hsv_baseline).""")

# 2 — Renk yöntemi
s = base("02 · RGB ve HSV renk maskesi", "Aynı görüntü, iki renk yöntemi", 2, "Omar · Derviş", 4)
picture(s, "sunum/gorseller/sekiz_maske.png", 0.70, 1.55, 8.55, 4.60)
stat(s, "1 / 4", "RGB sınıf doğru", 9.65, 1.55, 3.05, 1.12, TEAL)
stat(s, "2 / 4", "HSV sınıf doğru", 9.65, 2.80, 3.05, 1.12, AMBER)
card(s, 9.65, 4.05, 3.05, 2.10)
txt(s, "KARAR KURALI", 9.85, 4.14, 2.7, 0.28, 11, TEAL, True)
txt(s, "Baş yok → belirsiz\nAlan < %2,5 → baret yok\nBaş örtüşmesi ≥ %5 → başta\nAksi → başta değil",
    9.85, 4.45, 2.75, 1.62, 13, NAVY, anchor=MSO_ANCHOR.TOP, spacing=5)
txt(s, "Aralıklar yalnızca G1/G2'de seçildi ve kontrol öncesi donduruldu.  RGB [180,140,0]–[255,255,120]  ·  HSV [18,120,80]–[30,255,255]",
    0.70, 6.32, 12.0, 0.36, 12, MUTED)
notes(s, """OMAR — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
RGB'de sarı baret rengini sabit alt ve üst kanal sınırlarıyla seçtim. Güncel ortak aralık alt 180, 140, 0 ve üst 255, 255, 120; bu aralık geliştirme görüntülerinde seçilip kontrol öncesi donduruldu. Tahminimde sabit RGB'nin loş ışıkta ve küçük uzaktaki barette zorlanacağını, eldeki baretin de yanlış baş kararı üretebileceğini yazmıştım. Kontrolde K1 ve K2 gerçekten “baret yok” tahmini aldı; K4 ise doğru biçimde “baret var, başta değil” çıktı. K3'te sarı iş makinesi RGB maskesinde yüzde 2,65 alan oluşturdu ve yanlış alarm doğurdu. Sonuç dört kontrolden biri doğru; daha geniş bir başarı iddiası değil.

DERVİŞ — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
HSV renk tonu, doygunluk ve parlaklığı ayrı ele alıyor. Dondurulmuş OpenCV aralığımız alt 18, 120, 80; üst 30, 255, 255. Ön tahminimde bunun değişen aydınlatmada RGB'den daha iyi seçim yapabileceğini, yine de karanlık ve benzer renkli nesnelerin hata yaratacağını öngörmüştüm. Güncel kontrolde HSV iki görüntüyü doğru sınıflandırdı: K3'te toplam renkli alan yüzde 1,46 ile alan eşiğinin altında kaldı, K4'te eldeki baret baş ROI'sine girmedi. Ancak K1 ve K2 yine “baret yok” çıktı. K2'de ROI örtüşmesi yüzde 17,88 olsa bile toplam maske alanı yalnızca yüzde 0,03.

ORTAK KURAL VE GÖRSELİN OKUNMASI
Sekiz görselin ilk satırı RGB, ikinci satırı HSV maskesidir. Turkuaz ve turuncu vurgular maskenin seçtiği piksellerdir; altındaki yüzdeler tüm görüntüye göre CSV'deki gerçek maske alanıdır. Önce baş ROI'nin varlığı, sonra yüzde 2,5 toplam alan, ardından yüzde 5 ROI örtüşmesi sınanır. Görüntü sınıfı doğruluğu ile aday kutu TP/FP/FN sayısı aynı ölçü değildir.

Kaynak: ayarlar/deney_ayarlari.json; sonuclar/temel_sonuclar.csv; sonuclar/ozet.json; belgeler/tahminler.csv (rgb_baseline, dervis_hsv_baseline).""")

# 3 — Bulanıklık ve ölçek
s = base("03 · Tek değişkenli deneyler", "Ön işleme kararı değiştirmedi, kutuları etkiledi", 3, "Ahmet · Efe", 4)
for x, kim, renk in ((0.60, "AHMET · GAUSSIAN BLUR", TEAL), (6.80, "EFE · KÜÇÜLTME (RESIZE)", AMBER)):
    card(s, x, 1.55, 5.95, 5.22)
    chip(s, kim, x + 0.20, 1.70, 3.2, renk, WHITE, 12, 0.36)
picture(s, "sonuclar/bulaniklik/sunum/K2_bas_roi_ortusmesi.png", 0.78, 2.18, 5.60, 3.05)
picture(s, "sonuclar/olcek/K2_geri_buyutme.png", 6.98, 2.18, 5.60, 3.05)
txt(s, "K2 baş örtüşmesi, σ 0 → 3\nRGB %17,74 → %14,91   ·   HSV %17,88 → %22,85", 0.80, 5.40, 5.6, 0.80, 15, NAVY, True)
txt(s, "Değişken: σ = 0 / 0,5 / 1,5 / 3   ·   çekirdek 15×15", 0.80, 6.22, 5.6, 0.40, 12, MUTED)
txt(s, "K2 HSV TP/FN: 1/1 → 0/2 (×1 → ×0,5)\n×0,25 geri büyütme: PSNR 27,52 dB", 7.00, 5.40, 5.6, 0.80, 15, NAVY, True)
txt(s, "Değişken: ölçek ×1 / ×0,75 / ×0,5 / ×0,25   ·   INTER_AREA", 7.00, 6.22, 5.6, 0.40, 12, MUTED)
notes(s, """AHMET — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Gaussian Blur deneyimde 15'e 15 çekirdeği sabit tuttum; filtresiz sıfır referansı ile sigma 0,5, 1,5 ve 3 değerlerini karşılaştırdım. Tahminim küçük baretin baş örtüşmesinin yüksek sigmada azalabileceği ve maske değişiminin sınıfı etkileyebileceğiydi. Güncel küçük baret K2'de RGB örtüşmesi yüzde 17,74'ten 14,91'e düştü; HSV ise yüzde 17,88'den 22,85'e yükseldi. İki yöntemin etkisi aynı yönde değil. Toplam alan her düzeyde yüzde 2,5 eşiğinin çok altında olduğu için K2 her sigma seviyesinde “baret yok” kaldı. K1–K4'te iki yöntemde de sınıf değişimi yok; bu, sistemin güvenilir olduğu anlamına gelmez.

EFE — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Ben ölçek katsayısını 1, 0,75, 0,5 ve 0,25 olarak değiştirdim; INTER_AREA küçültme ve sabit renk/karar ayarlarını kullandım. Ön tahminimde küçük uzak baretin yarıya ve çeyreğe küçültmede kaçabileceğini, geri büyütmenin kayıp ayrıntıyı getirmeyeceğini yazdım. Güncel K2'de HSV için kutu düzeyindeki sonuç tam ölçekte bir TP, bir FN iken yarı ölçekte sıfır TP, iki FN oldu. Çeyrek ölçekte de sıfır TP, iki FN. Geri büyütme görseli kaybı gösteriyor; çeyrek ölçek için ölçülen PSNR 27,52 dB. Görüntü düzeyindeki sınıf kararları değişmedi. Sabit 50 piksel aday bileşen eşiği, sonraki kontrolde ayrıca incelenmeli.

İKİ DENEYİ BAĞLAYAN BULGU
Grafikler farklı deneyleri gösterir: solda sadece sigma, sağda sadece ölçek değişir. Her iki deneyde ortak RGB/HSV aralıkları ve karar kuralı sabit kaldı. Bu sonuçlar, değişmeyen sınıf kararının kutu tespiti veya küçük ayrıntılar da değişmediği anlamına gelmediğini gösterir.

Kaynak: sonuclar/bulaniklik/bulaniklik_sonuclari.csv; sonuclar/olcek/olcek_sonuclari.csv; sonuclar/olcek/geri_buyutme.csv; sonuclar/ozet.json; belgeler/tahminler.csv (ahmet_gaussian_blur, efe_olcek).""")

# 4 — Hata analizi
s = base("04 · Hata analizi ve TP / FP / FN", "Renkli bölge, baret nesnesi değildir", 4, "Murathan", 3)
picture(s, "sonuclar/kutular/K3_rgb.png", 0.70, 1.55, 6.95, 5.15)
chip(s, "K3 · gerçek baret yok", 8.00, 1.55, 3.1, RED, WHITE, 13, 0.40)
stat(s, "27 FP", "RGB · kural “baret var”", 8.00, 2.10, 2.30, 1.10, RED, 26)
stat(s, "33 FP", "HSV · sınıf doğru", 10.42, 2.10, 2.30, 1.10, AMBER, 26)
card(s, 8.00, 3.35, 4.72, 1.30)
txt(s, "K1–K4 TOPLAMI  (IoU ≥ 0,50)", 8.18, 3.42, 4.4, 0.28, 11, TEAL, True)
txt(s, "RGB   1 TP / 45 FP / 3 FN\nHSV   3 TP / 36 FP / 1 FN", 8.18, 3.74, 4.4, 0.82, 18, NAVY, True)
card(s, 8.00, 4.80, 4.72, 1.90, PALE, None)
txt(s, "NEDEN", 8.18, 4.88, 2.0, 0.28, 11, RED, True)
txt(s, "Yöntem şekle değil yalnızca renge bakıyor.", 8.18, 5.15, 4.4, 0.42, 14, NAVY)
txt(s, "SONRAKİ KONTROL", 8.18, 5.62, 3.0, 0.28, 11, TEAL, True)
txt(s, "Aday kutulara şekil ölçütü (en–boy, doluluk); G1/G2'de tanımlanıp K3'te yeniden ölçülür.", 8.18, 5.90, 4.4, 0.72, 13, NAVY, anchor=MSO_ANCHOR.TOP)
notes(s, """MURATHAN — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Ben renk maskelerinin bağlı bileşenlerinden aday kutular çıkardım. Elle çizilmiş gerçek baret kutularıyla IoU en az 0,50 olacak biçimde bire bir eşleştirdim: eşleşen TP, eşleşmeyen aday FP, bulunamayan gerçek baret FN. Ön tahminimde sarı ekipman ve yeleklerin yanlış kutu üreteceğini, elde tutulan baretin ise kutu olarak bulunsa da başta sayılmayacağını yazmıştım. K1–K4 toplamında RGB bir TP, kırk beş FP ve üç FN; HSV üç TP, otuz altı FP ve bir FN verdi. K4'te eldeki baret her iki yöntemde de TP, fakat görüntü sınıfı “baret var, başta değil”dir.

HATA ANALİZİ VE YÖNTEM
K3 görselinde kırmızı işaretli adayların çoğu sarı-turuncu iş makinesinden çıkıyor. K3'te gerçek baret olmadığı için RGB'nin 27, HSV'nin 33 kutusu yanlış pozitif. HSV görüntü düzeyinde doğru biçimde “baret yok” dese de kutu düzeyinde yanlış adaylar var. Ters yönde, K1 ve K2'de baret baş bölgesinde renkli pikseller verse de toplam maske alanı yüzde 2,5'in altında kalıyor; görüntü kararı “baret yok”. Kutu ve sınıf ölçülerini ayrı tutuyoruz. Burada eğitimli veya hazır bir nesne dedektörü kullanılmadı; sonuçlar renk maskesi ve ortak kurala aittir. Sonraki kontrolde baş çevresi alanı ve şekil ölçütleri G1/G2'de tanımlanabilir.

Kaynak: sonuclar/temel_sonuclar.csv; sonuclar/ozet.json; ayarlar/deney_ayarlari.json; belgeler/tahminler.csv (color_mask_box_eval).""")

# 5 — Sonuç tablosu ve canlı demo
s = base("05 · Sonuç tablosu ve canlı çalıştırma", "Sonuç tablosu ve canlı uygulama", 5, "Nesli · Murathan", 4)
KOSUL = {"K1": "Loş ışık", "K2": "Uzak, küçük", "K3": "Sarı makine", "K4": "Elde baret"}
basliklar = ["Görüntü", "Koşul", "Doğru sınıf", "Yöntem", "Kuralın sınıfı", "Maske alanı", "TP / FP / FN"]
satirlar = []
for kimlik in ("K1", "K2", "K3", "K4"):
    for yontem in ("RGB", "HSV"):
        r = temel[kimlik, yontem]
        satirlar.append([kimlik, KOSUL[kimlik], SINIF[r["dogru_sinif"]], yontem,
                         SINIF[r["kural_sinifi"]] + ("" if r["dogru_mu"] == "evet" else "  ✗"),
                         "%" + r["maske_alani_yuzde"].replace(".", ","), f"{r['tp']} / {r['fp']} / {r['fn']}"])
tablo = s.shapes.add_table(len(satirlar) + 1, len(basliklar), Inches(0.60), Inches(1.55),
                           Inches(8.05), Inches(4.95)).table
for j, w in enumerate([0.85, 1.25, 1.20, 0.85, 1.45, 1.05, 1.40]):
    tablo.columns[j].width = Inches(w)
for i, satir in enumerate([basliklar] + satirlar):
    for j, deger in enumerate(satir):
        hucre = tablo.cell(i, j)
        hucre.text = str(deger)
        hucre.margin_left = hucre.margin_right = Inches(0.04)
        hucre.vertical_anchor = MSO_ANCHOR.MIDDLE
        para = hucre.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        for run in para.runs:
            run.font.name = FONT
            run.font.size = Pt(12)
            run.font.bold = i == 0 or j == 0 or "✗" in str(deger)
            run.font.color.rgb = WHITE if i == 0 else (RED if "✗" in str(deger) else NAVY)
        hucre.fill.solid()
        hucre.fill.fore_color.rgb = NAVY if i == 0 else (PALE if (i - 1) // 2 % 2 == 0 else WHITE)
txt(s, "✗ kuralın sınıfı yanlış  ·  sınıf doğruluğu ve kutu sayımı ayrı ölçülerdir", 0.62, 6.55, 8.0, 0.30, 11, MUTED)
card(s, 8.95, 1.55, 3.78, 5.15)
txt(s, "CANLI ÇALIŞTIRMA", 9.15, 1.68, 3.4, 0.30, 11, TEAL, True)
for k, adim in enumerate(["Görüntü ve baş ROI", "RGB / HSV maskesi", "Alan → örtüşme → sınıf", "Aday kutular"], start=1):
    numara(s, k, 9.15, 1.98 + (k - 1) * 0.68, 0.44)
    txt(s, adim, 9.72, 1.98 + (k - 1) * 0.68, 2.9, 0.44, 15, NAVY, True)
kod = card(s, 9.12, 4.80, 3.45, 0.80, NAVY, None, 0.10)
txt(s, "python betikler/canli_demo.py K3", 9.25, 4.86, 3.25, 0.68, 13, YELLOW, True)
txt(s, "Yeni görüntüde baş ROI fareyle seçilir; etiket yoksa TP/FP/FN hesaplanmaz.", 9.15, 5.75, 3.4, 0.80, 11, MUTED, anchor=MSO_ANCHOR.TOP)
notes(s, """SONUÇ TABLOSU (yönerge 8b)
Soldaki tablo hocanın istediği sütunları taşır: görüntü, koşul, doğru sınıf, kuralın sınıfı, maske alanı ve TP/FP/FN. Sınıf doğruluğu RGB'de 1/4, HSV'de 2/4; kutu düzeyinde RGB 1/45/3, HSV 3/36/1. İki ölçü ayrı tutulur. Tablo sonuclar/sonuc_tablosu.md dosyasıyla aynıdır.

CANLI UYGULAMA — NESLİ VE MURATHAN (yaklaşık 4 dakika)
Öğretim elemanının seçtiği görüntüyü betikler/canli_demo.py dosyasına vereceğiz. Veri setindeki K1, K2, K3 veya K4 kimliğiyle çağrılırsa kayıtlı baş ROI ve gerçek kutular okunur. Dosya yolu verilirse baş bölgesi ekranda fareyle seçilir; baş görünmüyorsa Esc ile belirsiz kararı verilebilir. Yeni görüntüde gerçek etiket bulunmadığı için doğru/yanlış, TP/FP/FN veya başarı oranı üretmeyeceğiz.

Önce orijinal görüntüyü ve hedef baş ROI'sini gösterin. Ardından RGB ve HSV maske bindirmelerini, tüm görüntüdeki renkli alan yüzdesini ve baş ROI örtüşmesini ayrı ayrı okuyun. Kural sırayla baş ROI'nin varlığını, yüzde 2,5 alan sınırını ve yüzde 5 örtüşme sınırını kullanır. Son olarak renk maskesinden çıkan aday kutuları gösterin; bunların hazır bir dedektör çıktısı olmadığını vurgulayın. Öğretim elemanı mevcut K3'ü seçerse RGB'nin benzer renkli makinede yanlış alarm verdiğini gösteren mevcut sonuca bağlayın; yeni bir görüntü seçerse o anki çıktıyı önceden bilinmeyen bir sonuç olarak yorumlayın. Demo için gerekirse defterler/00_canli_demo.ipynb kullanılabilir, fakat sunum slaytlarla yürür.

Kaynak: sonuclar/temel_sonuclar.csv; sonuclar/sonuc_tablosu.md; betikler/canli_demo.py; kaynak/analiz.py; ayarlar/deney_ayarlari.json.""")

# 6 — Sınırlılık ve sonraki adım
s = base("06 · Sınırlılık ve sonraki adım", "Renk, nesne kimliği değildir", 6, "Grup", 1)
picture(s, "sonuclar/kutular/K2_rgb.png", 0.70, 1.55, 6.30, 5.15)
txt(s, "K2'de baş örtüşmesi yüksek, toplam alan çok küçük", 7.40, 1.55, 5.3, 0.85, 19, NAVY, True)
stat(s, "%0,02–0,04", "toplam maske alanı  <  %2,5 eşik  →  “baret yok”", 7.40, 2.50, 5.30, 1.25, RED, 30)
txt(s, "SONRAKİ KONTROL", 7.40, 4.00, 3.0, 0.30, 11, TEAL, True)
for k, madde in enumerate(["Alanı baş ROI çevresinde hesaplamak", "Aday kutulara şekil ölçütleri", "Daha büyük bağımsız veri setinde, aynı dondurulmuş ayarlarla"], start=1):
    numara(s, k, 7.40, 4.38 + (k - 1) * 0.72, 0.44, AMBER)
    txt(s, madde, 7.98, 4.36 + (k - 1) * 0.72, 4.75, 0.50, 15, NAVY)
txt(s, "Altı görüntülük eğitim prototipi; saha güvenilirliği iddia edilmez.", 7.40, 6.45, 5.3, 0.30, 11, MUTED)
notes(s, """SONUÇ VE SINIRLILIKLAR (yaklaşık 1 dakika)
Bu çalışma sarı piksellerin varlığını ölçüyor; sarı bir bölgenin gerçekten baret nesnesi olduğunu kanıtlamıyor. K3'teki iş makinesi yanlış kutular üretti. K2'de ise baş ROI örtüşmesi yüksek olmasına rağmen tüm görüntüye göre maske alanı yüzde 0,02 ile 0,04 arasında; ortak yüzde 2,5 sınırı önce uygulandığı için karar “baret yok”. Gaussian Blur ve ölçek değişse bile sınıfın aynı kalması sağlamlık kanıtı değildir. Bir sonraki deneyde alanı baş ROI çevresinde ölçmeyi ve aday kutuların şeklini değerlendirmeyi öneriyoruz. Yeni kural geliştirme görüntülerinde tanımlanıp daha büyük bağımsız veri setinde sınanmalı. Altı görüntüyle saha güvenilirliği iddia etmiyoruz.

Kaynak: sonuclar/bulaniklik/bulaniklik_sonuclari.csv; sonuclar/temel_sonuclar.csv; ayarlar/deney_ayarlari.json; etiketler/gercek_etiketler.json.""")

assert len(prs.slides) == TOPLAM
prs.save(OUT)
print(OUT.relative_to(KOK))
