"""defterler/ altındaki bütün defterleri baştan çalıştırıp çıktılarıyla kaydeder.

Kullanım:  python betikler/defterleri_calistir.py   (önce: python betikler/deneyleri_calistir.py)
00_canli_demo, yeni görüntü için pencere açabileceğinden varsayılan hedefle (K4) çalışır.
"""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

KOK = Path(__file__).resolve().parents[1]
for yol in sorted((KOK / "defterler").glob("*.ipynb")):
    defter = nbformat.read(yol, as_version=4)
    NotebookClient(defter, timeout=900, kernel_name="python3",
                   resources={"metadata": {"path": str(yol.parent)}}).execute()
    nbformat.write(defter, yol)
    print("çalıştırıldı:", yol.name)
