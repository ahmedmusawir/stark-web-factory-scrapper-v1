# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `4b40fa90b9a6982395dc2500ea99bd6cc2cb4c2437e5baf57dfeed31d3365d97`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- post: advertised 1 records / 1 pages; enumerated 1 unique; status enumerated\_metadata; gaps \[\].

## Candidates

1. **\[title unknown\]** — `doc-1cdb8c7ffd0c2646b288` — document
   - URL: http://127.0.0.1:9888/a
   - HTTP content type: unknown; WordPress type: unknown; dates: {'sitemap\_lastmod': '2026-10-01'}
   - REST item scope: not established
   - Gaps: content\_type\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[0\]
   - Evidence: evidence/0001.body — XML loc\[1\]
2. **Article 11945** — `doc-d6ffea3485e026353fa6` — document
   - URL: http://127.0.0.1:9888/article-11945
   - HTTP content type: unknown; WordPress type: post; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/posts/11945'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0003.body — $\[0\]
3. **\[title unknown\]** — `doc-44758ca80440b39a5f01` — document
   - URL: http://127.0.0.1:9888/b
   - HTTP content type: unknown; WordPress type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[2\]
4. **REST collection: Posts** — `rest-dc5aa2127387494cbe21` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/posts
   - HTTP content type: unknown; WordPress type: post; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.post
