# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `cfd0b731313915a3a98ba6ac5c809917043c5d1f98b11a34ddfab5f6ece999ba`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- post: advertised 3 records / 2 pages; enumerated 3 unique; status enumerated\_metadata; gaps \[\].

## Candidates

1. **\[title unknown\]** — `doc-1cdb8c7ffd0c2646b288` — document
   - URL: http://127.0.0.1:9888/a
   - HTTP content type: unknown; WordPress type: unknown; dates: {'sitemap\_lastmod': '2026-10-01'}
   - REST item scope: not established
   - Gaps: content\_type\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[0\]
   - Evidence: evidence/0001.body — XML loc\[1\]
2. **Article 1** — `doc-31950248dda8b8a77892` — document
   - URL: http://127.0.0.1:9888/article-1
   - HTTP content type: unknown; WordPress type: post; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/posts/1'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0003.body — $\[0\]
3. **Article 2** — `doc-a120093e7c4ffa02f7d2` — document
   - URL: http://127.0.0.1:9888/article-2
   - HTTP content type: unknown; WordPress type: post; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/posts/2'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0004.body — $\[0\]
4. **Article 3** — `doc-9c10c1545076a6699be2` — document
   - URL: http://127.0.0.1:9888/article-3
   - HTTP content type: unknown; WordPress type: post; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/posts/3'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0004.body — $\[1\]
5. **\[title unknown\]** — `doc-44758ca80440b39a5f01` — document
   - URL: http://127.0.0.1:9888/b
   - HTTP content type: unknown; WordPress type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[2\]
6. **REST collection: Posts** — `rest-dc5aa2127387494cbe21` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/posts
   - HTTP content type: unknown; WordPress type: post; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.post
