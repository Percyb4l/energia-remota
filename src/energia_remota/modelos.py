from dataclasses import dataclass


FUENTES_VALIDAS = ("solar", "eolica", "hidraulica", "biomasa")


class ErrorMercado(Exception):
    """Datos o reglas del mercado que no se pueden aceptar."""


@dataclass
class Oferta:
    id: str
    generador: str
    planta: str
    fuente: str
    kwh_disponibles: float
    precio_kwh: float


@dataclass
class Contrato:
    id: str
    oferta_id: str
    generador: str
    planta: str
    consumidor: str
    kwh: float
    precio_kwh: float

    @property
    def valor(self):
        return round(self.kwh * self.precio_kwh, 2)


def texto_obligatorio(valor, campo):
    if valor is None or not str(valor).strip():
        raise ErrorMercado(f"{campo} es obligatorio")
    return str(valor).strip()


def numero_positivo(valor, campo):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ErrorMercado(f"{campo} debe ser un numero") from None
    if numero <= 0:
        raise ErrorMercado(f"{campo} debe ser mayor que cero")
    return numero


def fuente_valida(valor):
    fuente = texto_obligatorio(valor, "La fuente").lower()
    if fuente not in FUENTES_VALIDAS:
        permitidas = ", ".join(FUENTES_VALIDAS)
        raise ErrorMercado(f"Fuente no reconocida. Use: {permitidas}")
    return fuente
