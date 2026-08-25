"""
audit_contrast — resolucao de cor efetiva e calculo de contraste WCAG.

O erro classico de auditor caseiro e ler <a:srgbClr> e parar ai. Cor em OOXML
quase sempre vem por referencia ao tema (<a:schemeClr val="tx1">) com
modificadores encadeados (lumMod, lumOff, tint, shade). Ignorar os
modificadores produz contraste fantasiado.

Cadeia implementada:
  schemeClr -> mapa de cores (p:clrMap do master, p:clrMapOvr do layout/slide)
            -> a:clrScheme do tema -> modificadores na ordem em que aparecem.
"""
from __future__ import annotations

import colorsys

from a11y_lib import NS, q, local, get_txBody, iter_paragraphs

try:
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
except ImportError:  # pragma: no cover
    RT = None


# --------------------------------------------------------------------------
# Matematica de cor
# --------------------------------------------------------------------------
def _srgb_lin(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb) -> float:
    r, g, b = rgb
    return 0.2126 * _srgb_lin(r) + 0.7152 * _srgb_lin(g) + 0.0722 * _srgb_lin(b)


def contrast_ratio(rgb1, rgb2) -> float:
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def hex_to_rgb(h: str):
    h = h.strip().lstrip("#")
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_to_hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def _clamp01(v):
    return max(0.0, min(1.0, v))


def apply_lum_mod_off(rgb, lum_mod=None, lum_off=None):
    r, g, b = (c / 255.0 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if lum_mod is not None:
        l *= lum_mod
    if lum_off is not None:
        l += lum_off
    l = _clamp01(l)
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (r * 255, g * 255, b * 255)


def apply_shade(rgb, val):
    """Shade opera em espaco linear, conforme ECMA-376."""
    out = []
    for c in rgb:
        lin = _srgb_lin(c) * val
        out.append(_lin_to_srgb(lin))
    return tuple(out)


def apply_tint(rgb, val):
    out = []
    for c in rgb:
        lin = _srgb_lin(c) * val + (1.0 - val)
        out.append(_lin_to_srgb(lin))
    return tuple(out)


def _lin_to_srgb(lin: float) -> float:
    lin = _clamp01(lin)
    s = lin * 12.92 if lin <= 0.0031308 else 1.055 * (lin ** (1 / 2.4)) - 0.055
    return _clamp01(s) * 255


PRESET_COLORS = {
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "gray": (128, 128, 128), "grey": (128, 128, 128), "darkGray": (169, 169, 169),
    "lightGray": (211, 211, 211),
}


# --------------------------------------------------------------------------
# Tema
# --------------------------------------------------------------------------
class ThemeResolver:
    """Resolve cor de tema para RGB, no contexto de um slide."""

    def __init__(self, prs):
        self.prs = prs
        self._scheme_cache = {}

    # -- tema do master --------------------------------------------------
    def _theme_scheme(self, master):
        key = id(master)
        if key in self._scheme_cache:
            return self._scheme_cache[key]
        scheme = {}
        try:
            theme_part = master.part.part_related_by(RT.THEME)
            root = theme_part._element if hasattr(theme_part, "_element") else None
            if root is None:
                from lxml import etree
                root = etree.fromstring(theme_part.blob)
            clrScheme = root.find(".//" + q("a:clrScheme"))
            if clrScheme is not None:
                for child in clrScheme:
                    name = local(child)
                    rgb = self._literal_color(child)
                    if rgb:
                        scheme[name] = rgb
        except Exception:
            pass
        self._scheme_cache[key] = scheme
        return scheme

    @staticmethod
    def _literal_color(parent):
        """<a:dk1><a:sysClr .../></a:dk1> ou <a:srgbClr val=.../>"""
        for child in parent:
            n = local(child)
            if n == "srgbClr":
                return hex_to_rgb(child.get("val"))
            if n == "sysClr":
                last = child.get("lastClr")
                if last:
                    return hex_to_rgb(last)
                return (0, 0, 0) if child.get("val") == "windowText" else (255, 255, 255)
        return None

    # -- mapa de cores ---------------------------------------------------
    @staticmethod
    def _color_map(slide):
        """tx1->dk1, bg1->lt1 etc., considerando p:clrMapOvr."""
        default = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2"}
        mapping = dict(default)
        try:
            master = slide.slide_layout.slide_master
            cm = master._element.find(q("p:clrMap"))
            if cm is not None:
                for k, v in cm.attrib.items():
                    mapping[k] = v
        except Exception:
            pass
        for part in (getattr(slide, "slide_layout", None), slide):
            if part is None:
                continue
            ovr = part._element.find(q("p:clrMapOvr"))
            if ovr is not None:
                om = ovr.find(q("a:overrideClrMapping"))
                if om is not None:
                    for k, v in om.attrib.items():
                        mapping[k] = v
        return mapping

    # -- API principal ---------------------------------------------------
    def resolve(self, color_el, slide):
        """
        Recebe um elemento de cor (a:srgbClr, a:schemeClr, a:sysClr, a:prstClr)
        e devolve (rgb, descricao) ou (None, motivo).
        """
        if color_el is None:
            return None, "sem elemento de cor"
        n = local(color_el)
        base = None
        desc = n

        if n == "srgbClr":
            base = hex_to_rgb(color_el.get("val"))
            desc = "#" + (color_el.get("val") or "")
        elif n == "sysClr":
            last = color_el.get("lastClr")
            base = hex_to_rgb(last) if last else (
                (0, 0, 0) if color_el.get("val") == "windowText" else (255, 255, 255))
            desc = "sysClr:%s" % color_el.get("val")
        elif n == "prstClr":
            base = PRESET_COLORS.get(color_el.get("val"))
            desc = "prstClr:%s" % color_el.get("val")
        elif n == "schemeClr":
            val = color_el.get("val")
            mapping = self._color_map(slide)
            target = mapping.get(val, val)
            # phClr nao e resolvivel fora do contexto de um estilo de forma
            if val == "phClr":
                return None, "phClr (herdado de estilo)"
            master = slide.slide_layout.slide_master
            scheme = self._theme_scheme(master)
            base = scheme.get(target) or scheme.get(val)
            desc = "schemeClr:%s->%s" % (val, target)

        if base is None:
            return None, "nao resolvida (%s)" % desc

        # modificadores, na ordem em que aparecem
        rgb = tuple(float(c) for c in base)
        lum_mod = lum_off = None
        for mod in color_el:
            m = local(mod)
            v = mod.get("val")
            if v is None:
                continue
            fv = int(v) / 100000.0
            if m == "lumMod":
                lum_mod = fv
            elif m == "lumOff":
                lum_off = fv
            elif m == "shade":
                rgb = apply_shade(rgb, fv)
                desc += "+shade%d" % int(fv * 100)
            elif m == "tint":
                rgb = apply_tint(rgb, fv)
                desc += "+tint%d" % int(fv * 100)
        if lum_mod is not None or lum_off is not None:
            rgb = apply_lum_mod_off(rgb, lum_mod, lum_off)
            desc += "+lum"
        return tuple(int(round(c)) for c in rgb), desc


# --------------------------------------------------------------------------
# Preenchimento de formas e fundo do slide
# --------------------------------------------------------------------------
FILL_TAGS = ("a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:noFill", "a:grpFill")


def _first_fill(parent):
    if parent is None:
        return None
    for child in parent:
        t = "a:" + local(child)
        if t in FILL_TAGS:
            return child
    return None


def shape_fill(shape_el, slide, resolver):
    """(rgb, descricao) do preenchimento proprio da forma, ou (None, motivo)."""
    spPr = None
    for child in shape_el:
        if local(child) in ("spPr", "grpSpPr"):
            spPr = child
            break
    fill = _first_fill(spPr)
    if fill is None:
        return None, "sem preenchimento explicito"
    t = local(fill)
    if t == "noFill":
        return None, "noFill"
    if t == "solidFill":
        for child in fill:
            rgb, d = resolver.resolve(child, slide)
            if rgb:
                return rgb, d
        return None, "solidFill nao resolvido"
    return None, t  # gradFill / blipFill / pattFill -> indeterminado


def slide_background(slide, resolver):
    """
    Fundo efetivo: p:bg do slide, senao do layout, senao do master.
    Devolve (rgb, descricao) ou (None, motivo) — motivo 'gradFill'/'blipFill'
    significa que o contraste tem de ser avaliado por humano (regra E09).
    """
    chain = [("slide", slide)]
    layout = getattr(slide, "slide_layout", None)
    if layout is not None:
        chain.append(("layout", layout))
        master = getattr(layout, "slide_master", None)
        if master is not None:
            chain.append(("master", master))

    for nome, part in chain:
        cSld = part._element.find(q("p:cSld"))
        if cSld is None:
            continue
        bg = cSld.find(q("p:bg"))
        if bg is None:
            continue
        bgPr = bg.find(q("p:bgPr"))
        if bgPr is not None:
            fill = _first_fill(bgPr)
            if fill is None:
                continue
            t = local(fill)
            if t == "solidFill":
                for child in fill:
                    rgb, d = resolver.resolve(child, slide)
                    if rgb:
                        return rgb, "%s:%s" % (nome, d)
                continue
            return None, "%s:%s" % (nome, t)
        bgRef = bg.find(q("p:bgRef"))
        if bgRef is not None:
            for child in bgRef:
                rgb, d = resolver.resolve(child, slide)
                if rgb:
                    return rgb, "%s:bgRef(%s)" % (nome, d)

    # sem p:bg em lugar nenhum: o padrao do tema e lt1
    try:
        master = slide.slide_layout.slide_master
        scheme = resolver._theme_scheme(master)
        if "lt1" in scheme:
            return scheme["lt1"], "tema:lt1 (padrao)"
    except Exception:
        pass
    return None, "fundo indeterminado"


def run_color(r_el, slide, resolver):
    """Cor declarada no run. (None, motivo) se herdada."""
    rPr = r_el.find(q("a:rPr"))
    if rPr is None:
        return None, "sem rPr"
    fill = _first_fill(rPr)
    if fill is None or local(fill) != "solidFill":
        return None, "cor herdada"
    for child in fill:
        rgb, d = resolver.resolve(child, slide)
        if rgb:
            return rgb, d
    return None, "cor nao resolvida"


def default_text_color(slide, resolver):
    """Fallback quando a cor do texto e herdada: tx1 do tema."""
    try:
        master = slide.slide_layout.slide_master
        scheme = resolver._theme_scheme(master)
        mapping = resolver._color_map(slide)
        return scheme.get(mapping.get("tx1", "dk1")), "tema:tx1 (herdado)"
    except Exception:
        return None, "indeterminado"


# --------------------------------------------------------------------------
# Limiares WCAG
# --------------------------------------------------------------------------
def is_large_text(sz_centipt, bold: bool) -> bool:
    """18pt normal, ou 14pt negrito."""
    if sz_centipt is None:
        return False
    return sz_centipt >= 1800 or (bold and sz_centipt >= 1400)


def required_ratio(sz_centipt, bold: bool, level: str = "AA") -> float:
    large = is_large_text(sz_centipt, bold)
    if level == "AAA":
        return 4.5 if large else 7.0
    return 3.0 if large else 4.5
