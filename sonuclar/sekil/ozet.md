# Şekil ölçütü (ek, keşif amaçlı) — K1–K4 toplamı

Eşikler: en-boy 0.6–2.0, doluluk ≥ 0.4, dışbükeylik ≥ 0.6 (ayarlar/sekil_olcutu.json).

| Uzay | TP önce → sonra | FP önce → sonra | FN önce → sonra | Doğru sınıf önce → sonra | Doğru sınıf (ek kural) |
| --- | --- | --- | --- | --- | --- |
| HSV | 3 → 1 | 36 → 19 | 1 → 3 | 2/4 → 2/4 | 4/4 |
| RGB | 1 → 1 | 45 → 18 | 3 → 3 | 1/4 → 2/4 | 4/4 |

Ek kural: Baş bölgesi yoksa: belirsiz → Baş bölgesindeki renkli piksel oranı (ham renk maskesi) >= %5: basta_baret → Şekil ölçütünü geçen renkli alan < %2,5: baret_yok → Aksi halde: baret_var_basta_degil

Ana yöntemin parçası değildir. Hata analizinde (K3 yanlış alarmı) önerilen sonraki kontrol olarak, K1-K4 sonuçları bilindikten sonra eklendi; bu yüzden yalnızca keşif amaçlı raporlanır. Ana sonuç tablosu (sonuclar/) değişmez. Model eğitimi yoktur; yalnızca geometrik ölçüler kullanılır.

K1-K4 sonuçları görüldükten sonra tasarlandı; ana sonuç değildir. Gerçek sınaması yeni, daha önce görülmemiş görüntülerle yapılmalıdır.
