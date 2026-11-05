import pytest

from energia_remota import ErrorMercado, Mercado
from energia_remota.cli import demo, procesar


def test_jhonnier_publica_la_oferta_que_luego_se_contrata():
    mercado = Mercado()

    oferta = mercado.publicar(
        "Aguas del Cauca",
        "Central Rio Cauca",
        "HIDRAULICA",
        "1000",
        "210",
    )

    assert oferta.id == "OF-1"
    assert oferta.fuente == "hidraulica"
    assert oferta.kwh_disponibles == 1000


def test_jhonnier_rechaza_una_oferta_que_no_se_puede_contratar():
    mercado = Mercado()

    with pytest.raises(ErrorMercado):
        mercado.publicar(" ", "Central", "hidraulica", 100, 210)
    with pytest.raises(ErrorMercado):
        mercado.publicar("Aguas del Cauca", "", "hidraulica", 100, 210)
    with pytest.raises(ErrorMercado):
        mercado.publicar("Aguas del Cauca", "Central", "carbon", 100, 210)
    with pytest.raises(ErrorMercado):
        mercado.publicar("Aguas del Cauca", "Central", "hidraulica", 0, 210)
    with pytest.raises(ErrorMercado):
        mercado.publicar("Aguas del Cauca", "Central", "hidraulica", 100, -1)
    with pytest.raises(ErrorMercado):
        mercado.publicar("Aguas del Cauca", "Central", "hidraulica", "mucho", 210)


def test_jhonnier_elige_la_oferta_mas_barata_del_catalogo():
    mercado = Mercado()
    mercado.publicar("Sol del Valle", "Granja Jamundi", "solar", 500, 280)
    mercado.publicar("Vientos del Norte", "Parque Guajira", "eolica", 800, 250)
    mercado.publicar("Aguas del Cauca", "Central Rio Cauca", "hidraulica", 1000, 210)

    catalogo = mercado.catalogo()
    elegida = catalogo[0]
    contrato = mercado.contratar("Colegio San Pedro", elegida.id, 120)

    assert [oferta.id for oferta in catalogo] == ["OF-3", "OF-2", "OF-1"]
    assert contrato.planta == "Central Rio Cauca"
    assert contrato.valor == 25200
    assert mercado.ofertas[2].kwh_disponibles == 880
    assert [oferta.id for oferta in mercado.catalogo(precio_maximo=250)] == ["OF-3", "OF-2"]
    assert [oferta.planta for oferta in mercado.catalogo(fuente="solar")] == ["Granja Jamundi"]


def test_jhonnier_no_compra_mas_energia_de_la_disponible():
    mercado = Mercado()
    mercado.publicar("Sol del Valle", "Granja Jamundi", "solar", 50, 280)

    with pytest.raises(ErrorMercado):
        mercado.contratar("Colegio San Pedro", "OF-1", 51)
    with pytest.raises(ErrorMercado):
        mercado.contratar("Colegio San Pedro", "OF-9", 10)
    with pytest.raises(ErrorMercado):
        mercado.contratar("  ", "OF-1", 10)
    with pytest.raises(ErrorMercado):
        mercado.contratar("Colegio San Pedro", "OF-1", 0)
    with pytest.raises(ErrorMercado):
        mercado.catalogo(fuente="carbon")
    with pytest.raises(ErrorMercado):
        mercado.catalogo(precio_maximo=0)

    assert mercado.ofertas[0].kwh_disponibles == 50
    assert mercado.contratos == []


def test_jhonnier_los_paneles_reflejan_su_contrato():
    mercado = Mercado()
    mercado.publicar("Aguas del Cauca", "Central Rio Cauca", "hidraulica", 1000, 210)
    mercado.publicar("Aguas del Cauca", "Pequena Central Pance", "hidraulica", 200, 230)
    mercado.contratar("Colegio San Pedro", "OF-1", 120)
    mercado.contratar("Colegio San Pedro", "OF-2", 30)

    generador = mercado.panel_generador(" Aguas del Cauca ")
    consumidor = mercado.panel_consumidor("Colegio San Pedro")
    admin = mercado.panel_administrador()

    assert generador["kwh_vendidos"] == 150
    assert generador["kwh_disponibles"] == 1050
    assert generador["contratos"] == 2
    assert consumidor["cantidad_plantas"] == 2
    assert consumidor["kwh"] == 150
    assert consumidor["valor"] == 32100
    assert admin["oferta_kwh"] == 1200
    assert admin["demanda_kwh"] == 150
    assert Mercado().panel_consumidor("Barrio Nuevo")["plantas"] == []
    assert mercado.panel_generador("Generador Nuevo")["ofertas"] == 0


def test_jhonnier_contrata_desde_la_linea_de_comandos():
    mercado = Mercado()
    publicado = procesar(
        mercado,
        "publicar;Aguas del Cauca;Central Rio Cauca;hidraulica;1000;210",
    )
    catalogo = procesar(mercado, "catalogo;hidraulica;250")
    contrato = procesar(mercado, "contratar;Colegio San Pedro;OF-1;120")

    assert "OF-1" in publicado
    assert "Central Rio Cauca" in catalogo
    assert "CT-1" in contrato
    assert "25200" in contrato
    generador = procesar(mercado, "generador;Aguas del Cauca")
    assert "120" in generador
    assert "880" in generador
    assert "1 plantas" in procesar(mercado, "consumidor;Colegio San Pedro")
    assert "Oferta 1000" in procesar(mercado, "admin")
    assert "Comandos" in procesar(mercado, "ayuda")
    assert procesar(Mercado(), "catalogo") == "No hay ofertas con esos filtros."
    assert "0 plantas" in procesar(Mercado(), "consumidor;Barrio Nuevo")


def test_jhonnier_rechaza_comandos_mal_escritos():
    mercado = Mercado()

    with pytest.raises(ErrorMercado):
        procesar(mercado, "")
    with pytest.raises(ErrorMercado):
        procesar(mercado, "borrar")
    with pytest.raises(ErrorMercado):
        procesar(mercado, "publicar;solo-dos-datos")
    with pytest.raises(ErrorMercado):
        procesar(mercado, "contratar;incompleto")
    with pytest.raises(ErrorMercado):
        procesar(mercado, "generador")
    with pytest.raises(ErrorMercado):
        procesar(mercado, "consumidor")
    with pytest.raises(ErrorMercado):
        procesar(mercado, "catalogo;solar;280;extra")


def test_jhonnier_la_demo_muestra_el_contrato_y_los_paneles():
    texto = demo()

    assert "CT-1" in texto
    assert "Central Rio Cauca" in texto
    assert "2 plantas" in texto
    assert "Oferta 2300" in texto
