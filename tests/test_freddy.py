from energia_remota import Mercado

def test_freddy_panel_consumidor_consolida_multiples_contratos():
    mercado = Mercado()
    mercado.publicar("Sol del Valle", "Granja Jamundi", "solar", 500, 250)
    mercado.publicar("Vientos del Norte", "Parque Guajira", "eolica", 400, 200)

    # El consumidor contrata energia de dos fuentes distintas
    mercado.contratar("Empresa Indutal", "OF-1", 100)
    mercado.contratar("Empresa Indutal", "OF-2", 150)

    panel = mercado.panel_consumidor("Empresa Indutal")

    # Validaciones del resumen del consumidor
    assert panel["consumidor"] == "Empresa Indutal"
    assert panel["contratos"] == 2
    assert panel["kwh"] == 250
    assert panel["valor"] == 55000  # (100 * 250) + (150 * 200)
    assert set(panel["plantas"]) == {"Granja Jamundi", "Parque Guajira"}