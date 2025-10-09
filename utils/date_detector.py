"""
Utilidad para detectar y extraer fechas de textos
"""
import re
from datetime import datetime
from config.constants import MESES


class DateDetector:
    """
    Detecta fechas en diferentes formatos dentro de un texto.
    
    Formatos soportados:
    - DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    - YYYY/MM/DD, YYYY-MM-DD
    - "15 de marzo", "mar, 7 de oct"
    """
    
    def __init__(self):
        self.meses = MESES
        self.patron_numerico = r'\b((\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})|(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}))\b'
        # Patrón más flexible que acepta saltos de línea y caracteres especiales
        self.patron_texto = r'(?:[a-z]{3},?\s+)?(\d{1,2})\s+de\s+([a-z]{3,9})'
    
    def extract_date(self, texto):
        """
        Detecta y extrae una fecha del texto en formato DD/MM/YYYY.
        
        Args:
            texto (str): Texto donde buscar la fecha
            
        Returns:
            str: Fecha en formato DD/MM/YYYY o "No detectada"
        """
        # Buscar formato numérico
        fecha_match = re.search(self.patron_numerico, texto, re.IGNORECASE)
        
        if fecha_match:
            return fecha_match.group(1)
        
        # Buscar formato texto (con re.DOTALL para que \s incluya saltos de línea)
        fecha_match_texto = re.search(self.patron_texto, texto, re.IGNORECASE | re.MULTILINE)
        
        if fecha_match_texto:
            dia = fecha_match_texto.group(1).zfill(2)
            mes_texto = fecha_match_texto.group(2).lower()
            mes = self.meses.get(mes_texto, '01')
            anio = datetime.now().year
            
            return f"{dia}/{mes}/{anio}"
        
        return "No detectado"