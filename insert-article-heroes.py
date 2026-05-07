#!/usr/bin/env python3
"""Insert hero images into all 6 blog articles.

Replaces any existing article banner between </header> and <!-- ARTICLE BODY -->
with a full-width image banner using the mapped image per article.
"""
import re
from pathlib import Path

BLOG = Path(__file__).parent / "blog"

# (article_slug, image_filename, alt_text)
ARTICLES = [
    ("como-obtener-cdl-florida",
     "blog-thumb-cdl-florida.jpg",
     "Licencia CDL Clase A de Florida sobre escritorio con mapa y llaves de camión"),
    ("cambios-industria-2025",
     "blog-thumb-industry-2025.jpg",
     "Terminal de carga de Florida al atardecer con camiones Clase A en muelles de carga"),
    ("cdl-nacional",
     "blog-thumb-national-cdl.jpg",
     "Camión Clase A rojo cruzando autopista interestatal con paisajes variados al atardecer"),
    ("regulaciones-cdl-florida",
     "blog-thumb-fl-regulations.jpg",
     "Mapa de Florida con formulario médico DOT y documentos regulatorios CDL"),
    ("dominio-ingles-cdl",
     "blog-thumb-elp.jpg",
     "Chofer hispano en inspección del Florida Highway Patrol con portapapeles"),
    ("salario-camionero-tampa",
     "blog-thumb-tampa-salary.jpg",
     "Camionero hispano exitoso en Tampa con camión Clase A rojo y billetera"),
]

BANNER_TMPL = """<!-- ARTICLE BANNER -->
<div class="article-banner" style="position:relative;overflow:hidden;max-width:1200px;margin:0 auto 0;aspect-ratio:21/9;max-height:420px;border-bottom:1px solid rgba(255,255,255,0.06)">
  <img src="../../images/{img}" alt="{alt}" loading="lazy" fetchpriority="high" style="width:100%;height:100%;object-fit:cover;display:block"/>
  <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,10,10,0.15) 0%,rgba(10,10,10,0.55) 100%);pointer-events:none"></div>
</div>
"""


def process(path: Path, img: str, alt: str):
    html = path.read_text()
    new_banner = BANNER_TMPL.format(img=img, alt=alt)

    # Replace everything between </header> and <!-- ARTICLE BODY --> with new banner.
    pattern = re.compile(
        r"(</header>\s*\n)(.*?)(<!-- ARTICLE BODY -->)",
        re.DOTALL,
    )
    replacement = r"\1" + new_banner + r"\n\3"
    new_html, n = pattern.subn(replacement, html, count=1)
    if n == 0:
        return f"SKIP (no match): {path}"
    path.write_text(new_html)
    return f"OK: {path} ({img})"


def main():
    for slug, img, alt in ARTICLES:
        p = BLOG / slug / "index.html"
        if not p.exists():
            print(f"MISSING: {p}")
            continue
        print(process(p, img, alt))


if __name__ == "__main__":
    main()
