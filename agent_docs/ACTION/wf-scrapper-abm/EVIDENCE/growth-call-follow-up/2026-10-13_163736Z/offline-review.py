from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
import json,hashlib,os
from bs4 import BeautifulSoup
from recon_pipeline.collector import load,valid_result
root=Path('/home/moose/PYTHON/stark-web-factory-scrapper-v1');os.chdir(root)
cpath=Path('/tmp/webfactory_growth_context.json');c=json.loads(cpath.read_bytes());e=Path(c['evidence']);initial=Path(c['prepared']);out=Path(str(initial)+'-reviewed');assert not out.exists();out.mkdir()
collection=Path(c['collection']);state=load(collection);item=state['items'][0];meta=valid_result(collection,item);assert meta
index=json.loads((initial/'SOURCE_INDEX.json').read_bytes());page=index['pages'][0];html=BeautifulSoup(Path(page['source']['raw_file']).read_bytes().decode('utf-8'),'html.parser');main=html.select(page['extraction']['css_selector'])[0]
frame=next(x for x in main.select('iframe[src]') if '/widget/booking/' in x['src']);widget=frame['src']
assert not main.get_text(' ',strip=True) and len(html.select('form'))==0 and len(html.select('label'))==0
observed={'source_id':item['id'],'source_file':page['source']['raw_file'],'source_sha256':meta['sha256'],'source_saved_at':meta['saved_at'],'page_title':page['title'],'body_classes':html.body.get('class',[]),'locator':page['extraction']['css_selector'],'body_headings':[],'main_paragraphs':0,'main_list_items':0,'main_links':0,'parent_document_forms':0,'parent_document_labels':0,'visible_form_labels_available':False,'field_gap':'No form labels in parent DOM; child booking document not archived by this capture','booking_iframe':{'source_url':widget,'locator':page['extraction']['css_selector']+' iframe[src="'+widget+'"]','style':frame.get('style'),'title_attribute':frame.get('title'),'inner_body_saved':False},'iframed_content':'Iframe declaration is preserved; child DOM, slot availability, labels and booking functionality are unverified','form_interactions':0,'booking_attempts':0,'new_planned_calls':1,'additional_traffic':'Ordinary browser subresources and frame navigations; not additional selected-page calls'}
# Do not copy values, hidden fields, private headers, or credential-like query parameters.
def sanitized(address):
 p=urlsplit(address);return urlunsplit((p.scheme,p.netloc,p.path,urlencode([(k,'[redacted]' if k.casefold() in ('key','token','api_key','secret','auth','password') else v) for k,v in parse_qsl(p.query)]),''))
observed['other_iframes']=[{'source_url_sanitized':sanitized(n.get('src','')),'title':n.get('title'),'not_collected_separately':True} for n in html.select('iframe') if n is not frame]
(out/'EMBEDS_AND_FORM_LABELS.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2)+'\n')
(e/'page-observations.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2)+'\n')
name='pages/'+item['id']+'.md';(out/'pages').mkdir()
prepared=f'''# Growth Call — saved parent-page evidence

This is an **agent-authored presentation of saved source facts**. The saved main subtree contains an iframe and no standalone heading, paragraph or list text; the headings below are presentation labels, not invented webpage copy.

- Original URL: <{c['target']}>
- Document title from `<title>`: **{page['title']}**
- Capture saved (UTC): {meta['saved_at']}
- Source ID: `{item['id']}`
- Extraction location: `{page['extraction']['css_selector']}`

## Main text from the saved source

<!-- MAIN CONTENT -->
<!-- END MAIN CONTENT -->

No inline body text was returned by the extraction. The unmodified initial converter output is preserved in the earlier derived directory; it is not meaningful offer copy.

## Embedded consultation destination

The parent declares a booking iframe:

[{widget}]({widget})

The saved iframe style declares `display: block`, `visibility: visible`, `opacity: 1`, width100% and height785px. This is evidence of intended display in the parent DOM, not proof of the inner UI's completeness or viewport appearance. The iframe has no saved title attribute.

## Form and CTA evidence

No `<form>` elements or `<label>` elements are present in the captured parent document. Booking-widget field labels, choices, duration, prices, available slots and submit-button copy are **unavailable in this parent snapshot**. They must not be invented. There is no standalone main-content link/button CTA: the iframe itself is the observed destination mechanism.

No form was filled, submitted or booked. Parent capture succeeded; child booking content remains unarchived. Image and hidden/deferred-content completeness are unverified.
'''
(out/name).write_text(prepared.replace('width100%','width 100%').replace('height785px','height 785px'))
(out/'BOILERPLATE.md').write_bytes((initial/'BOILERPLATE.md').read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
page['document_type']='consultation/booking page with embedded widget'
page['classification_basis']='Body has WordPress page classes (page-id-8331); title describes a digital growth strategy call; main subtree contains a booking iframe. The helper initial article heuristic is not the observed content type.'
page['prepared']={'file':str(out/name),'sha256':sha(out/name),'presentation':'agent-authored source-fact annotations; native main text empty'}
page['extraction']['main_text_empty']=True;page['gaps']=['booking iframe child DOM not archived','visible field labels unavailable in parent snapshot','offer details and booking function untested']
index['pages']=[page];index['scope']='One explicitly selected follow-up HTML parent page; embedded booking content remains unavailable; not whole-site assessment'
index['boilerplate']={'file':str(out/'BOILERPLATE.md'),'sha256':sha(out/'BOILERPLATE.md')}
index['agent_authored']=[];index['supporting_evidence']=[{'file':str(out/'EMBEDS_AND_FORM_LABELS.json'),'sha256':sha(out/'EMBEDS_AND_FORM_LABELS.json')},{'file':str(e/'collect.log'),'sha256':sha(e/'collect.log')}]
index['preparation_outcome']='Parent-page evidence prepared; booking form/content coverage PARTIAL / UNKNOWN'
index['initial_extraction']={'directory':str(initial),'finding':'Initial helper type heuristic labels this page article and Markdown contains an empty code marker; preserved. No helper or baseline edits.'}
index['images_completeness']='UNVERIFIED; parent snapshot does not archive child images/resources'
brief=f'''# Architect follow-up — Growth Call

**Observed result:** one approved HTML page was captured successfully and prepared offline. The page reaches a **separate embedded booking widget**. Its parent HTML does not expose the widget's field labels or detailed offer text. This is a useful destination finding with incomplete booking-content coverage; no booking/form QA was performed.

## Source facts

- Requested/final URL: <{c['target']}>; HTTP{meta['status']}; saved{meta['bytes']:,}rendered-HTML bytes at {meta['saved_at']}.
- Document title: **{page['title']}**. This identifies a digital growth strategy call. The parent contains **no separate on-page headings, paragraph copy, native CTA links, forms or labels**. Do not transfer duration/price/guarantees from an assumption or title alone.
- Body classes identify a WordPress page (`page`, `page-id-8331`). It is a booking/consultation destination, not an editorial article despite the initial helper heuristic.
- The iframe source is [{widget}]({widget}), under `{page['extraction']['css_selector']}`. Its inline style declares visible/block display, full width and785pxheight. That does not prove the embedded form loaded completely or its fields were visible in a particular viewport.
- The captured parent document does not contain the **child iframe's DOM**. No visible field labels, submit-button wording, calendar slots, duration or booking availability can be reported from this saved evidence. No iframe label/title attribute was present either.
- Other parent iframe declarations include a tag-manager fallback and map embed; details are recorded in [EMBEDS_AND_FORM_LABELS.json](EMBEDS_AND_FORM_LABELS.json) with credential-like query values redacted. Those resources were not explicitly selected or separately harvested.

See [prepared page]({name}) and [SOURCE_INDEX.json](SOURCE_INDEX.json) for raw/metadata hashes, save time and exact extraction/iframe locations. Navigation/footer output is separate in [BOILERPLATE.md](BOILERPLATE.md); no meaningful repeated navigation/footer text was found in this page snapshot.

## Agent interpretation — implications for JARVIS

- The consultation CTA handoff leads to an embedded booking service, rather than an inline WordPress form. Treat **parent destination** and **embedded booking experience** as separate content/functionality boundaries.
- The document title supports “digital growth strategy call” as an observed offering label. Exact service promise, cost, duration and required visitor inputs remain unknown. Ask for evidence rather than inventing them.
- If the architect requires the actual fields or booking offer, a separately authorized widget-specific capture or owner-provided form specification is needed. This follow-up does not itself approve another host/page or booking interaction.
- The existing parent-HTML collector preserves iframe declarations but not nested document bodies. The limitation is visible in this result; it is not a reason to repeat the same page automatically or reopen the legacy controller.

## Collection versus preparation/coverage

One planned collection call completed, exit0, original stopnull, no reported cleanup error. Prepare ran offline, exit0. The parent result is hash-valid. **Useful preparation is partial for inner booking content:** only the title, iframe declaration/style and explicit absences are established.

`--gap 5` was retained. With one planned call there is no completion-to-next-call interval to measure. Ordinary page/frame resources were additional browser traffic. No links were clicked, inputs filled, forms submitted, booking attempted, REST collected or media harvested. Images/hidden content remain unverified; this is one follow-up, not independent QA certification.

## Baseline status

Per Tony's current instruction, JARVIS accepted Prepare v0.1 for Home, Agency Services and Andromeda. That baseline, its three captures and prepared output remain unchanged. This follow-up adds separately saved evidence and does not reissue a baseline assessment. See [GAPS_AND_REQUESTS.md](GAPS_AND_REQUESTS.md) for the precise remaining questions; no further requests are executed.
'''
for a,b in {'HTTP200':'HTTP 200','saved298,221rendered':'saved 298,221 rendered','and785pxheight':'and 785 px height','exit0':'exit 0','stopnull':'stop reason null'}.items():brief=brief.replace(a,b)
# General spacing for the actual byte value.
brief=brief.replace(f'saved{meta["bytes"]:,}rendered',f'saved {meta["bytes"]:,} rendered')
gaps=f'''# Growth Call — gaps and requests

**No automatic fetching or booking.** The approved scope was one HTML URL and no REST. Parent capture succeeded; the embedded booking content is not archived.

## Missing/unknown evidence

- **Detailed offer:** the source document title says “{page['title']}.” No standalone offer copy, price, duration, conditions or availability is present in the parent main subtree.
- **Visible form labels:** no inline form/label elements exist in the saved parent. Widget field labels and submit CTA are unknown; this does **not** establish that the widget has no form.
- **Embedded content:** the saved DOM declares `{widget}`. Child HTML, calendars and nested resources are not saved here. Aggregate response counts do not establish that this specific frame completed successfully.
- **Functionality:** no form/consent interaction or booking was attempted. Required fields, validation, confirmation, notifications and downstream workflow remain untested.
- **Images/viewport/hidden content:** unverified. Inline iframe style indicates intended visibility only; no screenshot, computed-visibility audit or complete child resource inventory is supplied.
- **Prepare heuristic:** the unchanged helper initially labeled a WordPress page article and converted an empty subtree to a code marker. Agent review corrected the derived classification and made the iframe/absence evidence explicit, preserving the initial output. A future scoped enhancement could record iframe declarations directly; none is implemented now.

## Specific architect/owner requests

1. **Ask Tony/content owner for the booking offer and form specification**: title, duration, cost/free terms, required/optional field labels and confirmation copy. Reason: these details are missing from the parent snapshot and are needed for architect input.
2. **If live widget evidence is needed, request a separately bounded authorization for the exact observed widget URL** `{widget}`. Reason: it is the destination that may contain labels/calendar UI. It is a different host/document and is **not authorized by this one-page task**. Decide whether owner-provided evidence is sufficient first; do not fetch it automatically.
3. **Ask JARVIS whether nested-document capture is required for future Prepare work.** Reason: the current tools archive parent HTML, not iframe bodies. Any collector/skill change needs its own narrow scope; no legacy controller work is implied.

The accepted three-page baseline remains intact. No extra HTML selection, REST items, media downloads, form submission, external messages or further live attempt follows this handoff.
'''
for filename,text in [('ARCHITECT_BRIEF.md',brief),('GAPS_AND_REQUESTS.md',gaps)]:
 p=out/filename;p.write_text(text);index['agent_authored'].append({'file':str(p),'sha256':sha(p),'author':'Cody, Engineer','basis':'saved parent-source facts and labeled agent interpretation'})
(out/'SOURCE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
c['initial_prepared']=str(initial);c['prepared']=str(out);cpath.write_text(json.dumps(c))
print(json.dumps({'prepared':str(out),'booking_source':widget,'parent_forms':0,'parent_labels':0,'headings':0,'main_text_empty':True,'preparation_coverage':'inner booking content PARTIAL / UNKNOWN'},indent=2))
