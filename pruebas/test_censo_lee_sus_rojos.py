"""El censo tiene que saber leer los rojos que él mismo provoca.

`--censo` cambia un campo de la salida, corre la suite entera y mira si algún nodo se pone
rojo. Todo eso funcionaba. Lo que no funcionaba era el último paso: reconocer la línea
`FAILED …` en la salida de pytest.

El 18-ago-2026 los cuarenta y tres campos daban `indeterminado` con la evidencia diciendo
`mutados: 48` y un `FAILED` adentro del detalle. O sea: mutaba, la suite se ponía roja como
tenía que ponerse, y el veredicto era «no pude medir». El patrón buscaba líneas que
empezaran por `FAILED`, y la línea llegaba como `\\x1b[31mFAILED\\x1b[0m …` porque pytest
colorea cuando el entorno trae `FORCE_COLOR` o `PY_COLORS`, aunque la salida vaya a una
tubería.

**Ese entorno es el de un agente**, no el de una terminal cualquiera. Y este kit está hecho
para que lo construya un agente, así que el censo se rompía justo donde más se usa. En una
terminal normal funcionaba, y por eso nadie lo vio.

Un censo que no lee sus propios rojos no falla: **afirma que no midió nada**, y el chequeo
que lo consume lo daba por bueno porque lee la evidencia guardada.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

AUDITAR = Path(__file__).resolve().parent.parent / "scripts" / "auditar.py"

pytestmark = pytest.mark.skipif(not AUDITAR.is_file(), reason="no está scripts/auditar.py")


def _patron_del_censo() -> re.Pattern:
    """`FALLA_DE_PYTEST` leído del archivo, sin importar `auditar.py` entero."""
    arbol = ast.parse(AUDITAR.read_text(encoding="utf-8"))
    espacio: dict = {"re": re}
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign):
            nombres = {getattr(t, "id", "") for t in nodo.targets}
            if nombres & {"ANSI", "FALLA_DE_PYTEST"}:
                exec(compile(ast.Module([nodo], []), "<auditar>", "exec"), espacio)  # noqa: S102
    patron = espacio.get("FALLA_DE_PYTEST")
    assert patron is not None, "no encontré `FALLA_DE_PYTEST` en scripts/auditar.py"
    return patron


ROJO = "\x1b[31m"
FIN = "\x1b[0m"
NODO = "pruebas/test_caso_01.py::test_6_no_escala_y_la_salida_valida_con_estado_parcial"


@pytest.mark.parametrize(
    "linea,esperado",
    [
        pytest.param(f"FAILED {NODO}", NODO, id="sin color"),
        pytest.param(f"{ROJO}FAILED{FIN} {NODO}", NODO, id="con color, que es el caso que falló"),
        pytest.param(f"ERROR {NODO}", NODO, id="ERROR sin color"),
        pytest.param(f"{ROJO}ERROR{FIN} {NODO}", NODO, id="ERROR con color"),
        pytest.param(f"\x1b[1m\x1b[31mFAILED{FIN} {NODO}", NODO, id="dos escapes seguidos"),
    ],
)
def test_el_censo_reconoce_un_rojo_venga_o_no_coloreado(linea: str, esperado: str):
    m = _patron_del_censo().match(linea.strip())
    assert m is not None, (
        f"el censo no reconoce este rojo: {linea!r}. Sin reconocerlo, el campo sale "
        f"`indeterminado` y el censo afirma que no midió nada, con la suite roja delante"
    )
    assert m.group(1) == esperado


@pytest.mark.parametrize(
    "linea",
    ["257 passed in 16.03s", "-- Docs: https://docs.pytest.org/", "", "  FAILED_pero_no  x"],
)
def test_no_confunde_con_un_rojo_lo_que_no_lo_es(linea: str):
    assert _patron_del_censo().match(linea.strip()) is None, (
        f"{linea!r} no es un nodo rojo y el censo lo está leyendo como si lo fuera"
    )


def test_el_censo_le_pide_a_pytest_que_no_coloree():
    """El cinturón, además del tirante: si pytest no colorea, el patrón ni se pone a prueba."""
    fuente = AUDITAR.read_text(encoding="utf-8")
    corridas = fuente.count('"--color=no"')
    assert corridas >= 2, (
        f"esperaba `--color=no` en las dos corridas del censo (la base y cada mutante) y lo "
        f"encontré {corridas} vez/veces. Sin eso, el patrón queda como única defensa"
    )
