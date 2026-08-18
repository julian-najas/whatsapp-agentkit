"""El prefijo estático viaja con `cache_control`, o no se está cobrando el caché.

`cache-estatico` (chequeo 15) garantiza que el prefijo **se puede** cachear: nada de reloj, ni
`uuid`, ni valores de la petición interpolados. Esa es la mitad difícil y estaba resuelta desde
la primera ronda.

La otra mitad no la miraba nadie: que la llamada **mande** ese prefijo con `cache_control`. Sin
la clave, el prefijo se vuelve a cobrar entero en cada mensaje que entra, y no hay forma de
notarlo desde afuera —la respuesta es correcta, no hay error, sólo sube la factura—. Un cerrador
lee el mismo catálogo y el mismo playbook en cada turno de cada conversación, así que es
justamente el caso donde más duele.

Esto se afirma leyendo el árbol y no llamando a la API a propósito: la suite corre sin red y sin
credenciales, igual que la compuerta.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
AGENTE = RAIZ / "agente"

pytestmark = pytest.mark.skipif(
    not AGENTE.is_dir(), reason="no existe agente/: esto corre después de /armar-cerrador"
)


def _llamadas_al_modelo():
    """Cada `…messages.create(…)` del build, con el árbol de su función."""
    for modulo in sorted(AGENTE.glob("*.py")):
        arbol = ast.parse(modulo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if not (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)):
                continue
            if nodo.func.attr != "create":
                continue
            if not isinstance(nodo.func.value, ast.Attribute):
                continue
            if nodo.func.value.attr != "messages":
                continue
            yield modulo, arbol, nodo


def _dicts_con(arbol, clave: str) -> list[ast.Dict]:
    encontrados = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Dict):
            continue
        for k in nodo.keys:
            if isinstance(k, ast.Constant) and k.value == clave:
                encontrados.append(nodo)
    return encontrados


def test_hay_exactamente_una_llamada_al_modelo():
    """Si aparece una segunda, esta prueba deja de cubrir el build entero y hay que mirarla."""
    llamadas = list(_llamadas_al_modelo())
    assert len(llamadas) == 1, (
        f"esperaba una sola llamada `messages.create` en agente/ y encontré {len(llamadas)}: "
        f"{[m.name for m, _, _ in llamadas]}"
    )


def test_el_prefijo_del_sistema_viaja_con_cache_control():
    modulo, arbol, _ = next(iter(_llamadas_al_modelo()))
    con_cache = _dicts_con(arbol, "cache_control")
    assert con_cache, (
        f"{modulo.name} llama al modelo sin `cache_control` en el cuerpo del sistema. El prefijo "
        f"es estático y sin esa clave se vuelve a cobrar entero en cada mensaje. "
        f"Ver blueprint/30-generacion.md § Paso 5"
    )


def test_el_cache_control_es_ephemeral_y_no_otra_cosa():
    """`{'type': 'ephemeral'}` es la única forma que acepta la API; un typo se traga sin error."""
    _, arbol, _ = next(iter(_llamadas_al_modelo()))
    valores = []
    for d in _dicts_con(arbol, "cache_control"):
        for k, v in zip(d.keys, d.values):
            if isinstance(k, ast.Constant) and k.value == "cache_control":
                valores.append(v)
    assert valores, "no hay ningún valor asociado a `cache_control`"
    for v in valores:
        assert isinstance(v, ast.Dict), "`cache_control` tiene que ser un dict `{'type': ...}`"
        tipos = [
            c.value
            for k, c in zip(v.keys, v.values)
            if isinstance(k, ast.Constant) and k.value == "type" and isinstance(c, ast.Constant)
        ]
        assert tipos == ["ephemeral"], f"`cache_control.type` tiene que ser 'ephemeral', es {tipos}"


def test_el_cache_control_va_en_el_bloque_del_sistema_y_no_en_el_del_usuario():
    """Ponerlo en `messages` en vez de en `system` cachea lo que cambia y no lo que se repite."""
    _, arbol, _ = next(iter(_llamadas_al_modelo()))
    for d in _dicts_con(arbol, "cache_control"):
        claves = {k.value for k in d.keys if isinstance(k, ast.Constant)}
        assert "text" in claves and "type" in claves, (
            "el `cache_control` tiene que ir en el mismo bloque que lleva el texto del sistema, "
            f"y este dict sólo trae {sorted(claves)}"
        )
