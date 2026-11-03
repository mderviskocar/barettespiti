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
NAVY = RGBColor(18, 43, 64)
TEAL = RGBColor(7, 120, 136)
ORANGE = RGBColor(209, 105, 30)
MUTED = RGBColor(81, 100, 113)
PALE = RGBColor(245, 248, 250)
WHITE = RGBColor(255, 255, 255)


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


def rect(slide, x, y, w, h, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def txt(slide, text, x, y, w, h, size=20, color=NAVY, bold=False, align=None):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.02)
    frame.margin_right = Inches(0.02)
    frame.margin_top = Inches(0.01)
    frame.margin_bottom = Inches(0.01)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, line in enumerate(text.split("\n")):
        para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        para.text = line
        para.space_after = Pt(3)
        if align is not None:
            para.alignment = align
        for run in para.runs:
            run.font.name = FONT
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
    return shape


def picture(slide, rel, x, y, w, h):
    path = KOK / rel
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(w / iw, h / ih)
    pw, ph = iw * ratio, ih * ratio
    return slide.shapes.add_picture(str(path), Inches(x + (w - pw) / 2),
                                    Inches(y + (h - ph) / 2), width=Inches(pw), height=Inches(ph))


def base(title: str, number: int, speaker: str, minutes: int):
    s = prs.slides.add_slide(blank)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = WHITE
    rect(s, 0, 0, 0.15, 7.5, TEAL)
    txt(s, title, 0.53, 0.29, 12.0, 0.57, 31, NAVY, True)
    rect(s, 0.56, 0.94, 12.18, 0.026, RGBColor(215, 225, 231))
    txt(s, f"{speaker}  •  {minutes} dk", 0.55, 7.10, 11.8, 0.27, 11, MUTED)
    txt(s, f"{number} / 6", 12.1, 7.10, 0.65, 0.27, 11, MUTED, align=PP_ALIGN.RIGHT)
    return s


def notes(slide, body: str):
    slide.notes_slide.notes_text_frame.text = body.strip()


# 1 — Veri ve sınıflar
s = base("Baret var mı? Başta mı?", 1, "Nesli", 4)
picture(s, "sunum/gorseller/alti_goruntu_anotasyon.png", 0.56, 1.12, 12.18, 4.72)
txt(s, "2 geliştirme  +  4 kontrol görüntüsü", 0.69, 5.93, 6.0, 0.42, 22, TEAL, True)
txt(s, "Renk tabanlı başlangıç yöntemi · hazır dedektör yok", 7.05, 5.93, 5.7, 0.42, 18, ORANGE, True)
txt(s, "Başta baret  •  Başta değil  •  Baret yok  •  Belirsiz",
    0.69, 6.40, 11.9, 0.37, 18, NAVY)
notes(s, """
NESLİ — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Önce altı görüntüyü G1 ve G2 geliştirme, K1 ile K4 arasını kontrol olarak ayırdım. Baş bölgesini ve gerçek baret kutularını yöntem sonuçlarını görmeden elle işaretledim. Dört sınıfımız başta baret, baret var ama başta değil, baret yok ve baş görünmüyorsa belirsizdir. K4'te baret elde olduğu için “başta değil” etiketledim. Ön tahminimde karanlık ve küçük baretlerin renk yöntemlerini zorlayacağını yazmıştım; o sıradaki eski K2 artık güncel K1, eski küçük baret K3 ise güncel K2. Bu eşlemeyi tahmini değiştirmeden kullanıyorum.

VERİ VE SINIFLAR (kalan süre)
G1 sarı baretli gündüz örneği, G2 kumaş şapkalı ve baretsiz geliştirme örneğidir. Kontrolde K1 loş, K2 küçük ve uzak, K3 sarı iş makinesinin yanlış alarm riski yarattığı baretsiz sahne, K4 ise elde baret örneğidir. Turkuaz kutu hedef baş ROI'sini, sarı kutu gerçek bareti gösterir. K2'nin baş ROI ve iki baret kutusu JSON'daki güncel etiketlerden çizilmiştir. Kaynaklar ve lisanslar veri/kaynaklar.csv içinde kayıtlıdır: dört Pexels fotoğrafı Pexels lisansı, G2 ve K2 Roboflow CHV kaydı CC BY 4.0. Altı görüntü, genelleme için yeterli bir örneklem değildir.

Kaynak: veri/kaynaklar.csv; etiketler/gercek_etiketler.json; belgeler/tahminler.csv (nesli_rgb_hsv_baseline).
""")

# 2 — Maskeler
s = base("Aynı görüntü, iki renk yöntemi", 2, "Omar · Derviş", 4)
picture(s, "sunum/gorseller/sekiz_maske.png", 0.57, 1.12, 12.15, 4.58)
txt(s, "RGB  1/4 doğru", 0.72, 5.81, 3.0, 0.45, 25, TEAL, True)
txt(s, "HSV  2/4 doğru", 4.05, 5.81, 3.0, 0.45, 25, ORANGE, True)
txt(s, "Kural:  baş yok → belirsiz  |  alan <%2,5 → baret yok  |  baş örtüşmesi ≥%5 → başta baret  |  aksi → başta değil",
    0.72, 6.33, 12.0, 0.42, 15, NAVY)
notes(s, """
OMAR — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
RGB'de sarı baret rengini sabit alt ve üst kanal sınırlarıyla seçtim. Güncel ortak aralık alt 180, 140, 0 ve üst 255, 255, 120; bu aralık geliştirme görüntülerinde seçilip kontrol öncesi donduruldu. Tahminimde sabit RGB'nin loş ışıkta ve küçük uzaktaki barette zorlanacağını, eldeki baretin de yanlış baş kararı üretebileceğini yazmıştım. Kontrolde K1 ve K2 gerçekten “baret yok” tahmini aldı; K4 ise doğru biçimde “baret var, başta değil” çıktı. K3'te sarı iş makinesi RGB maskesinde yüzde 2,65 alan oluşturdu ve yanlış alarm doğurdu. Sonuç dört kontrolden biri doğru; daha geniş bir başarı iddiası değil.

DERVİŞ — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
HSV renk tonu, doygunluk ve parlaklığı ayrı ele alıyor. Dondurulmuş OpenCV aralığımız alt 18, 120, 80; üst 30, 255, 255. Ön tahminimde bunun değişen aydınlatmada RGB'den daha iyi seçim yapabileceğini, yine de karanlık ve benzer renkli nesnelerin hata yaratacağını öngörmüştüm. Güncel kontrolde HSV iki görüntüyü doğru sınıflandırdı: K3'te toplam renkli alan yüzde 1,46 ile alan eşiğinin altında kaldı, K4'te eldeki baret baş ROI'sine girmedi. Ancak K1 ve K2 yine “baret yok” çıktı. K2'de ROI örtüşmesi yüzde 17,88 olsa bile toplam maske alanı yalnızca yüzde 0,03.

ORTAK KURAL VE GÖRSELİN OKUNMASI
Sekiz görselin ilk satırı RGB, ikinci satırı HSV maskesidir. Turkuaz ve turuncu vurgular maskenin seçtiği piksellerdir; altındaki yüzdeler tüm görüntüye göre CSV'deki gerçek maske alanıdır. Önce baş ROI'nin varlığı, sonra yüzde 2,5 toplam alan, ardından yüzde 5 ROI örtüşmesi sınanır. Görüntü sınıfı doğruluğu ile aday kutu TP/FP/FN sayısı aynı ölçü değildir.

Kaynak: ayarlar/deney_ayarlari.json; sonuclar/temel_sonuclar.csv; sonuclar/ozet.json; belgeler/tahminler.csv (rgb_baseline, dervis_hsv_baseline).
""")

# 3 — İki ayrı deney
s = base("Ön işleme aynı kararı korudu; kutuları etkiledi", 3, "Ahmet · Efe", 4)
txt(s, "AHMET  /  GAUSSIAN BLUR", 0.66, 1.10, 6.0, 0.42, 20, TEAL, True)
txt(s, "EFE  /  RESIZE", 6.87, 1.10, 5.8, 0.42, 20, ORANGE, True)
rect(s, 6.65, 1.10, 0.025, 5.48, RGBColor(213, 225, 230))
picture(s, "sonuclar/bulaniklik/sunum/K2_bas_roi_ortusmesi.png", 0.58, 1.56, 5.98, 3.48)
picture(s, "sonuclar/olcek/K2_geri_buyutme.png", 6.81, 1.56, 5.91, 3.48)
txt(s, "σ 0→3: RGB %17,74→%14,91\nHSV %17,88→%22,85", 0.75, 5.13, 5.65, 0.85, 20, NAVY, True)
txt(s, "K2 HSV TP/FN: 1/1 → 0/2 (×1→×0,5)\n×0,25 geri büyütme: 27,52 dB", 6.88, 5.13, 5.72, 0.85, 20, NAVY, True)
txt(s, "Blur: 15×15; σ=0/0,5/1,5/3  •  Ölçek: ×1/×0,75/×0,5/×0,25  •  Sınıf değişimi yok",
    0.70, 6.35, 12.0, 0.38, 16, MUTED)
notes(s, """
AHMET — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Gaussian Blur deneyimde 15'e 15 çekirdeği sabit tuttum; filtresiz sıfır referansı ile sigma 0,5, 1,5 ve 3 değerlerini karşılaştırdım. Tahminim küçük baretin baş örtüşmesinin yüksek sigmada azalabileceği ve maske değişiminin sınıfı etkileyebileceğiydi. Güncel küçük baret K2'de RGB örtüşmesi yüzde 17,74'ten 14,91'e düştü; HSV ise yüzde 17,88'den 22,85'e yükseldi. İki yöntemin etkisi aynı yönde değil. Toplam alan her düzeyde yüzde 2,5 eşiğinin çok altında olduğu için K2 her sigma seviyesinde “baret yok” kaldı. K1–K4'te iki yöntemde de sınıf değişimi yok; bu, sistemin güvenilir olduğu anlamına gelmez.

EFE — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Ben ölçek katsayısını 1, 0,75, 0,5 ve 0,25 olarak değiştirdim; INTER_AREA küçültme ve sabit renk/karar ayarlarını kullandım. Ön tahminimde küçük uzak baretin yarıya ve çeyreğe küçültmede kaçabileceğini, geri büyütmenin kayıp ayrıntıyı getirmeyeceğini yazdım. Güncel K2'de HSV için kutu düzeyindeki sonuç tam ölçekte bir TP, bir FN iken yarı ölçekte sıfır TP, iki FN oldu. Çeyrek ölçekte de sıfır TP, iki FN. Geri büyütme görseli kaybı gösteriyor; çeyrek ölçek için ölçülen PSNR 27,52 dB. Görüntü düzeyindeki sınıf kararları değişmedi. Sabit 50 piksel aday bileşen eşiği, sonraki kontrolde ayrıca incelenmeli.

İKİ DENEYİ BAĞLAYAN BULGU
Grafikler farklı deneyleri gösterir: solda sadece sigma, sağda sadece ölçek değişir. Her iki deneyde ortak RGB/HSV aralıkları ve karar kuralı sabit kaldı. Bu sonuçlar, değişmeyen sınıf kararının kutu tespiti veya küçük ayrıntılar da değişmediği anlamına gelmediğini gösterir.

Kaynak: sonuclar/bulaniklik/bulaniklik_sonuclari.csv; sonuclar/olcek/olcek_sonuclari.csv; sonuclar/olcek/geri_buyutme.csv; sonuclar/ozet.json; belgeler/tahminler.csv (ahmet_gaussian_blur, efe_olcek).
""")

# 4 — Kutular ve hata
s = base("Renkli bölge, baret nesnesi değildir", 4, "Murathan", 3)
picture(s, "sonuclar/kutular/K3_rgb.png", 0.60, 1.20, 7.45, 5.42)
txt(s, "K3 · gerçek baret yok", 8.18, 1.48, 4.35, 0.5, 24, NAVY, True)
txt(s, "RGB 27 yanlış kutu\nHSV 33 yanlış kutu", 8.18, 2.18, 4.45, 1.25, 25, ORANGE, True)
rect(s, 8.20, 3.80, 4.20, 0.027, RGBColor(213, 225, 230))
txt(s, "K1–K4 toplamı", 8.18, 4.07, 4.45, 0.38, 18, MUTED, True)
txt(s, "RGB   1 TP / 45 FP / 3 FN\nHSV   3 TP / 36 FP / 1 FN", 8.18, 4.57, 4.50, 0.92, 21, NAVY, True)
txt(s, "Neden: yöntem yalnızca renge bakıyor.\nSonraki kontrol: aday kutulara şekil\nölçütü (en–boy, doluluk), G1/G2'de.", 8.18, 5.55, 4.50, 1.05, 15, MUTED)
notes(s, """
MURATHAN — BİREYSEL DENEY ANLATIMI (yaklaşık 1 dakika)
Ben renk maskelerinin bağlı bileşenlerinden aday kutular çıkardım. Elle çizilmiş gerçek baret kutularıyla IoU en az 0,50 olacak biçimde bire bir eşleştirdim: eşleşen TP, eşleşmeyen aday FP, bulunamayan gerçek baret FN. Ön tahminimde sarı ekipman ve yeleklerin yanlış kutu üreteceğini, elde tutulan baretin ise kutu olarak bulunsa da başta sayılmayacağını yazmıştım. K1–K4 toplamında RGB bir TP, kırk beş FP ve üç FN; HSV üç TP, otuz altı FP ve bir FN verdi. K4'te eldeki baret her iki yöntemde de TP, fakat görüntü sınıfı “baret var, başta değil”dir.

HATA ANALİZİ VE YÖNTEM
K3 görselinde kırmızı işaretli adayların çoğu sarı-turuncu iş makinesinden çıkıyor. K3'te gerçek baret olmadığı için RGB'nin 27, HSV'nin 33 kutusu yanlış pozitif. HSV görüntü düzeyinde doğru biçimde “baret yok” dese de kutu düzeyinde yanlış adaylar var. Ters yönde, K1 ve K2'de baret baş bölgesinde renkli pikseller verse de toplam maske alanı yüzde 2,5'in altında kalıyor; görüntü kararı “baret yok”. Kutu ve sınıf ölçülerini ayrı tutuyoruz. Burada eğitimli veya hazır bir nesne dedektörü kullanılmadı; sonuçlar renk maskesi ve ortak kurala aittir. Sonraki kontrolde baş çevresi alanı ve şekil ölçütleri G1/G2'de tanımlanabilir.

Kaynak: sonuclar/temel_sonuclar.csv; sonuclar/ozet.json; ayarlar/deney_ayarlari.json; belgeler/tahminler.csv (color_mask_box_eval).
""")

# 5 — Canlı demo
s = base("Sonuç tablosu ve canlı uygulama", 5, "Nesli · Murathan", 4)
SINIF = {"basta_baret": "Başta baret", "baret_var_basta_degil": "Başta değil", "baret_yok": "Baret yok", "belirsiz": "Belirsiz"}
KOSUL = {"K1": "Loş ışık", "K2": "Uzak, küçük", "K3": "Sarı makine", "K4": "Elde baret"}
basliklar = ["Görüntü", "Koşul", "Doğru sınıf", "Yöntem", "Kuralın sınıfı", "Maske alanı", "TP / FP / FN"]
satirlar = []
for kimlik in ("K1", "K2", "K3", "K4"):
    for yontem in ("RGB", "HSV"):
        r = temel[kimlik, yontem]
        satirlar.append([kimlik, KOSUL[kimlik], SINIF[r["dogru_sinif"]], yontem,
                         SINIF[r["kural_sinifi"]] + ("" if r["dogru_mu"] == "evet" else " ✗"),
                         "%" + r["maske_alani_yuzde"].replace(".", ","), f"{r['tp']} / {r['fp']} / {r['fn']}"])
tablo = s.shapes.add_table(len(satirlar) + 1, len(basliklar), Inches(0.58), Inches(1.18),
                           Inches(7.85), Inches(5.35)).table
genislik = [0.85, 1.20, 1.15, 0.80, 1.40, 1.05, 1.40]
for j, w in enumerate(genislik):
    tablo.columns[j].width = Inches(w)
for i, satir in enumerate([basliklar] + satirlar):
    for j, deger in enumerate(satir):
        hucre = tablo.cell(i, j)
        hucre.text = str(deger)
        hucre.margin_left = hucre.margin_right = Inches(0.04)
        para = hucre.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER
        for run in para.runs:
            run.font.name = FONT
            run.font.size = Pt(12 if i else 12)
            run.font.bold = i == 0 or j == 0
            run.font.color.rgb = WHITE if i == 0 else (ORANGE if "✗" in str(deger) else NAVY)
        hucre.fill.solid()
        hucre.fill.fore_color.rgb = TEAL if i == 0 else (PALE if (i - 1) // 2 % 2 == 0 else WHITE)
txt(s, "✗ = kuralın sınıfı yanlış  •  TP/FP/FN: IoU ≥ 0,50 (renk maskesi kutuları)", 0.60, 6.60, 7.9, 0.32, 11, MUTED)
txt(s, "1  Görüntü / baş ROI", 8.55, 1.45, 4.0, 0.48, 22, TEAL, True)
txt(s, "2  RGB ve HSV maskeleri", 8.55, 2.24, 4.0, 0.48, 22, TEAL, True)
txt(s, "3  Alan → örtüşme → sınıf", 8.55, 3.03, 4.1, 0.48, 22, TEAL, True)
txt(s, "4  Renk maskesi aday kutuları", 8.55, 3.82, 4.0, 0.75, 22, TEAL, True)
rect(s, 8.52, 5.12, 4.20, 0.93, PALE)
txt(s, "python betikler/canli_demo.py K3", 8.69, 5.25, 3.88, 0.65, 16, NAVY, True)
txt(s, "Yeni görüntüde etiket yoksa TP/FP/FN hesaplanmaz.", 8.55, 6.23, 4.12, 0.44, 13, MUTED)
notes(s, """
SONUÇ TABLOSU (yönerge 8b)
Soldaki tablo hocanın istediği sütunları taşır: görüntü, koşul, doğru sınıf, kuralın sınıfı, maske alanı ve TP/FP/FN. Sınıf doğruluğu RGB'de 1/4, HSV'de 2/4; kutu düzeyinde RGB 1/45/3, HSV 3/36/1. İki ölçü ayrı tutulur. Tablo sonuclar/sonuc_tablosu.md dosyasıyla aynıdır.

CANLI UYGULAMA — NESLİ VE MURATHAN (yaklaşık 4 dakika)
Öğretim elemanının seçtiği görüntüyü betikler/canli_demo.py dosyasına vereceğiz. Veri setindeki K1, K2, K3 veya K4 kimliğiyle çağrılırsa kayıtlı baş ROI ve gerçek kutular okunur. Dosya yolu verilirse baş bölgesi ekranda fareyle seçilir; baş görünmüyorsa Esc ile belirsiz kararı verilebilir. Yeni görüntüde gerçek etiket bulunmadığı için doğru/yanlış, TP/FP/FN veya başarı oranı üretmeyeceğiz.

Önce orijinal görüntüyü ve hedef baş ROI'sini gösterin. Ardından RGB ve HSV maske bindirmelerini, tüm görüntüdeki renkli alan yüzdesini ve baş ROI örtüşmesini ayrı ayrı okuyun. Kural sırayla baş ROI'nin varlığını, yüzde 2,5 alan sınırını ve yüzde 5 örtüşme sınırını kullanır. Son olarak renk maskesinden çıkan aday kutuları gösterin; bunların hazır bir dedektör çıktısı olmadığını vurgulayın. Öğretim elemanı mevcut K3'ü seçerse RGB'nin benzer renkli makinede yanlış alarm verdiğini gösteren mevcut sonuca bağlayın; yeni bir görüntü seçerse o anki çıktıyı önceden bilinmeyen bir sonuç olarak yorumlayın. Demo için gerekirse defterler/00_canli_demo.ipynb kullanılabilir, fakat sunum slaytlarla yürür.

Kaynak: sonuclar/temel_sonuclar.csv; sonuclar/sonuc_tablosu.md; betikler/canli_demo.py; kaynak/analiz.py; ayarlar/deney_ayarlari.json.
""")

# 6 — Sonuç ve sınırlar
s = base("Sınır: renk, nesne kimliği değildir", 6, "Grup", 1)
picture(s, "sonuclar/kutular/K2_rgb.png", 0.60, 1.25, 6.45, 5.35)
txt(s, "K2'de ROI yüksek, toplam alan çok küçük", 7.30, 1.55, 5.26, 1.02, 24, NAVY, True)
txt(s, "Alan %0,02–0,04  <  %2,5 eşik", 7.30, 2.92, 5.23, 0.60, 23, ORANGE, True)
rect(s, 7.30, 3.91, 5.10, 0.028, RGBColor(213, 225, 230))
txt(s, "Sonraki kontrol", 7.30, 4.17, 5.15, 0.45, 20, TEAL, True)
txt(s, "Baş çevresinde alan hesabı\nŞekil ölçütleri\nDaha büyük bağımsız veri seti",
    7.30, 4.75, 5.12, 1.45, 19, NAVY)
notes(s, """
SONUÇ VE SINIRLILIKLAR (yaklaşık 1 dakika)
Bu çalışma sarı piksellerin varlığını ölçüyor; sarı bir bölgenin gerçekten baret nesnesi olduğunu kanıtlamıyor. K3'teki iş makinesi yanlış kutular üretti. K2'de ise baş ROI örtüşmesi yüksek olmasına rağmen tüm görüntüye göre maske alanı yüzde 0,02 ile 0,04 arasında; ortak yüzde 2,5 sınırı önce uygulandığı için karar “baret yok”. Gaussian Blur ve ölçek değişse bile sınıfın aynı kalması sağlamlık kanıtı değildir. Bir sonraki deneyde alanı baş ROI çevresinde ölçmeyi ve aday kutuların şeklini değerlendirmeyi öneriyoruz. Yeni kural geliştirme görüntülerinde tanımlanıp daha büyük bağımsız veri setinde sınanmalı. Altı görüntüyle saha güvenilirliği iddia etmiyoruz.

Kaynak: sonuclar/bulaniklik/bulaniklik_sonuclari.csv; sonuclar/temel_sonuclar.csv; ayarlar/deney_ayarlari.json; etiketler/gercek_etiketler.json.
""")

assert len(prs.slides) == 6
prs.save(OUT)
print(OUT.relative_to(KOK))
