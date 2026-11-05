from energia_remota.modelos import (
    Contrato,
    ErrorMercado,
    Oferta,
    fuente_valida,
    numero_positivo,
    texto_obligatorio,
)


class Mercado:
    """Ofertas de plantas y contratos directos entre generador y consumidor."""

    def __init__(self):
        self.ofertas = []
        self.contratos = []
        self._seq_oferta = 0
        self._seq_contrato = 0

    def publicar(self, generador, planta, fuente, kwh_disponibles, precio_kwh):
        generador = texto_obligatorio(generador, "El generador")
        planta = texto_obligatorio(planta, "La planta")
        fuente = fuente_valida(fuente)
        kwh = numero_positivo(kwh_disponibles, "La energia disponible")
        precio = numero_positivo(precio_kwh, "El precio")

        self._seq_oferta += 1
        oferta = Oferta(
            id=f"OF-{self._seq_oferta}",
            generador=generador,
            planta=planta,
            fuente=fuente,
            kwh_disponibles=kwh,
            precio_kwh=precio,
        )
        self.ofertas.append(oferta)
        return oferta

    def catalogo(self, fuente=None, precio_maximo=None):
        resultado = [oferta for oferta in self.ofertas if oferta.kwh_disponibles > 0]
        if fuente:
            fuente = fuente_valida(fuente)
            resultado = [oferta for oferta in resultado if oferta.fuente == fuente]
        if precio_maximo is not None:
            tope = numero_positivo(precio_maximo, "El precio maximo")
            resultado = [oferta for oferta in resultado if oferta.precio_kwh <= tope]
        return sorted(resultado, key=lambda oferta: (oferta.precio_kwh, oferta.planta))

    def contratar(self, consumidor, oferta_id, kwh):
        consumidor = texto_obligatorio(consumidor, "El consumidor")
        oferta_id = texto_obligatorio(oferta_id, "La oferta")
        cantidad = numero_positivo(kwh, "La cantidad")

        oferta = self._buscar_oferta(oferta_id)
        if cantidad > oferta.kwh_disponibles:
            raise ErrorMercado("No hay suficiente energia disponible en esa planta")

        oferta.kwh_disponibles = round(oferta.kwh_disponibles - cantidad, 4)
        self._seq_contrato += 1
        contrato = Contrato(
            id=f"CT-{self._seq_contrato}",
            oferta_id=oferta.id,
            generador=oferta.generador,
            planta=oferta.planta,
            consumidor=consumidor,
            kwh=cantidad,
            precio_kwh=oferta.precio_kwh,
        )
        self.contratos.append(contrato)
        return contrato

    def panel_generador(self, generador):
        generador = texto_obligatorio(generador, "El generador")
        propias = [oferta for oferta in self.ofertas if oferta.generador == generador]
        vendidos = [
            contrato
            for contrato in self.contratos
            if contrato.generador == generador
        ]
        return {
            "generador": generador,
            "ofertas": len(propias),
            "kwh_disponibles": round(sum(oferta.kwh_disponibles for oferta in propias), 4),
            "kwh_vendidos": round(sum(contrato.kwh for contrato in vendidos), 4),
            "contratos": len(vendidos),
        }

    def panel_consumidor(self, consumidor):
        consumidor = texto_obligatorio(consumidor, "El consumidor")
        mios = [
            contrato
            for contrato in self.contratos
            if contrato.consumidor == consumidor
        ]
        plantas = sorted({contrato.planta for contrato in mios})
        return {
            "consumidor": consumidor,
            "plantas": plantas,
            "cantidad_plantas": len(plantas),
            "kwh": round(sum(contrato.kwh for contrato in mios), 4),
            "valor": round(sum(contrato.valor for contrato in mios), 2),
            "contratos": len(mios),
        }

    def panel_administrador(self):
        vendido = sum(contrato.kwh for contrato in self.contratos)
        disponible = sum(oferta.kwh_disponibles for oferta in self.ofertas)
        return {
            "oferta_kwh": round(disponible + vendido, 4),
            "demanda_kwh": round(vendido, 4),
            "ofertas_abiertas": sum(
                1 for oferta in self.ofertas if oferta.kwh_disponibles > 0
            ),
            "contratos": len(self.contratos),
        }

    def _buscar_oferta(self, oferta_id):
        for oferta in self.ofertas:
            if oferta.id == oferta_id:
                return oferta
        raise ErrorMercado("La oferta no existe")
