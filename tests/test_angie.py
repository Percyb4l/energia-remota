
import pytest

from energia_remota import ErrorMercado, Mercado
from energia_remota.cli import AYUDA, demo, main, procesar


def test_angie_compra_multiples_ofertas_y_actualiza_paneles():
    mercado = Mercado()

    o1 = mercado.publicar(
        "Empresa Eolica Norte", "Parque Eolico 1", "eolica", 500, 180
    )
    o2 = mercado.publicar(
        "Solar del Sur", "Planta Solar 1", "solar", 300, 200
    )

    assert o1.id == "OF-1"
    assert o2.id == "OF-2"

    contrato1 = mercado.contratar("Industrias del Valle", "OF-1", 200)
    contrato2 = mercado.contratar("Industrias del Valle", "OF-1", 300)
    contrato3 = mercado.contratar("Industrias del Valle", "OF-2", 100)

    assert contrato1.id == "CT-1"
    assert contrato1.valor == 36000
    assert contrato2.id == "CT-2"
    assert contrato3.id == "CT-3"

    catalogo = mercado.catalogo()
    assert len(catalogo) == 1
    assert catalogo[0].id == "OF-2"
    assert catalogo[0].kwh_disponibles == 200

    consumidor = mercado.panel_consumidor("Industrias del Valle")
    assert consumidor["kwh"] == 600
    assert consumidor["valor"] == 110000
    assert consumidor["cantidad_plantas"] == 2
    assert "Parque Eolico 1" in consumidor["plantas"]
    assert "Planta Solar 1" in consumidor["plantas"]

    admin = mercado.panel_administrador()
    assert admin["ofertas_abiertas"] == 1
    assert admin["demanda_kwh"] == 600
    assert admin["oferta_kwh"] == 800


def test_angie_valida_filtros_catalogo_y_excepciones():
    mercado = Mercado()
    mercado.publicar("EcoEnergia", "Termica Solar", "solar", 1000, 150)
    mercado.publicar("HidroCauca", "Represa Mayo", "hidraulica", 500, 120)

    baratas = mercado.catalogo(precio_maximo=130)
    assert len(baratas) == 1
    assert baratas[0].planta == "Represa Mayo"

    respuesta = procesar(
        mercado, "contratar;Clinica Central;OF-2;100"
    )
    assert "CT-1" in respuesta

    with pytest.raises(ErrorMercado):
        procesar(mercado, "catalogo;nuclear;500")

    with pytest.raises(ErrorMercado):
        procesar(mercado, "contratar;Clinica Central;OF-2;99999")


def test_angie_rechaza_publicaciones_invalidas():
    mercado = Mercado()

    with pytest.raises(ErrorMercado):
        mercado.publicar("Generadora X", "Planta Y", "solar", -50, 100)

    with pytest.raises(ErrorMercado):
        mercado.publicar("Generadora X", "Planta Y", "solar", 100, 0)


def test_angie_valida_comandos_cli_y_paneles():
    mercado = Mercado()
    mercado.publicar("Energia Angie", "Planta Solar", "solar", 500, 180)
    mercado.contratar("Universidad del Valle", "OF-1", 100)

    assert procesar(mercado, "ayuda") == AYUDA
    assert "Planta Solar" in procesar(mercado, "catalogo")
    assert "Energia Angie" in procesar(mercado, "generador;Energia Angie")
    assert "100.0 kWh" in procesar(mercado, "consumidor;Universidad del Valle")
    assert "demanda 100.0 kWh" in procesar(mercado, "admin")

    with pytest.raises(ErrorMercado):
        procesar(mercado, "comando_invalido")

    with pytest.raises(ErrorMercado):
        procesar(mercado, "publicar;Energia Angie")

    with pytest.raises(ErrorMercado):
        procesar(mercado, "catalogo;solar;100;extra")


def test_angie_ejecuta_demo_y_main(capsys):
    resultado = demo()

    assert "Sol del Valle" in resultado
    assert "Colegio San Pedro" in resultado
    assert "Contrato CT-" in resultado

    main()
    salida = capsys.readouterr().out

    assert "Energia remota" in salida
    assert "Comandos, separados por punto y coma" in salida
