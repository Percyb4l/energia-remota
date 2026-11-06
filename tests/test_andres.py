from energia_remota import Mercado


def test_andres_catalogo_filtra_por_fuente_y_precio_maximo():
    mercado = Mercado()
    mercado.publicar("Sol del Valle", "Granja Jamundi", "solar", 300, 250)
    mercado.publicar("Vientos del Norte", "Parque Guajira", "eolica", 400, 200)
    mercado.publicar("Sol del Valle", "Techo Cali", "solar", 100, 180)

    solares = mercado.catalogo(fuente="solar")
    assert [oferta.id for oferta in solares] == ["OF-3", "OF-1"]

    baratas = mercado.catalogo(precio_maximo=200)
    assert [oferta.id for oferta in baratas] == ["OF-3", "OF-2"]


def test_andres_panel_generador_suma_ofertas_y_ventas():
    mercado = Mercado()
    mercado.publicar("Sol del Valle", "Granja Jamundi", "solar", 300, 250)
    mercado.publicar("Vientos del Norte", "Parque Guajira", "eolica", 400, 260)
    mercado.publicar("Sol del Valle", "Techo Cali", "solar", 100, 180)
    mercado.contratar("Colegio San Pedro", "OF-1", 120)

    panel = mercado.panel_generador("Sol del Valle")

    assert panel["ofertas"] == 2
    assert panel["kwh_disponibles"] == 280
    assert panel["kwh_vendidos"] == 120
    assert panel["contratos"] == 1


def test_andres_panel_generador_sin_ofertas_queda_en_cero():
    mercado = Mercado()
    mercado.publicar("Sol del Valle", "Granja Jamundi", "solar", 300, 250)

    panel = mercado.panel_generador("Central Desconocida")

    assert panel["generador"] == "Central Desconocida"
    assert panel["ofertas"] == 0
    assert panel["kwh_disponibles"] == 0
    assert panel["kwh_vendidos"] == 0
    assert panel["contratos"] == 0
