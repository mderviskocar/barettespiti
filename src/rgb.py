import cv2
import numpy as np


def create_mask(image_bgr, config):
    """Sabit RGB aralığıyla 0/255 maske döndürür. Girdi BGR'dir; dönüşüm burada yapılır. Sahip: Omar."""
    if config.get("lower") is None or config.get("upper") is None:
        raise ValueError("RGB ayarında lower/upper aralığı yok; önce G1/G2 üzerinde seçin.")
    # OpenCV görüntüyü BGR okur; aralık RGB'de tanımlı olduğu için açıkça dönüştürülür.
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    lower = np.array(config["lower"], dtype=np.uint8)
    upper = np.array(config["upper"], dtype=np.uint8)
    # Üç kanal da aralığın içindeyse piksel 255, değilse 0 olur.
    return cv2.inRange(image_rgb, lower, upper)
