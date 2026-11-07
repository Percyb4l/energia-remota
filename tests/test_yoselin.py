from energia_remota import Mercado

def test_yoselin_contratar_oferta():
    mercado = Mercado()
    # Primero publicamos una oferta para poder contratarla
    mercado.publicar(
        "Sol del Valle",
        "Granja Jamundi",
        "solar",
        300,
        250,
    )
    # Probamos la función contratar con el orden correcto de argumentos
    contrato = mercado.contratar("Cliente Jamundi", "OF-1", 100)
    assert contrato.oferta_id == "OF-1"
    assert contrato.consumidor == "Cliente Jamundi"
    assert len(mercado.contratos) == 1