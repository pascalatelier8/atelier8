"""Assemble src/k1..k5.html puis génère le site publié (docs/ par défaut) : pages FR/EN, données structurées, sitemap, robots, llms.txt.
Usage : python3 src/build.py [dossier_sortie]"""
import json, os, sys
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
sys.path.insert(0, S)
import seo
rd = lambda n: open(os.path.join(S, n), encoding='utf-8').read()
def assemble():
    m = json.loads(rd('mark.json')); k1, k2, k3, k4, k5 = (rd(f'k{i}.html') for i in range(1, 6)); lenis = rd('lenis.min.js')
    body = k2.replace('@@DL@@', m['DL']).replace('@@DR@@', m['DR']).replace('<!-- @@CTA -->\n', '').replace('<!-- @@K3 -->\n', '') + k3.replace('<!-- @@CTAFOOT -->\n', k4) + k5.replace('@@LENIS@@', lenis).replace('@@MARK@@', json.dumps(m, separators=(',', ':')))
    site = k1 + body
    local = site.replace('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js', 'libs/gsap.min.js').replace('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js', 'libs/ScrollTrigger.min.js')
    head, rest = local.split('<style>', 1); css, rest2 = rest.split('</style>', 1)
    return '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + head + '<style>\nhtml,body{margin:0}img{max-width:100%}[hidden]{display:none!important}\n' + css + '</style>\n</head>\n<body>\n' + rest2 + '\n</body>\n</html>\n'
if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'docs')
    full = assemble()
    F, Q = seo.build(full, out)
    print(out, len(F), 'films', len(Q), 'questions')
