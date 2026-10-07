# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `36c12e96bc28e74f926d199ea51fc518e24b3dc75a5213559d386fcba748d4eb`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- post: advertised 2 records / 1 pages; enumerated 1 unique; status partial; gaps \['advertised\_count\_mismatch', 'duplicate\_ids'\].

## Candidates

1. **\[title unknown\]** — `doc-1cdb8c7ffd0c2646b288` — document
   - URL: http://127.0.0.1:9888/a
   - Content type: unknown; dates: {'sitemap\_lastmod': '2026-10-01'}
   - Source evidence: evidence/0001.body XML loc\[0\]; evidence/0001.body XML loc\[1\]
   - REST item scope: not established
   - Gaps: content\_type\_unknown, title\_unknown.
2. **Article 1** — `doc-31950248dda8b8a77892` — document
   - URL: http://127.0.0.1:9888/article-1
   - Content type: unknown; dates: {'date': '2026-10-07T00:00:00'}
   - Source evidence: evidence/0003.body $\[0\]; evidence/0003.body $\[1\]
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/posts/1'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
3. **\[title unknown\]** — `doc-44758ca80440b39a5f01` — document
   - URL: http://127.0.0.1:9888/b
   - Content type: unknown; dates: unknown
   - Source evidence: evidence/0001.body XML loc\[2\]
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
4. **REST collection: Posts** — `rest-dc5aa2127387494cbe21` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/posts
   - Content type: unknown; dates: unknown
   - Source evidence: evidence/0002.body types.post
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
