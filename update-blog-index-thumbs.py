#!/usr/bin/env python3
"""Replace gradient+SVG placeholder thumbs on /blog/ with real hero images."""
import re
from pathlib import Path

INDEX = Path(__file__).parent / "blog" / "index.html"

# (href pattern for the card link, image filename, alt text)
CARD_IMAGES = [
    ("/blog/como-obtener-cdl-florida/",
     "blog-thumb-cdl-florida.jpg",
     "Licencia CDL Clase A de Florida sobre escritorio con mapa y llaves"),
    ("/blog/cambios-industria-2025/",
     "blog-thumb-industry-2025.jpg",
     "Terminal de carga al atardecer con camiones Clase A en muelles"),
    ("/blog/cdl-nacional/",
     "blog-thumb-national-cdl.jpg",
     "Camión Clase A rojo cruzando autopista interestatal con paisajes variados"),
    ("/blog/regulaciones-cdl-florida/",
     "blog-thumb-fl-regulations.jpg",
     "Mapa de Florida con formulario médico DOT y documentos regulatorios CDL"),
    ("/blog/dominio-ingles-cdl/",
     "blog-thumb-elp.jpg",
     "Chofer hispano en inspección del Florida Highway Patrol"),
    ("/blog/salario-camionero-tampa/",
     "blog-thumb-tampa-salary.jpg",
     "Camionero hispano exitoso con camión Clase A rojo en Tampa"),
]

# Each card-thumb is a div with gradient background containing an SVG.
# Pattern: <div class="card-thumb" style="background:...">...</div>
CARD_PATTERN = re.compile(
    r'<div class="card-thumb"[^>]*>\s*<svg[^<]*(?:<[^>]+>[^<]*)*</svg>\s*</div>',
    re.DOTALL,
)


def process():
    html = INDEX.read_text()
    cards_updated = 0

    for href, img, alt in CARD_IMAGES:
        # Find the <article> that contains this href, then replace its card-thumb.
        # Locate the href anchor position, walk backwards to find the enclosing <article>,
        # then locate the card-thumb INSIDE that article.
        article_open_pattern = re.compile(r'<article class="article-card[^"]*">')
        hrefs_pattern = re.compile(re.escape(f'href="{href}"'))
        h_match = hrefs_pattern.search(html)
        if not h_match:
            print(f"SKIP (no card for): {href}")
            continue
        # Find the nearest <article class="article-card"> before this position
        article_starts = [m.start() for m in article_open_pattern.finditer(html[:h_match.start()])]
        if not article_starts:
            print(f"SKIP (no enclosing article): {href}")
            continue
        article_start = article_starts[-1]
        # Find closing </article>
        article_end = html.find("</article>", article_start)
        article_block = html[article_start:article_end]
        # Replace the first card-thumb inside this block
        new_thumb = (
            f'<div class="card-thumb">\n'
            f'        <img src="../images/{img}" alt="{alt}" loading="lazy" '
            f'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block"/>\n'
            f'        <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(160deg,rgba(10,10,10,0.10) 0%,rgba(10,10,10,0.45) 100%);pointer-events:none"></div>\n'
            f'      </div>'
        )
        new_block, n = CARD_PATTERN.subn(new_thumb, article_block, count=1)
        if n == 0:
            print(f"SKIP (no thumb found inside): {href}")
            continue
        html = html[:article_start] + new_block + html[article_end:]
        cards_updated += 1
        print(f"OK: {href} <- {img}")

    # Also update the .card-thumb CSS in blog.css to handle images (need position:relative)
    INDEX.write_text(html)
    return cards_updated


def main():
    n = process()
    print(f"\nTotal cards updated: {n}")


if __name__ == "__main__":
    main()
