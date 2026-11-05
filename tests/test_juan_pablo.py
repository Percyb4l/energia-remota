from energia_remota import Mercado


def test_juan_pablo_agota_una_oferta_y_sale_del_catalogo():
    mercado = Mercado()
    mercado.publicar("Sol del Valle", "Granja Jamundi", "solar", 300, 250)
    mercado.publicar("Vientos del Norte", "Parque Guajira", "eolica", 400, 260)

    contrato = mercado.contratar("Hospital Universitario", "OF-1", 300)

    assert contrato.id == "CT-1"
    assert contrato.valor == 75000
    assert mercado.ofertas[0].kwh_disponibles == 0
    assert [oferta.id for oferta in mercado.catalogo()] == ["OF-2"]

    consumidor = mercado.panel_consumidor("Hospital Universitario")
    assert consumidor["plantas"] == ["Granja Jamundi"]
    assert consumidor["kwh"] == 300
    assert consumidor["contratos"] == 1

    admin = mercado.panel_administrador()
    assert admin["ofertas_abiertas"] == 1
    assert admin["oferta_kwh"] == 700
    assert admin["demanda_kwh"] == 300
