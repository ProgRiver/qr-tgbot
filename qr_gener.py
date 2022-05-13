import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask


def get_green_qrcode(url, user_id):
    """
    Функция генератор QR кода по переданной ссылке.
    """
    try:
        qr = qrcode.QRCode(box_size=9)
        qr.add_data(url)
        img = qr.make_image(image_factory=StyledPilImage, 
                            color_mask=RadialGradiantColorMask(back_color=(255, 255, 255), center_color=(0, 0, 0), edge_color=(0, 128, 0)))
        name = f"{user_id}.png"
        img.save(stream=name)
        print(f"QRcode выполнен, файл {name}")
        return name
    except Exception as er:
        print(f"[!] Ошибка модуля get_green_qrcode\n{er}")
