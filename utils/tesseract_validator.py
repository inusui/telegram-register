import pytesseract

class TesseractValidator:
    """Clase para validar la instalación de Tesseract OCR"""

    @staticmethod
    def verificar_tesseract():
        # Verificar Tesseract
        try:
            pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR detectado: {pytesseract.get_tesseract_version()}")
        except Exception as e:
            print(f"⚠️ ADVERTENCIA: Tesseract no detectado. Error: {e}")
            print("   Asegúrate de que Tesseract esté instalado y en el PATH")
            print("   O configura TESSERACT_PATH en el archivo .env")
            return