#!/usr/bin/env python3
"""Bouwt de Engelse site retinalsurgery.info uit netvliesoperatie.info.

Gebruik: python3 mirror.py <bron> <doel>

Kopieert index.html, img/ en fonts/ uit de bron en maakt index.html Engels:
Engels als standaardtaal, de NL-knop gaat naar netvliesoperatie.info,
en titel, beschrijving, canonical en merknaam (RetinalSurgery.Info) staan
al in het Engels in de HTML voor zoekmachines en linkvoorbeelden.

Ontbreekt een onderdeel dat nodig is om de site Engels te laten werken,
dan stopt het script met een fout en blijft de vorige versie online.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

EN = 'https://retinalsurgery.info/'
NL = 'https://netvliesoperatie.info/'
BRAND_NL, BRAND_EN = 'Netvliesoperatie.Info', 'RetinalSurgery.Info'
SKIP = {'.git', '.github', 'CNAME', 'README.md'}

warnings = []


def rep(s, old, new, required=False):
    n = s.count(old)
    if n == 0:
        if required:
            sys.exit('FOUT: niet gevonden: ' + old[:80])
        warnings.append('niet gevonden: ' + old[:80])
        return s
    return s.replace(old, new)


def main(src, dst):
    src, dst = Path(src), Path(dst)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for p in src.iterdir():
        if p.name in SKIP:
            continue
        (shutil.copytree if p.is_dir() else shutil.copy2)(p, dst / p.name)

    s = (src / 'index.html').read_text(encoding='utf-8')

    # Woordenboek: merknaam en zoekveld voor dit domein
    m = re.search(r'(<script type="application/json" id="i18n-en">)(.*?)(</script>)', s, re.S)
    if not m:
        sys.exit('FOUT: Engels woordenboek (#i18n-en) ontbreekt')
    d = json.loads(m.group(2))
    for k, v in d.items():
        d[k] = v.replace(BRAND_NL, BRAND_EN).replace('netvliesoperatie.info', 'retinalsurgery.info')
    dj = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    s = s[:m.start(2)] + dj + s[m.end(2):]

    # Taalkeuze: Engels standaard; NL-knop naar het Nederlandse domein
    s = rep(s, "  var L = 'nl';", "  var L = 'en';", required=True)
    s = rep(s, "    else { var s = localStorage.getItem('site-lang'); if (s === 'en' || s === 'nl') L = s; }\n", "")
    s = rep(s, "if (b) setLang(b.getAttribute('data-setlang'));",
            "if (b) {\n      var l = b.getAttribute('data-setlang');\n"
            "      if (l === 'nl') { location.href = '" + NL + "?lang=nl' + location.hash; return; }\n"
            "      setLang(l);\n    }", required=True)
    s = rep(s, "var site = '" + BRAND_NL + "';", "var site = '" + BRAND_EN + "';")

    # Kop van het document: taal, canonical, Open Graph, hreflang
    h_end = s.find('</head>')
    head, rest = s[:h_end], s[h_end:]
    head = rep(head, '<html lang="nl"', '<html lang="en"')
    head = rep(head, '<link rel="canonical" href="' + NL + '">',
               '<link rel="canonical" href="' + EN + '">\n'
               '<link rel="alternate" hreflang="en" href="' + EN + '">\n'
               '<link rel="alternate" hreflang="nl" href="' + NL + '">\n'
               '<link rel="alternate" hreflang="x-default" href="' + NL + '">')
    head = rep(head, '<meta property="og:url" content="' + NL + '">',
               '<meta property="og:url" content="' + EN + '">')
    head = rep(head, '<meta property="og:locale" content="nl_NL">\n<meta property="og:locale:alternate" content="en_GB">',
               '<meta property="og:locale" content="en_GB">\n<meta property="og:locale:alternate" content="nl_NL">')
    head = rep(head, '<meta property="og:site_name" content="' + BRAND_NL + '">',
               '<meta property="og:site_name" content="' + BRAND_EN + '">')

    def title(mt):
        en = d.get(mt.group(2))
        return mt.group(1) + (html.escape(en, quote=False) if en else mt.group(3)) + '</title>'
    head = re.sub(r'(<title data-i18n="([0-9a-f]+)">)(.*?)</title>', title, head, count=1, flags=re.S)

    def content(mt):
        en = d.get(mt.group(3))
        if not en:
            return mt.group(0)
        return mt.group(1) + html.escape(en, quote=True) + mt.group(2) + mt.group(3) + mt.group(4)
    head = re.sub(r'(<meta [^>]*?content=")[^"]*(" data-i18n-attr="content:)([^"|]+)(")', content, head)

    s = head + rest
    (dst / 'index.html').write_text(s, encoding='utf-8')
    (dst / '.nojekyll').write_text('')
    for w in warnings:
        print('let op:', w)
    print('klaar:', dst / 'index.html', len(s.encode('utf-8')), 'bytes')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
