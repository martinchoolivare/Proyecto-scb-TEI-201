# Diseño 3D: gemelo completo y caja de control

![Gemelo 3D completo del Proyecto SCB](renders/gemelo_completo.png)

## Dónde está cada cosa

| Archivo o carpeta | Qué es |
|---|---|
| **`SCB_gemelo_completo.step`** | **Gemelo 3D de todo el sistema**: brazo v3 con sus 3 MG996R, pinza con SG90 y FSR, estación de sensado (celda de carga, HX711, inductivo, capacitivo y HC-SR04), fuente de 5 V, caja de control con el Arduino y la electrónica adentro, contenedores, tablero y patas. Cada pieza trae su nombre y color |
| `modelo_3d/` | Modelo del robot: piezas impresas del brazo, la pinza, la estación y la base (STL y STEP), ensambles, planos de armado y scripts. Ver [`modelo_3d/README.md`](modelo_3d/README.md) |
| `SCB_caja_control_gemelo.step` | Gemelo de la caja sola: base, tapa y los volúmenes del Arduino UNO, la placa perforada con borneras y condensador, el HX711 y el MT3608 |
| `SCB_componentes_externos.step` | Biblioteca de componentes sueltos (MG996R, SG90, HC-SR04, inductivo M12, capacitivo M18, celda de 1 kg, FSR-402 y fuente S-50-5). Ya van montados en el gemelo completo |
| `planos/planos_caja_control.pdf` | 3 hojas A3 a escala 1:1 de la caja: base, tapa y ensamble (vistas ortogonales, cotas, tolerancias, lista de piezas y cómo reparar) |
| `renders/` | `gemelo_completo*.png` (sistema completo, caja abierta y vista trasera) y `caja_*.png` (exterior, interior y explosionada), en PNG con fondo transparente; `SCB_gemelo_completo_giro.mp4`, video de 12 s del gemelo girando |
| `stl/` | `caja_base.stl` y `caja_tapa.stl`, listos para imprimir (caben en una cama de 160 mm) |
| `fuente/` | Scripts de CadQuery: `caja_control.py`, `planos.py` y `render_caja.py` para la caja; `gemelo_completo.py`, `render_gemelo.py` y `video_giro.py` para el gemelo completo |

## Gemelo completo

`fuente/gemelo_completo.py` toma el prototipo completo de `modelo_3d/ensamble/Prototipo_SCB_completo.step` y le agrega la caja de control. La caja reemplaza al soporte abierto del Arduino (pieza 18), a la protoboard y al HX711 suelto, porque esos tres elementos van dentro de ella.

- **Posición:** la caja va en la esquina delantera derecha del tablero, girada para que el USB y el conector DC del Arduino queden hacia el borde delantero, donde se conecta el notebook. La ranura de cables mira hacia el brazo y la estación.
- **Sin interferencias:** el script calcula la intersección de la caja con todas las piezas del prototipo y no encuentra ninguna; la caja solo apoya sobre el tablero. Holguras: 12 mm a la base del brazo, 4 mm al pasacables del tablero y 8 mm al borde delantero.
- **Alcance del brazo:** la caja mide 45,4 mm de alto y la torreta empieza a 46 mm del tablero, así que el brazo puede girar sin tocarla.

| Caja abierta | Vista trasera |
|:---:|:---:|
| ![Caja abierta](renders/gemelo_completo_caja_abierta.png) | ![Vista trasera](renders/gemelo_completo_atras.png) |

Para regenerarlo: `cd fuente`, luego `python gemelo_completo.py` y después `python render_gemelo.py`.

## La caja en números

- Exterior de 154,8 × 104,8 × 45,4 mm con la tapa; interior útil de 150 × 100 × 40 mm. Paredes de 2,4 mm.
- **Sin interferencias**: se verificó por cálculo de intersección entre todos los cuerpos. El componente más alto, el condensador, llega a 26,6 mm y el techo útil está a 37,5 mm.
- **Diseño para la reparación**: la tapa se cierra con 4 tornillos M3 avellanados sobre insertos de bronce, el Arduino y la placa van atornillados con tuercas cautivas, y el HX711 y el MT3608 entran deslizando en rieles, sin tornillos. Los cables salen por una ranura en U que se abre al levantar la tapa.
- Holgura de 0,3 mm por lado en todos los ajustes entre piezas impresas.

## Sacar el `.f3d` en Fusion 360 (lo pide la guía)

1. **Archivo → Abrir → Abrir desde mi equipo → `SCB_gemelo_completo.step`**. Fusion lo convierte y quedan todas las piezas con su nombre y color en el navegador, ya en su lugar.
2. **Guardar**. Queda el `.f3d` en su proyecto de Fusion.
3. **Archivo → Exportar → Tipo: Archivos de Fusion 360 (`.f3d`)**, y súbanlo a esta carpeta como `SCB_gemelo_completo.f3d`.
4. Para la demo: oculten la tapa de la caja (componente `Caja_control → Tapa`) con el ojito del navegador para mostrar la electrónica, o usen **Inspeccionar → Análisis de sección**.

**Sobre la parametrización.** El modelo paramétrico vive en `fuente/caja_control.py`: todas las medidas salen de la sección `PARÁMETROS`, por ejemplo `L_INT`, `PARED`, `HOLGURA` o la posición de cada componente. Cambian un valor, corren `python caja_control.py` y se regeneran el STEP, los STL, los planos (`planos.py`) y los renders (`render_caja.py`). Al importarse en Fusion, el STEP queda como geometría fija: si el evaluador pide ver parámetros en Fusion, muestren este script y expliquen que es el árbol paramétrico del diseño.

## Imprimir

| Pieza | Orientación | Soportes | Relleno | Masa aprox. |
|---|---|---|---|---|
| `caja_base.stl` | Boca hacia arriba | No | 20 % | 100 g |
| `caja_tapa.stl` | Ya viene boca abajo | No | 20 % | 50 g |

Después de imprimir: coloquen los 4 insertos M3 con el cautín a unos 220 °C, presionen las 8 tuercas M3 en los hexágonos de abajo y prueben que el USB del Arduino calce en su calado antes de cablear.
