"""El kit no puede afirmar en presente algo que venció mientras nadie miraba.

`blueprint/05-arranque.md` decía «hoy ese mensaje no se cobra» sobre el precio de WhatsApp, y
`blueprint/50-despliegue.md` lo mismo. El 1 de octubre de 2026 Meta pasa a cobrar por mensaje
de negocio, así que esa frase **se vuelve falsa sola**: sin que nadie toque un archivo, sin
que falle ninguna prueba, sin que la compuerta se entere. Y el kit se la sigue contando al
comprador con la misma seguridad con la que contaba lo demás.

Es la peor clase de mentira que puede tener un producto que se vende hecho: no hay error, hay
confianza. Un archivo fechado que se cree actual es peor que uno sin fecha, porque el segundo
al menos te hace dudar.

El arreglo son dos cosas y las dos hacen falta. La prosa pasa a describir **dos regímenes con
fecha** —hasta el 30 de septiembre, desde el 1 de octubre— y así es cierta a los dos lados del
corte. Y el chequeo 25 se pone rojo si alguien la reescribe en futuro, para que no vuelva a
pasar.

La prueba que cierra el asunto es la última: agarra los blueprints de verdad, se para en el 2
de octubre de 2026 y comprueba que el kit sigue diciendo la verdad ese día.
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
AUDITAR = RAIZ / "scripts" / "auditar.py"

pytestmark = pytest.mark.skipif(not AUDITAR.is_file(), reason="no está scripts/auditar.py")

CORTE = date(2026, 10, 1)
LITERAL = "1 de octubre de 2026"


def _modulo():
    """`auditar.py` cargado aparte, para poder mentirle el calendario sin tocar el de nadie.

    El alta en `sys.modules` antes de ejecutarlo no es adorno: `@dataclass` resuelve las
    anotaciones mirando el módulo por nombre, y sin el alta revienta con un `AttributeError`
    de `dataclasses` que no dice nada de esto.
    """
    spec = importlib.util.spec_from_file_location("auditar_bajo_prueba", AUDITAR)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class _Calendario:
    """Un almanaque mentido. Sin esto no hay forma de pararse del otro lado del corte."""

    def __init__(self, hoy: date) -> None:
        self.hoy = hoy

    def today(self) -> date:
        return self.hoy

    @staticmethod
    def fromisoformat(crudo: str) -> date:
        return date.fromisoformat(crudo)


def _correr(hoy: date, archivos: dict[str, str], tmp_path: Path):
    """Corre el chequeo 25 sobre un árbol de mentira, con la fecha que le digamos."""
    for rel, texto in archivos.items():
        destino = tmp_path / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")

    mod = _modulo()
    mod.date = _Calendario(hoy)
    mod.AFIRMACIONES_CON_FECHA = tuple(
        ("2026-10-01", LITERAL, rel, "el precio de WhatsApp") for rel in archivos
    ) or (("2026-10-01", LITERAL, "blueprint/no-existe.md", "el precio de WhatsApp"),)

    reporte = mod.Reporte("fechas-que-caducan", "prueba")
    mod.chequeo_fechas_que_caducan(mod.Contexto(tmp_path), reporte)
    return reporte.cerrar()


def _ids(chequeo) -> set[str]:
    return {h.id for h in chequeo.hallazgos}


DOS_REGIMENES = f"""# Costos

- **WhatsApp.** Son dos regímenes y el corte es el **{LITERAL}**. *Hasta el 30 de septiembre
  de 2026:* si el cliente escribió primero, ese mensaje no se cobra. *Desde el {LITERAL}:*
  Meta cobra por mensaje de negocio.
"""

EN_FUTURO = f"""# Costos

- **WhatsApp.** Hoy ese mensaje no se cobra. **El {LITERAL} esto cambia:** Meta pasa a cobrar
  por mensaje de negocio.
"""


def test_verde_cuando_la_fecha_esta_lejos(tmp_path: Path) -> None:
    ch = _correr(CORTE - timedelta(days=200), {"blueprint/05-arranque.md": EN_FUTURO}, tmp_path)
    assert ch.estado == "pass"
    assert _ids(ch) == set()


def test_avisa_cuando_el_corte_se_acerca(tmp_path: Path) -> None:
    """Cuarenta y cinco días de aviso, para que no llegue el día y nadie se acuerde."""
    ch = _correr(CORTE - timedelta(days=10), {"blueprint/05-arranque.md": DOS_REGIMENES},
                 tmp_path)
    assert ch.estado == "pass", "acercarse no es fallar"
    assert "fechas/se_acerca" in _ids(ch)


def test_rojo_si_la_fecha_paso_y_el_texto_sigue_hablando_en_futuro(tmp_path: Path) -> None:
    """El agujero entero, en una prueba."""
    ch = _correr(CORTE + timedelta(days=1), {"blueprint/05-arranque.md": EN_FUTURO}, tmp_path)
    assert ch.estado == "fail"
    assert "fechas/futuro_vencido" in _ids(ch)


def test_verde_despues_del_corte_si_la_prosa_describe_los_dos_regimenes(tmp_path: Path) -> None:
    """Lo que hace que el kit sobreviva al 1 de octubre sin que nadie lo edite ese día."""
    ch = _correr(CORTE + timedelta(days=90), {"blueprint/05-arranque.md": DOS_REGIMENES},
                 tmp_path)
    assert ch.estado == "pass"
    assert _ids(ch) == set()


def test_rojo_si_alguien_borra_la_advertencia(tmp_path: Path) -> None:
    """Borrar el aviso deja al comprador leyendo un precio viejo como si fuera el de hoy."""
    ch = _correr(CORTE - timedelta(days=200),
                 {"blueprint/05-arranque.md": "# Costos\n\nWhatsApp sale barato.\n"}, tmp_path)
    assert ch.estado == "fail"
    assert "fechas/aviso_borrado" in _ids(ch)


def test_rojo_si_falta_el_archivo(tmp_path: Path) -> None:
    ch = _correr(CORTE - timedelta(days=200), {}, tmp_path)
    assert ch.estado == "fail"
    assert "fechas/archivo_ausente" in _ids(ch)


@pytest.mark.parametrize("rel", ["blueprint/05-arranque.md", "blueprint/50-despliegue.md"])
def test_los_blueprints_de_verdad_siguen_diciendo_la_verdad_el_2_de_octubre(rel: str) -> None:
    """La prueba que cierra el encargo: el kit tiene que perdurar más allá del 1 de octubre.

    No es una maqueta. Son los archivos que se le entregan al comprador, leídos parados en el
    día después del corte.
    """
    archivo = RAIZ / rel
    assert archivo.is_file(), f"falta {rel}"
    texto = archivo.read_text(encoding="utf-8")

    assert LITERAL in texto, f"{rel} ya no nombra el corte"

    mod = _modulo()
    parrafos = mod._parrafos_con(texto, LITERAL)
    culpables = sorted({f for p in parrafos for f in mod.HABLA_EN_FUTURO if f in p})
    assert not culpables, (
        f"{rel} habla en futuro del {LITERAL} ({', '.join(culpables)}): el 2 de octubre de "
        f"2026 ese párrafo afirma algo falso"
    )
