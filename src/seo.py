"""Atelier 8 : génère les pages indexables (FR + EN), les données structurées, robots.txt, sitemap.xml et llms.txt.

Entrée : le HTML complet de la page unique (toutes les vues), chemins médias relatifs.
Sortie : OUT/index.html, OUT/films/index.html … OUT/en/…, OUT/robots.txt, OUT/sitemap.xml, OUT/llms.txt,
OUT/confidentialite/index.html, OUT/404.html.
"""
import html as H, json, os, re

SITE = 'https://atelier8.io'
TODAY = '2026-10-08'
VIEWS = ['accueil', 'films', 'formats', 'atelier', 'faq', 'brief']
MAIL = 'pascal@atelier8.io'
OG = SITE + '/media/og-atelier8.jpg'
LOGO = SITE + '/media/apple-touch-icon.png'

# Dates de mise en ligne des films (premier commit du fichier dans le dépôt)
UPLOAD = {'nomos': '2026-10-09T09:00:00+00:00', 'aesop': '2026-10-09T09:00:00+00:00', 'on': '2026-10-09T09:00:00+00:00', 'sonos': '2026-10-09T09:00:00+00:00', 'boom': '2026-10-08T13:33:20+00:00', 'hem': '2026-10-08T13:33:20+00:00',
          'teenage-engineering': '2026-10-08T13:33:20+00:00', 'polestar-v3': '2026-10-08T14:33:36+00:00'}
UPLOAD_DEFAULT = '2026-10-08T10:48:51+00:00'

T = {
 'fr': {
  'accueil': ('Atelier 8 · Studio de motion design à Paris et Hong Kong',
              'Studio de motion design indépendant entre Paris et Hong Kong. Films de marque de 15 à 90 s, script, voix, musique et montage. Dès 2 500 € HT, livrés en 5 à 30 jours.'),
  'films':   ('Films en motion design : 27 réalisations · Atelier 8',
              'Vingt-sept films en motion design : concepts pour des marques SaaS, tech et luxe, démos pour agences et showreel. 15 à 75 secondes, script, image et son.'),
  'formats': ('Prix d’un film en motion design, dès 2 500 € · Atelier 8',
              'Trois formats à prix écrits : Signal 15–30 s dès 2 500 € HT, Portrait 45–90 s dès 4 500 € HT, Campagne dès 7 500 € HT. Délais, révisions, droits inclus.'),
  'atelier': ('L’atelier : Pascal EK Loui et cinq agents IA · Atelier 8',
              'Atelier 8, c’est Pascal EK Loui : quinze ans de design produit entre Paris et Hong Kong, un regard humain sur chaque plan et cinq agents IA, un par métier.'),
  'faq':     ('FAQ film motion design : prix, délais, droits · Atelier 8',
              'Seize réponses courtes : prix d’un film en motion design, délais, révisions, paiement, droits d’utilisation, usage de l’IA, durée idéale d’une vidéo d’entreprise.'),
  'brief':   ('Demander un devis de film en motion design · Atelier 8',
              'Envoyez votre brief en deux minutes : l’adresse de votre site et quelques lignes. Première lecture et devis sous deux jours ouvrés, par Pascal lui-même.'),
 },
 'en': {
  'accueil': ('Atelier 8 · Motion design studio in Paris and Hong Kong',
              'Independent motion design studio between Paris and Hong Kong. Brand films of 15 to 90 s: script, voice, music and edit. From €2,500, delivered in 5 to 30 days.'),
  'films':   ('Motion design films: 27 projects · Atelier 8',
              'Twenty-seven motion design films: concepts for SaaS, tech and luxury brands, agency demos and a showreel. 15 to 75 seconds, script, picture and sound.'),
  'formats': ('Motion design film pricing from €2,500 · Atelier 8',
              'Three formats with written prices: Signal 15–30 s from €2,500, Portrait 45–90 s from €4,500, Campaign from €7,500, excl. VAT. Timing, revisions, rights included.'),
  'atelier': ('The studio: Pascal EK Loui and five AI agents · Atelier 8',
              'Atelier 8 is Pascal EK Loui: fifteen years of product design between Paris and Hong Kong, a human eye on every shot and five AI agents, one per craft.'),
  'faq':     ('Motion design film FAQ: pricing, timing, rights · Atelier 8',
              'Sixteen short answers: what a motion design film costs, timing, revisions, payment, usage rights, how AI is used, and how long a company video should be.'),
  'brief':   ('Request a motion design film quote · Atelier 8',
              'Send your brief in two minutes: your website and a few lines. First read and a quote within two working days, from Pascal himself.'),
 },
}
NAV = {'fr': {'accueil': 'Accueil', 'films': 'Films', 'formats': 'Formats', 'atelier': 'L’atelier', 'faq': 'FAQ', 'brief': 'Brief'},
       'en': {'accueil': 'Home', 'films': 'Films', 'formats': 'Formats', 'atelier': 'The studio', 'faq': 'FAQ', 'brief': 'Brief'}}
PAGETYPE = {'accueil': 'WebPage', 'films': 'CollectionPage', 'formats': 'WebPage', 'atelier': 'AboutPage', 'faq': 'FAQPage', 'brief': 'ContactPage'}

OFFERS = [
 ('signal', 'Signal', 2500, (5, 10), 2,
  {'fr': 'Film court de 15 à 30 secondes : une seule idée, écrite et storyboardée pour votre marque, musique et sous-titres intégrés, livré en 16:9, 9:16, 1:1 et 4:5.',
   'en': 'A 15 to 30 second film: one idea, written and storyboarded for your brand, music and subtitles included, delivered in 16:9, 9:16, 1:1 and 4:5.'}),
 ('portrait', 'Portrait', 4500, (10, 20), 2,
  {'fr': 'Film de marque de 45 à 90 secondes qui explique votre société : voix off en français ou en anglais, musique, sound design, sous-titres, tous les formats réseaux.',
   'en': 'A 45 to 90 second brand film that explains your company: French or English voice-over, music, sound design, subtitles, every social format.'}),
 ('campagne', 'Campagne', 7500, (25, 30), 3,
  {'fr': 'Cinq films : un Portrait, un Signal et trois déclinaisons courtes pour les réseaux, en français et en anglais.',
   'en': 'Five films: one Portrait, one Signal and three short cut-downs for social, in French and English.'}),
]


def url(lang, v):
    return SITE + ('/en' if lang == 'en' else '') + ('/' if v == 'accueil' else f'/{v}/')


def txt(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', H.unescape(s)).strip()


def span(block, lang):
    m = re.search(rf'<(?:span|p) lang="{lang}"[^>]*>(.*?)</(?:span|p)>', block, re.S)
    return txt(m.group(1)) if m else txt(block)


def films(src):
    out = []
    for a in re.findall(r'<article class="film[^"]*">(.*?)</article>', src, re.S):
        d = dict(re.findall(r'data-(src|src-en|title)="([^"]*)"', a))
        poster = re.search(r'<img src="([^"]+)"', a).group(1)
        h3 = re.search(r'<h3>(.*?)</h3>', a, re.S).group(1)
        brand = txt(h3.split('—')[0]) if '—' in h3 else txt(h3)

        def title(lang):
            if '—' not in h3:
                return txt(h3)
            rest = h3.split('—', 1)[1]
            return brand + ' — ' + (span(rest, lang) if 'lang=' in rest else txt(rest))
        dl = dict()
        for dt, dd in re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', a, re.S):
            dl[span(dt, 'fr')] = dd
        fmt = txt(dl.get('Format', ''))
        sec = re.search(r'(\d+)\s*s', fmt)
        d = {k: x.lstrip('/') for k, x in d.items()}
        poster = poster.lstrip('/')
        slug = os.path.basename(d['src'])[:-4]
        kind = 'demo' if 'tag demo' in a else ('concept' if 'tag concept' in a else 'showreel')
        out.append(dict(slug=slug, src=d['src'], src_en=d.get('src-en'), poster=poster, brand=brand,
                        title={l: title(l) for l in ('fr', 'en')}, kind=kind,
                        nature={l: span(dl['Nature'], l) for l in ('fr', 'en')} if 'Nature' in dl else None,
                        sector={l: span(dl['Secteur'], l) for l in ('fr', 'en')} if 'Secteur' in dl else None,
                        secs=int(sec.group(1)) if sec else 30))
    return out


def faqs(src):
    sec = src.split('data-view="faq"', 1)[1].split('<!-- BRIEF -->', 1)[0]
    out = []
    for q, a in re.findall(r'<summary><span class="n">\d+</span><span>(.*?)</span><span class="x"></span></summary><div class="a">(.*?)</div></details>', sec, re.S):
        item = {}
        for l in ('fr', 'en'):
            ans = span(a, l)
            sm = re.search(r'<small>(.*?)</small>', a, re.S)
            if sm:
                ans += ' ' + span(sm.group(1), l)
            item[l] = (span(q, l), ans)
        out.append(item)
    return out



DTF_DATE = '2026-10-09T15:00:00+00:00'
def dtf_video(lang):
    fr = lang == 'fr'
    return {'@type': 'VideoObject', '@id': SITE + '/#deux-traits-' + lang,
            'name': 'Atelier 8 — Deux traits' if fr else 'Atelier 8 — Two Strokes',
            'description': ('Le film de marque d’Atelier 8, studio de motion design à Paris et Hong Kong : l’impact, la méthode en quatre étapes, les cinq agents IA et les films, en 61 secondes.' if fr
                            else 'Atelier 8’s own brand film, a motion design studio in Paris and Hong Kong: the impact, the four-step method, the five AI agents and the films, in 61 seconds.'),
            'thumbnailUrl': SITE + '/media/films/atelier8-deux-traits-' + lang + '.jpg',
            'contentUrl': SITE + '/media/films/atelier8-deux-traits-' + lang + '.mp4',
            'uploadDate': DTF_DATE, 'duration': 'PT61S', 'width': 1600, 'height': 900, 'inLanguage': lang,
            'creator': {'@id': SITE + '/#org'}, 'publisher': {'@id': SITE + '/#org'}, 'isFamilyFriendly': True,
            'hasPart': [{'@type': 'Clip', 'name': n, 'startOffset': a, 'endOffset': b, 'url': url(lang, 'accueil') + '#dtf'}
                        for n, a, b in zip(['L’impact', 'Deux traits', 'La méthode', 'Les agents', 'Les films', 'La signature'] if fr
                                           else ['Impact', 'Two strokes', 'The method', 'The agents', 'The films', 'The signature'],
                                           [0, 9, 13, 29, 35, 55], [9, 13, 29, 35, 55, 61])]}

def graph(lang, v, F, Q):
    org = {
        '@type': ['Organization', 'ProfessionalService'], '@id': SITE + '/#org', 'name': 'Atelier 8', 'url': SITE + '/',
        'logo': {'@type': 'ImageObject', 'url': LOGO, 'width': 180, 'height': 180}, 'image': OG, 'email': MAIL,
        'description': T[lang]['accueil'][1], 'slogan': 'Un film qui marque.' if lang == 'fr' else 'A film that leaves a mark.',
        'founder': {'@id': SITE + '/#pascal'}, 'foundingDate': '2026',
        'sameAs': ['https://www.instagram.com/atelier8.io/', 'https://www.linkedin.com/company/atelier8-io/'],
        'address': [{'@type': 'PostalAddress', 'addressLocality': 'Paris', 'addressCountry': 'FR'},
                    {'@type': 'PostalAddress', 'addressLocality': 'Hong Kong', 'addressCountry': 'HK'}],
        'areaServed': [{'@type': 'Country', 'name': 'France'}, {'@type': 'Place', 'name': 'Hong Kong'},
                       {'@type': 'Place', 'name': 'Europe'}, {'@type': 'Place', 'name': 'Asia'}],
        'knowsLanguage': ['fr', 'en'], 'priceRange': '2 500 € – 7 500 € HT' if lang == 'fr' else '€2,500 – €7,500 excl. VAT',
        'knowsAbout': ['Motion design', 'Brand film', 'Explainer video', 'Product video', 'SaaS video', 'Animation', 'Sound design',
                       'Storyboard', 'Video scriptwriting', 'AI-assisted video production'],
        'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'email': MAIL, 'availableLanguage': ['French', 'English'],
                         'areaServed': ['FR', 'HK', 'EU']},
        'hasOfferCatalog': {'@id': SITE + '/#catalogue'},
    }
    person = {
        '@type': 'Person', '@id': SITE + '/#pascal', 'name': 'Pascal EK Loui', 'url': url(lang, 'atelier'),
        'jobTitle': 'Fondateur et directeur de création, Atelier 8' if lang == 'fr' else 'Founder and creative director, Atelier 8',
        'worksFor': {'@id': SITE + '/#org'}, 'knowsLanguage': ['fr', 'en'],
        'description': ('Designer produit depuis quinze ans pour de grandes marques et des start-ups, entre Paris et Hong Kong. '
                        'Fondateur d’Atelier 8, il écrit, dirige et valide chaque film en motion design.') if lang == 'fr' else
                       ('Product designer for fifteen years for large brands and start-ups, between Paris and Hong Kong. '
                        'Founder of Atelier 8, he writes, directs and signs off every motion design film.'),
        'knowsAbout': ['Motion design', 'Product design', 'UX design', 'Art direction'],
        'homeLocation': [{'@type': 'Place', 'name': 'Paris'}, {'@type': 'Place', 'name': 'Hong Kong'}],
    }
    site = {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Atelier 8', 'inLanguage': ['fr', 'en'],
            'publisher': {'@id': SITE + '/#org'}}
    cat = {'@type': 'OfferCatalog', '@id': SITE + '/#catalogue',
           'name': 'Formats de films en motion design' if lang == 'fr' else 'Motion design film formats', 'itemListElement': []}
    for slug, name, price, (dmin, dmax), rev, desc in OFFERS:
        nm = name if lang == 'fr' or name != 'Campagne' else 'Campaign'
        cat['itemListElement'].append({
            '@type': 'Offer', 'name': nm, 'url': url(lang, 'formats'), 'description': desc[lang],
            'price': price, 'priceCurrency': 'EUR',
            'priceSpecification': {'@type': 'UnitPriceSpecification', 'price': price, 'priceCurrency': 'EUR',
                                   'valueAddedTaxIncluded': False, 'description': 'À partir de, hors taxes' if lang == 'fr' else 'From, excluding VAT'},
            'deliveryLeadTime': {'@type': 'QuantitativeValue', 'minValue': dmin, 'maxValue': dmax, 'unitCode': 'DAY',
                                 'description': 'jours ouvrés' if lang == 'fr' else 'working days'},
            'itemOffered': {'@type': 'Service', 'name': ('Film motion design ' if lang == 'fr' else 'Motion design film ') + nm,
                            'serviceType': 'Motion design', 'provider': {'@id': SITE + '/#org'},
                            'areaServed': ['FR', 'HK', 'EU']},
            'seller': {'@id': SITE + '/#org'}})
    u = url(lang, v)
    page = {'@type': PAGETYPE[v], '@id': u + '#page', 'url': u, 'name': T[lang][v][0], 'description': T[lang][v][1],
            'inLanguage': lang, 'isPartOf': {'@id': SITE + '/#website'}, 'about': {'@id': SITE + '/#org'},
            'primaryImageOfPage': {'@type': 'ImageObject', 'url': OG}, 'dateModified': TODAY}
    G = [org, person, site, cat, page]
    if v != 'accueil':
        page['breadcrumb'] = {'@id': u + '#breadcrumb'}
        G.append({'@type': 'BreadcrumbList', '@id': u + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Atelier 8', 'item': url(lang, 'accueil')},
            {'@type': 'ListItem', 'position': 2, 'name': NAV[lang][v], 'item': u}]})
    if v == 'faq':
        page['mainEntity'] = [{'@type': 'Question', 'name': q[lang][0],
                               'acceptedAnswer': {'@type': 'Answer', 'text': q[lang][1]}} for q in Q]
    if v == 'atelier':
        page['mainEntity'] = {'@id': SITE + '/#pascal'}
    if v in ('films', 'accueil'):
        items = []
        for i, f in enumerate(F if v == 'films' else [f for f in F if f['kind'] == 'showreel']):
            src = f['src_en'] if (lang == 'en' and f['src_en']) else f['src']
            if f['nature']:
                d = f['nature'][lang]
            else:
                d = ('Showreel 2026 d’Atelier 8 pour UX Design Paris, en français et en anglais.' if lang == 'fr'
                     else 'Atelier 8’s 2026 showreel for UX Design Paris, in French and English.')
            if f['sector']:
                d += (' Secteur : ' if lang == 'fr' else ' Sector: ') + f['sector'][lang] + '.'
            d += (f' Film en motion design de {f["secs"]} secondes, script, image et son par Atelier 8.' if lang == 'fr'
                  else f' A {f["secs"]}-second motion design film, script, picture and sound by Atelier 8.')
            vo = {'@type': 'VideoObject', '@id': SITE + '/films/#' + f['slug'], 'name': f['title'][lang], 'description': d,
                  'thumbnailUrl': SITE + '/' + f['poster'], 'contentUrl': SITE + '/' + src,
                  'uploadDate': UPLOAD.get(f['slug'], UPLOAD_DEFAULT), 'duration': f'PT{f["secs"]}S',
                  'width': 1280, 'height': 720, 'inLanguage': lang if f['kind'] != 'showreel' else ['fr', 'en'],
                  'creator': {'@id': SITE + '/#org'}, 'publisher': {'@id': SITE + '/#org'}, 'isFamilyFriendly': True}
            items.append({'@type': 'ListItem', 'position': i + 1, 'item': vo})
        if v == 'films':
            page['mainEntity'] = {'@type': 'ItemList', 'numberOfItems': len(items), 'itemListElement': items}
        elif items:
            G.append(items[0]['item'])
    if v == 'accueil':
        G.append(dtf_video(lang))
    return {'@context': 'https://schema.org', '@graph': G}


def page(full, lang, v, F, Q):
    s = full
    title, desc = T[lang][v]
    u = url(lang, v)
    e = lambda x: H.escape(x, quote=True)
    if lang == 'en':
        s = s.replace('<html lang="fr">', '<html lang="en">', 1)
    s = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', s, count=1)
    alt = ''.join(f'<link rel="alternate" hreflang="{hl}" href="{url(L, v)}">\n' for hl, L in (('fr', 'fr'), ('en', 'en'), ('x-default', 'fr')))
    s = re.sub(r'<link rel="canonical" href="[^"]*">\n', f'<link rel="canonical" href="{u}">\n{alt}'
               '<meta name="robots" content="index, follow, max-image-preview:large, max-video-preview:-1, max-snippet:-1">\n'
               '<meta name="author" content="Pascal EK Loui">\n', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{u}">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(title)}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(desc)}">', s, count=1)
    s = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{e(title)}">', s, count=1)
    s = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{e(desc)}">', s, count=1)
    loc, alt_loc = ('en_GB', 'fr_FR') if lang == 'en' else ('fr_FR', 'en_GB')
    s = s.replace('<meta property="og:locale" content="fr_FR">',
                  f'<meta property="og:locale" content="{loc}">\n<meta property="og:locale:alternate" content="{alt_loc}">', 1)
    if lang == 'en':
        s = re.sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="A rock in the smoke, engraved with a glowing 八 sign, next to the title “A film that leaves a mark.” by Atelier 8">', s, count=1)
    if v != 'accueil':  # la vidéo du hero ne bloque pas le chargement des autres pages
        s = re.sub(r'<link rel="preload" as="fetch" href="/media/hero-lo[^"]*\.mp4"[^>]*>\n', '', s)
    ld = json.dumps(graph(lang, v, F, Q), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    s = s.replace('</head>', f'<script type="application/ld+json">{ld}</script>\n</head>', 1)
    # vue active
    s = s.replace('<div class="view on" data-view="accueil"', '<div class="view" data-view="accueil"', 1)
    s = s.replace(f'<div class="view" data-view="{v}"', f'<div class="view on" data-view="{v}"', 1)
    if lang == 'en':
        head, body = s.split('<body>', 1)

        def flip(m):
            tag = re.sub(r'\shidden(?![\w=-])', '', m.group(0))
            return tag[:-1] + ' hidden>' if f'lang="fr"' in tag else tag
        parts = re.split(r'(<script\b.*?</script>)', body, flags=re.S)
        body = ''.join(x if x.startswith('<script') else re.sub(r'<[a-zA-Z][a-zA-Z0-9]*\b[^<>]*\slang="(?:fr|en)"[^<>]*>', flip, x) for x in parts)
        body = body.replace('aria-label="Lire le film ', 'aria-label="Play the film ').replace(' · film en motion design, Atelier 8"', ' · motion design film by Atelier 8"')
        for vv in VIEWS[1:]:
            body = body.replace(f'href="/{vv}/"', f'href="/en/{vv}/"')
        body = body.replace('href="/" data-go', 'href="/en/" data-go')
        s = head + '<body>' + body
    return s


def absolutize(full):
    return re.sub(r'(?<=["\'(\s,])(media|libs)/', r'/\1/', full)


def seo_titles():
    return json.dumps({l: {v: T[l][v][0] for v in VIEWS} for l in T}, ensure_ascii=False, separators=(',', ':'))


def robots():
    bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User',
            'Google-Extended', 'Applebot', 'Applebot-Extended', 'Bingbot', 'DuckAssistBot', 'MistralAI-User', 'meta-externalagent', 'CCBot']
    r = '# Atelier 8 : tout le site est ouvert aux moteurs de recherche et aux moteurs de réponse IA.\nUser-agent: *\nAllow: /\n\n'
    r += ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots)
    return r + f'Sitemap: {SITE}/sitemap.xml\n'


def sitemap(F):
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">']
    pr = {'accueil': '1.0', 'films': '0.9', 'formats': '0.9', 'atelier': '0.7', 'faq': '0.8', 'brief': '0.6'}
    for lang in ('fr', 'en'):
        for v in VIEWS:
            x.append('<url>')
            x.append(f'<loc>{url(lang, v)}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pr[v]}</priority>')
            for hl, L in (('fr', 'fr'), ('en', 'en'), ('x-default', 'fr')):
                x.append(f'<xhtml:link rel="alternate" hreflang="{hl}" href="{url(L, v)}"/>')
            if v == 'accueil':
                dv = dtf_video(lang)
                x.append('<video:video>'
                         f'<video:thumbnail_loc>{dv["thumbnailUrl"]}</video:thumbnail_loc>'
                         f'<video:title>{H.escape(dv["name"])}</video:title>'
                         f'<video:description>{H.escape(dv["description"])}</video:description>'
                         f'<video:content_loc>{dv["contentUrl"]}</video:content_loc>'
                         '<video:duration>61</video:duration>'
                         f'<video:publication_date>{DTF_DATE}</video:publication_date>'
                         '<video:family_friendly>yes</video:family_friendly></video:video>')
            if v == 'films':
                for f in F:
                    src = f['src_en'] if (lang == 'en' and f['src_en']) else f['src']
                    d = (f['nature'][lang] if f['nature'] else ('Showreel 2026, français et anglais.' if lang == 'fr' else '2026 showreel, French and English.'))
                    x.append('<video:video>'
                             f'<video:thumbnail_loc>{SITE}/{f["poster"]}</video:thumbnail_loc>'
                             f'<video:title>{H.escape(f["title"][lang])}</video:title>'
                             f'<video:description>{H.escape(d)}</video:description>'
                             f'<video:content_loc>{SITE}/{src}</video:content_loc>'
                             f'<video:duration>{f["secs"]}</video:duration>'
                             f'<video:publication_date>{UPLOAD.get(f["slug"], UPLOAD_DEFAULT)}</video:publication_date>'
                             '<video:family_friendly>yes</video:family_friendly></video:video>')
            x.append('</url>')
    x.append(f'<url><loc>{SITE}/confidentialite/</loc><lastmod>{TODAY}</lastmod><priority>0.2</priority></url>')
    x.append('</urlset>')
    return '\n'.join(x) + '\n'


def llms(F, Q):
    L = ['# Atelier 8', '',
         '> Atelier 8 est un studio de motion design indépendant entre Paris et Hong Kong, fondé par Pascal EK Loui. '
         'Il réalise des films de marque de 15 à 90 secondes (script, storyboard, voix, musique, montage) pour des start-ups, '
         'des éditeurs SaaS et des marques premium, en français et en anglais. Prix publics dès 2 500 € HT, livraison en 5 à 30 jours ouvrés.',
         '',
         'Atelier 8 is an independent motion design studio between Paris and Hong Kong, founded by Pascal EK Loui. It makes 15 to 90 second '
         'brand films in French and English, with published prices from €2,500 excluding VAT.', '',
         '## Faits clés', '',
         '- Nom : Atelier 8 (signe : 八). Site : https://atelier8.io',
         '- Fondateur : Pascal EK Loui, quinze ans de design produit pour de grandes marques et des start-ups, entre Paris et Hong Kong.',
         '- Villes : Paris (France) et Hong Kong. Langues : français, anglais. Facturation depuis la France ou Hong Kong selon le projet.',
         '- Méthode : cinq temps (brief, devis, conception, production, livraison) et trois validations (script et storyboard, première version, livraison).',
         '- Équipe : un regard humain (Pascal) et cinq agents IA, un par métier (stratégie, produit, scénario, storyboard, motion design). '
         'La direction artistique, le montage final et chaque validation restent humains.',
         f'- Contact : {MAIL}. Réponse et devis sous deux jours ouvrés. Brief en ligne : https://atelier8.io/brief/',
         '- Réseaux : Instagram https://www.instagram.com/atelier8.io/ · LinkedIn https://www.linkedin.com/company/atelier8-io/', '',
         '## Formats et prix (hors taxes)', '']
    for slug, name, price, (dmin, dmax), rev, desc in OFFERS:
        L.append(f'- {name} : à partir de {price:,} € HT'.replace(',', ' ') + f', {dmin} à {dmax} jours ouvrés, {rev} révisions. {desc["fr"]}')
    L += ['- Options : seconde langue 390 €, révision supplémentaire 180 €, express (délai divisé par deux) +30 %.',
          '- Paiement : 50 % à la commande, solde à la livraison. Droits d’exploitation cédés sans limite de durée ni de territoire une fois le film payé.',
          '- Formats livrés : 16:9, 9:16, 1:1 et 4:5.', '',
          '## Films (portfolio)', '',
          'Les films de marques tierces sont des concepts ou des démos : aucun n’a été commandé ni validé par les marques citées.', '']
    for f in F:
        k = {'concept': 'concept, démo non officielle', 'demo': 'démo réalisée pour une agence, non validée par la marque', 'showreel': 'showreel FR/EN'}[f['kind']]
        L.append(f'- {f["title"]["fr"]} ({f["secs"]} s, {k}) : {SITE}/{f["src"]}')
    L += ['', '## Questions fréquentes', '']
    for q in Q:
        L.append(f'### {q["fr"][0]}')
        L.append(q['fr'][1]); L.append('')
    L += ['## Pages', '',
          f'- [Accueil]({url("fr", "accueil")}) · [English]({url("en", "accueil")})',
          f'- [Films]({url("fr", "films")}) : 27 films, nature de chaque film précisée',
          f'- [Formats et prix]({url("fr", "formats")})',
          f'- [L’atelier]({url("fr", "atelier")}) : Pascal EK Loui et les cinq agents IA',
          f'- [FAQ]({url("fr", "faq")})',
          f'- [Brief et devis]({url("fr", "brief")})', '']
    return '\n'.join(L)


PRIVACY = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Confidentialité · Atelier 8</title>
<meta name="description" content="Politique de confidentialité d’Atelier 8 : quelles données sont traitées quand vous envoyez un brief, pourquoi, combien de temps, et vos droits.">
<link rel="canonical" href="https://atelier8.io/confidentialite/"><meta name="robots" content="index, follow">
<link rel="icon" type="image/png" sizes="32x32" href="/media/favicon-32.png">
<style>
@font-face{font-family:'Jost';font-weight:300;font-display:swap;src:url(/media/fonts/jost-300.woff2) format('woff2')}@font-face{font-family:'Jost';font-weight:400;font-display:swap;src:url(/media/fonts/jost-400.woff2) format('woff2')}@font-face{font-family:'JetBrains Mono';font-weight:400;font-display:swap;src:url(/media/fonts/jbmono-400.woff2) format('woff2')}:root{color-scheme:dark}body{margin:0;background:#090908;color:#EFEDE6;font:17px/1.65 'Jost','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased}
main{max-width:720px;margin:0 auto;padding:56px 20px 96px}a{color:#C99B45}h1{font-weight:300;font-size:clamp(34px,7vw,56px);letter-spacing:.02em;line-height:1.05;margin:28px 0 8px;text-transform:uppercase}
h2{font-weight:400;font-size:19px;margin:40px 0 8px;color:#F4E1A6}p,li{color:rgba(239,237,230,.78)}small{color:rgba(239,237,230,.6);font-family:'JetBrains Mono',ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;font-size:11px}
.top{display:flex;justify-content:space-between;align-items:center}.top a{text-decoration:none;letter-spacing:.2em;font-size:12px;font-family:'JetBrains Mono',ui-monospace,monospace;color:#EFEDE6}hr{border:0;border-top:1px solid rgba(232,214,178,.13);margin:56px 0 24px}
</style></head><body><main>
<div class="top"><a href="/">← ATELIER 8</a><a href="#en">EN</a></div>
<h1>Confidentialité</h1><small>Mise à jour : 8 octobre 2026</small>
<h2>Qui traite vos données</h2><p>Atelier 8, studio de motion design de Pascal EK Loui. Contact : <a href="mailto:pascal@atelier8.io">pascal@atelier8.io</a>.</p>
<h2>Ce que ce site collecte</h2><p>Le formulaire de brief transmet vos réponses par e-mail à Pascal, via le service d’envoi de formulaires FormSubmit (formsubmit.co) ; rien n’est enregistré sur le site lui-même. Si l’envoi échoue, le brief s’ouvre dans votre propre messagerie et c’est vous qui l’envoyez. Seule la mesure d’audience, si vous l’acceptez, collecte des données de navigation (voir ci-dessous).</p>
<h2>Cookies et mesure d’audience</h2><p>Ce site utilise Google Analytics pour compter les visites et comprendre quelles pages intéressent (pages vues, durée, pays, type d’appareil, source de la visite). Il ne se charge <strong>qu’après votre accord</strong>, donné dans le bandeau affiché à votre première visite. Si vous refusez ou ignorez le bandeau, aucun cookie de mesure n’est déposé.</p>
<p>Avec votre accord, Google dépose les cookies <code>_ga</code> et <code>_ga_DJGKTQ3VHV</code>, valables 13 mois au plus. Les signaux publicitaires et Google Signals sont désactivés : vos données ne servent ni à la publicité ni au profilage. Google Ireland Ltd et Google LLC traitent ces données ; les transferts vers les États-Unis reposent sur le Data Privacy Framework UE–États-Unis.</p>
<p>Votre choix (accepter ou refuser) est gardé six mois dans le stockage de votre navigateur, puis la question vous est reposée. Vous pouvez le changer à tout moment : lien « Gérer les cookies » en pied de page, ou bouton ci-dessous.</p>
<p><button type="button" id="resetConsent" style="font:inherit;color:#090908;background:#C99B45;border:0;border-radius:999px;padding:10px 18px;cursor:pointer">Revoir mon choix</button> <span id="resetMsg" style="margin-left:10px"></span></p>
<p>Aucun autre traceur : pas de publicité, pas de pixel de réseau social, pas de vidéo hébergée chez un tiers.</p>
<h2>Ce que contient votre brief</h2><p>Votre nom, votre e-mail, votre téléphone si vous le donnez, l’adresse de votre site, quelques lignes sur votre projet et, si vous le souhaitez, des liens de référence. Ces informations servent à une seule chose : vous répondre et établir un devis. Elles ne sont ni revendues, ni partagées, ni utilisées pour de la prospection.</p>
<h2>Base légale et durée</h2><p>Le traitement repose sur votre demande, avant tout contrat (article 6.1.b du RGPD). Les échanges sont conservés trois ans après le dernier contact s’ils n’aboutissent pas, puis supprimés ; si un projet est signé, les pièces comptables sont gardées le temps exigé par la loi.</p>
<h2>Hébergement et prestataires</h2><p>Le site est hébergé par Vercel Inc. (États-Unis), qui traite les journaux techniques de connexion (adresse IP, navigateur) pour servir les pages. Les polices de caractères et les vidéos sont hébergées sur le site lui-même. Sans votre accord pour la mesure d’audience, aucun appel n’est fait à Google ni à un autre tiers pendant votre visite. Les briefs du formulaire sont acheminés par FormSubmit (formsubmit.co), puis reçus, comme tous les e-mails, sur une messagerie hébergée par IONOS.</p>
<h2>Vos droits</h2><p>Vous pouvez demander l’accès, la rectification ou la suppression de vos données, ou vous opposer à leur traitement, en écrivant à <a href="mailto:pascal@atelier8.io">pascal@atelier8.io</a>. Réponse sous un mois. En cas de désaccord, vous pouvez saisir la CNIL (cnil.fr). Pour les clients de Hong Kong, la Personal Data (Privacy) Ordinance s’applique également.</p>
<hr id="en">
<h1>Privacy</h1>
<p>Atelier 8 (Pascal EK Loui, <a href="mailto:pascal@atelier8.io">pascal@atelier8.io</a>) uses Google Analytics to count visits, <strong>only after you accept</strong> in the banner shown on your first visit. If you decline or ignore it, no analytics cookie is set. With consent, Google sets <code>_ga</code> and <code>_ga_DJGKTQ3VHV</code> (13 months max); advertising features and Google Signals are off. Transfers to the US rely on the EU–US Data Privacy Framework. Your choice is kept six months in your browser storage; change it any time with “Cookie settings” in the footer or the button above. The brief form prepares an e-mail in your own mail app: nothing is stored here.</p>
<p>What you send in a brief (name, e-mail, phone if given, website, project details, references, delivered by e-mail through the FormSubmit form service) is used only to reply and quote, on the basis of your pre-contract request (GDPR art. 6.1.b), kept three years after last contact if no project follows. Hosting: Vercel Inc. (USA), which processes technical connection logs; fonts and videos are self-hosted, so no third party is contacted during your visit; e-mail is hosted by IONOS. You can ask for access, correction or deletion at any time; you may also contact the CNIL (France) or, for Hong Kong clients, the PCPD under the Personal Data (Privacy) Ordinance.</p>
</main>
<script>(function(){var b=document.getElementById('resetConsent'),m=document.getElementById('resetMsg');if(!b)return;b.addEventListener('click',function(){try{localStorage.removeItem('a8-consent');}catch(e){}document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(/^_ga/.test(n))['','.atelier8.io','atelier8.io'].forEach(function(dm){document.cookie=n+'=; Max-Age=0; path=/'+(dm?'; domain='+dm:'');});});m.textContent='Choix effacé : le bandeau réapparaîtra sur le site.';});})();</script>
</body></html>
"""

NOTFOUND = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page introuvable · Atelier 8</title><meta name="robots" content="noindex">
<link rel="icon" type="image/png" sizes="32x32" href="/media/favicon-32.png">
<style>@font-face{font-family:'Jost';font-weight:300;font-display:swap;src:url(/media/fonts/jost-300.woff2) format('woff2')}@font-face{font-family:'Jost';font-weight:400;font-display:swap;src:url(/media/fonts/jost-400.woff2) format('woff2')}@font-face{font-family:'JetBrains Mono';font-weight:400;font-display:swap;src:url(/media/fonts/jbmono-400.woff2) format('woff2')}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#090908;color:#EFEDE6;font:17px/1.6 'Jost','Helvetica Neue',Arial,sans-serif;text-align:center}
h1{font-weight:300;font-size:clamp(40px,9vw,96px);margin:0;letter-spacing:.02em}p{color:rgba(239,237,230,.6)}a{color:#C99B45;text-decoration:none;letter-spacing:.16em;text-transform:uppercase;font-size:12px;font-family:'JetBrains Mono',ui-monospace,monospace}</style></head>
<body><div><h1>八</h1><p>Cette page n’existe pas. This page does not exist.</p><p><a href="/">Atelier 8 →</a> &nbsp; <a href="/films/">Films</a> &nbsp; <a href="/formats/">Formats</a> &nbsp; <a href="/brief/">Brief</a></p></div></body></html>
"""


def build(full, out):
    """full : page unique complète (chemins relatifs). Écrit tout l'arbre dans out/."""
    full = absolutize(full.replace('@@SEO@@', seo_titles()))
    F, Q = films(full), faqs(full)
    for lang in ('fr', 'en'):
        for v in VIEWS:
            d = os.path.join(out, *(['en'] if lang == 'en' else []), *([] if v == 'accueil' else [v]))
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page(full, lang, v, F, Q))
    w = lambda n, c: (os.makedirs(os.path.dirname(os.path.join(out, n)), exist_ok=True), open(os.path.join(out, n), 'w', encoding='utf-8').write(c))
    w('robots.txt', robots()); w('sitemap.xml', sitemap(F)); w('llms.txt', llms(F, Q))
    w('confidentialite/index.html', PRIVACY); w('404.html', NOTFOUND)
    return F, Q
