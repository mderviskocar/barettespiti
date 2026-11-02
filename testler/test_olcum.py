"""kaynak/olcum.py testleri. Çalıştırma: python testler/test_olcum.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402

from kaynak.olcum import alan_ve_ortusme, iou, kutulari_degerlendir, piksel_karsilastir  # noqa: E402
from kaynak.siniflandirma import sinifla  # noqa: E402

K2 = [981, 94, 1070, 165]
K3 = [[1094, 859, 1135, 908], [1633, 963, 1658, 1005]]
KURAL = {"en_az_renk_alani_yuzde": 2.5, "en_az_bas_ortusmesi_yuzde": 5.0}


def test_iou():
    assert iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1.0
    assert iou([0, 0, 10, 10], [20, 20, 30, 30]) == 0.0
    assert abs(iou([0, 0, 10, 10], [5, 0, 15, 10]) - 1 / 3) < 1e-9


def test_tam_eslesme_tp():
    d = kutulari_degerlendir([K2], [K2])
    assert (d["tp"], d["fp"], d["fn"]) == (1, 0, 0)


def test_ayni_barete_iki_kutu_tek_tp():
    d = kutulari_degerlendir([{"kutu": K2, "guven": 0.9}, {"kutu": [982, 95, 1071, 166], "guven": 0.6}], [K2])
    assert (d["tp"], d["fp"], d["fn"]) == (1, 1, 0)


def test_dusuk_iou_fp_ve_fn():
    d = kutulari_degerlendir([[1030, 94, 1119, 165]], [K2])
    assert (d["tp"], d["fp"], d["fn"]) == (0, 1, 1)


def test_kucuk_baret_kacirma():
    d = kutulari_degerlendir([K3[0]], K3)
    assert (d["tp"], d["fp"], d["fn"]) == (1, 0, 1) and d["kacirilan_gercekler"] == [1]


def test_gercek_yoksa_her_kutu_fp():
    assert kutulari_degerlendir([[10, 10, 50, 50]], [])["fp"] == 1


def test_alan_ve_ortusme():
    m = np.zeros((10, 10), np.uint8); m[0:2, 0:5] = 255
    alan, ortusme = alan_ve_ortusme(m, [0, 0, 5, 2])
    assert alan == 10.0 and ortusme == 100.0
    assert alan_ve_ortusme(m, None)[1] is None


def test_piksel_karsilastir():
    renk = np.zeros((4, 4), np.uint8); renk[:, :2] = 255
    baret = np.zeros((4, 4), np.uint8); baret[:2, :] = 255
    p = piksel_karsilastir(renk, baret)
    assert p["kesinlik_yuzde"] == 50.0 and p["duyarlilik_yuzde"] == 50.0


def test_karar_kurali():
    assert sinifla(3.0, 10.0, None, KURAL) == "belirsiz"
    assert sinifla(1.0, 50.0, [0, 0, 1, 1], KURAL) == "baret_yok"
    assert sinifla(3.0, 6.0, [0, 0, 1, 1], KURAL) == "basta_baret"
    assert sinifla(3.0, 1.0, [0, 0, 1, 1], KURAL) == "baret_var_basta_degil"


if __name__ == "__main__":
    for ad, f in list(globals().items()):
        if ad.startswith("test_"):
            f(); print("TAMAM", ad)
