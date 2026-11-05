# Energia remota

Programa pequeno para publicar ofertas de plantas, elegir una y consultar los paneles del generador, del consumidor y del administrador.

## Ejecutar

```bash
python -m energia_remota
```

El comando se corre desde esta carpeta. Para usarlo a mano:

```text
publicar;Sol del Valle;Granja Jamundi;solar;500;280
catalogo
contratar;Colegio San Pedro;OF-1;40
generador;Sol del Valle
consumidor;Colegio San Pedro
admin
```

## Pruebas

```bash
pip install -r requirements.txt
pytest
```

La cobertura minima es 60 %. La prueba de Jhonnier esta en `tests/test_jhonnier.py`. Cada integrante agrega la suya en `tests/`.

## Pipeline

En cada push, GitHub Actions ejecuta las pruebas y envia el resultado a SonarCloud. SonarCloud mide cobertura, complejidad ciclomatica, duplicacion, deuda tecnica y code smells.

Antes del primer push:

1. Crear el repositorio de GitHub con el contenido de esta carpeta.
2. Entrar a https://sonarcloud.io, importar ese repositorio y copiar el token.
3. En GitHub, guardar el token como secreto `SONAR_TOKEN`.
4. En `sonar-project.properties`, cambiar `sonar.organization` y `sonar.projectKey` por los valores que muestre SonarCloud.
