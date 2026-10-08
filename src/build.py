"""Assemble les fragments src/k1..k5.html en docs/index.html (site publié) et site.html (version artefact, libs CDN)."""
import json, os
S=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(S)
rd=lambda n: open(os.path.join(S,n),encoding='utf-8').read()
m=json.loads(rd('mark.json')); k1,k2,k3,k4,k5=(rd(f'k{i}.html') for i in range(1,6)); lenis=rd('lenis.min.js')
body=k2.replace('@@DL@@',m['DL']).replace('@@DR@@',m['DR']).replace('<!-- @@CTA -->\n','').replace('<!-- @@K3 -->\n','')+k3.replace('<!-- @@CTAFOOT -->\n',k4)+k5.replace('@@LENIS@@',lenis).replace('@@MARK@@',json.dumps(m,separators=(',',':')))
site=k1+body
open(os.path.join(R,'site.html'),'w',encoding='utf-8').write(site)
local=site.replace('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js','libs/gsap.min.js').replace('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js','libs/ScrollTrigger.min.js')
head,rest=local.split('<style>',1); css,rest2=rest.split('</style>',1)
full='<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'+head+'<style>\nhtml,body{margin:0}img{max-width:100%}[hidden]{display:none!important}\n'+css+'</style>\n</head>\n<body>\n'+rest2+'\n</body>\n</html>\n'
open(os.path.join(R,'docs','index.html'),'w',encoding='utf-8').write(full)
print('docs/index.html', len(full))
