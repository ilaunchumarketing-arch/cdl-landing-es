#!/usr/bin/env python3
"""Insert mid-article section images before specific H2/H3 anchors.

Each tuple: (article_slug, image_filename, alt_text, heading_marker, caption)
heading_marker is the exact text inside the H2 or H3 tag to match.
"""
from pathlib import Path

BLOG = Path(__file__).parent / "blog"

INSERTIONS = [
    ("como-obtener-cdl-florida",
     "blog-mid-yard-maneuvers.jpg",
     "Estudiante CDL practicando maniobra de patio con conos entre camión Clase A e instructor",
     "<h2>Paso 3: El Examen de Habilidades (Skills Test)</h2>",
     "El examen de habilidades incluye maniobras de patio con conos en un patio privado de entrenamiento."),

    ("cambios-industria-2025",
     "blog-mid-hiring.jpg",
     "Reclutador de empresa de transporte entrevistando conductor en patio con flota de camiones Clase A al atardecer",
     "<h2>¿Qué Significa Todo Esto Para Ti?</h2>",
     "Las empresas de transporte están contratando activamente — la demanda por conductores certificados nunca fue mayor."),

    ("cdl-nacional",
     "blog-mid-state-line.jpg",
     "Camión Clase A rojo en autopista de Florida bajo señal aérea con bandera estadounidense al atardecer",
     "<h2>Intra-Estatal vs. Inter-Estatal: La Diferencia de Edad</h2>",
     "Con CDL inter-estatal puedes operar en los 50 estados — tu licencia de Florida es válida en todas partes."),

    ("regulaciones-cdl-florida",
     "blog-mid-dot-physical.jpg",
     "Examinadora médica tomando presión arterial a chofer hispano en oficina médica con tabla optométrica",
     "<h2>El Examen Médico DOT: Requisito No Negociable</h2>",
     "El examen médico DOT evalúa visión, presión arterial, audición y más — lo hace un examinador certificado del Registro Nacional FMCSA."),

    ("dominio-ingles-cdl",
     "blog-mid-elp-highway.jpg",
     "Inspectora FL DOT en autopista I-75 apuntando a señales de tránsito con camión Clase A de fondo",
     "<h2>Cómo Funciona la Evaluación ELP en una Inspección de Carretera</h2>",
     "En la evaluación ELP, un inspector puede pedirte leer señales de tránsito en inglés — nuestros instructores bilingües te preparan para esto."),

    ("salario-camionero-tampa",
     "blog-mid-port-tampa.jpg",
     "Grúa pórtico del Puerto de Tampa cargando contenedor sobre camión Clase A con horizonte de Tampa al atardecer",
     "<h3>Puerto de Tampa: La Prima Intermodal</h3>",
     "El Puerto de Tampa mueve millones de toneladas de carga al año — los conductores con experiencia intermodal ganan 20–30% más."),
]

SECTION_IMG_TMPL = """<figure class="article-section-image" style="margin:40px -24px;position:relative">
  <div style="position:relative;overflow:hidden;aspect-ratio:16/9;border-radius:12px;border:1px solid rgba(255,255,255,0.07)">
    <img src="../../images/{img}" alt="{alt}" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block"/>
    <div aria-hidden="true" style="position:absolute;inset:0;background:linear-gradient(180deg,transparent 60%,rgba(10,10,10,0.55) 100%);pointer-events:none"></div>
  </div>
  <figcaption style="margin-top:12px;font-size:13px;color:#9CA3AF;font-style:italic;line-height:1.5;text-align:center">{caption}</figcaption>
</figure>

"""


def process(slug: str, img: str, alt: str, marker: str, caption: str):
    path = BLOG / slug / "index.html"
    if not path.exists():
        return f"MISSING: {path}"
    html = path.read_text()
    if marker not in html:
        return f"SKIP (marker not found): {slug} — {marker}"
    block = SECTION_IMG_TMPL.format(img=img, alt=alt, caption=caption)
    # Preserve the H2/H3 indentation: insert block BEFORE the marker, with same leading whitespace
    # Find position of marker, then walk back to start of its line to capture indent
    idx = html.index(marker)
    line_start = html.rfind("\n", 0, idx) + 1
    indent = html[line_start:idx]
    # Apply indent to each line of the block
    indented_block = "".join(
        (indent + line if line.strip() else line)
        for line in block.splitlines(keepends=True)
    )
    new_html = html[:line_start] + indented_block + html[line_start:]
    path.write_text(new_html)
    return f"OK: {slug} <- {img}"


def main():
    for slug, img, alt, marker, caption in INSERTIONS:
        print(process(slug, img, alt, marker, caption))


if __name__ == "__main__":
    main()
