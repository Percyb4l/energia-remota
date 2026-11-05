from energia_remota.mercado import Mercado
from energia_remota.modelos import ErrorMercado


AYUDA = """Comandos, separados por punto y coma:
  publicar;Generador;Planta;fuente;kwh;precio
  catalogo
  catalogo;fuente
  catalogo;fuente;precio_maximo
  contratar;Consumidor;OF-1;kwh
  generador;Nombre
  consumidor;Nombre
  admin
  ayuda
Fuentes: solar, eolica, hidraulica, biomasa.
"""


def procesar(mercado, linea):
    texto = (linea or "").strip()
    if not texto:
        raise ErrorMercado("Escribe un comando. Usa ayuda para ver la lista.")

    partes = [parte.strip() for parte in texto.split(";")]
    comando = partes[0].lower()

    if comando == "ayuda":
        return AYUDA
    if comando == "publicar":
        return _publicar(mercado, partes)
    if comando == "catalogo":
        return _catalogo(mercado, partes)
    if comando == "contratar":
        return _contratar(mercado, partes)
    if comando == "generador":
        return _generador(mercado, partes)
    if comando == "consumidor":
        return _consumidor(mercado, partes)
    if comando == "admin":
        return _admin(mercado)
    raise ErrorMercado(f"Comando no reconocido: {comando}")


def _exigir(partes, cantidad, uso):
    if len(partes) != cantidad:
        raise ErrorMercado(uso)
    return partes


def _publicar(mercado, partes):
    _, generador, planta, fuente, kwh, precio = _exigir(
        partes,
        6,
        "Uso: publicar;Generador;Planta;fuente;kwh;precio",
    )
    oferta = mercado.publicar(generador, planta, fuente, kwh, precio)
    return (
        f"Oferta {oferta.id}: {oferta.planta} ({oferta.fuente}), "
        f"{oferta.kwh_disponibles} kWh a {oferta.precio_kwh} por kWh"
    )


def _catalogo(mercado, partes):
    if len(partes) == 1:
        ofertas = mercado.catalogo()
    elif len(partes) == 2:
        ofertas = mercado.catalogo(fuente=partes[1])
    elif len(partes) == 3:
        ofertas = mercado.catalogo(fuente=partes[1], precio_maximo=partes[2])
    else:
        raise ErrorMercado("Uso: catalogo o catalogo;fuente;precio_maximo")

    if not ofertas:
        return "No hay ofertas con esos filtros."

    lineas = ["Catalogo de energia disponible:"]
    for oferta in ofertas:
        lineas.append(
            f"{oferta.id} | {oferta.planta} | {oferta.generador} | "
            f"{oferta.fuente} | {oferta.kwh_disponibles} kWh | "
            f"{oferta.precio_kwh} por kWh"
        )
    return "\n".join(lineas)


def _contratar(mercado, partes):
    _, consumidor, oferta_id, kwh = _exigir(
        partes,
        4,
        "Uso: contratar;Consumidor;OF-1;kwh",
    )
    contrato = mercado.contratar(consumidor, oferta_id, kwh)
    return (
        f"Contrato {contrato.id}: {contrato.consumidor} compra "
        f"{contrato.kwh} kWh a {contrato.planta} por {contrato.valor}"
    )


def _generador(mercado, partes):
    _, nombre = _exigir(partes, 2, "Uso: generador;Nombre")
    panel = mercado.panel_generador(nombre)
    return (
        f"{panel['generador']}: {panel['ofertas']} ofertas, "
        f"{panel['kwh_vendidos']} kWh vendidos, "
        f"{panel['kwh_disponibles']} kWh aun disponibles, "
        f"{panel['contratos']} contratos"
    )


def _consumidor(mercado, partes):
    _, nombre = _exigir(partes, 2, "Uso: consumidor;Nombre")
    panel = mercado.panel_consumidor(nombre)
    plantas = ", ".join(panel["plantas"]) if panel["plantas"] else "ninguna"
    return (
        f"{panel['consumidor']}: compra a {panel['cantidad_plantas']} plantas "
        f"({plantas}), {panel['kwh']} kWh, valor {panel['valor']}"
    )


def _admin(mercado):
    panel = mercado.panel_administrador()
    return (
        f"Oferta {panel['oferta_kwh']} kWh, demanda {panel['demanda_kwh']} kWh, "
        f"{panel['ofertas_abiertas']} ofertas abiertas, "
        f"{panel['contratos']} contratos"
    )


def demo():
    """Recorrido de la propuesta: publicar, elegir y mirar los tres paneles."""
    mercado = Mercado()
    ordenes = [
        "publicar;Sol del Valle;Granja Jamundi;solar;500;280",
        "publicar;Vientos del Norte;Parque Guajira;eolica;800;250",
        "publicar;Aguas del Cauca;Central Rio Cauca;hidraulica;1000;210",
        "catalogo",
        "contratar;Colegio San Pedro;OF-3;120",
        "contratar;Colegio San Pedro;OF-1;40",
        "generador;Aguas del Cauca",
        "consumidor;Colegio San Pedro",
        "admin",
    ]
    bloques = []
    for orden in ordenes:
        bloques.append(f"> {orden}\n{procesar(mercado, orden)}")
    return "\n\n".join(bloques)


def main():
    print("Energia remota: ofertas y contratos directos")
    print(demo())
    print()
    print(AYUDA)
