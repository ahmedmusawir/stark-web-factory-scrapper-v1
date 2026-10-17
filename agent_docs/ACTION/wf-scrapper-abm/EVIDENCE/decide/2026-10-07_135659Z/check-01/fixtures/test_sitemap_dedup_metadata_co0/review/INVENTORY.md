# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `b8452ae22e81aea45151af51e43e1a878a52f06171bc20cd6a9a3901571173bc`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- page: advertised 9 records / 3 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- post: advertised 4 records / 2 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- book: advertised 1 records / 1 pages; enumerated 1 unique; status enumerated\_metadata; gaps \[\].

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
   - Source evidence: evidence/0003.body $\[0\]
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/pages/1'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
3. **Article 2** — `doc-a120093e7c4ffa02f7d2` — document
   - URL: http://127.0.0.1:9888/article-2
   - Content type: unknown; dates: {'date': '2026-10-07T00:00:00'}
   - Source evidence: evidence/0004.body $\[0\]
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/posts/2'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
4. **Article 3** — `doc-9c10c1545076a6699be2` — document
   - URL: http://127.0.0.1:9888/article-3
   - Content type: unknown; dates: {'date': '2026-10-07T00:00:00'}
   - Source evidence: evidence/0005.body $\[0\]
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/books/3'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
5. **\[title unknown\]** — `doc-44758ca80440b39a5f01` — document
   - URL: http://127.0.0.1:9888/b
   - Content type: unknown; dates: unknown
   - Source evidence: evidence/0001.body XML loc\[2\]
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
6. **REST collection: Books** — `rest-6437f9963992b783c7cf` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/books
   - Content type: unknown; dates: unknown
   - Source evidence: evidence/0002.body types.book
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
7. **REST collection: Pages** — `rest-1d50b3e4f4962e3e4eb0` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/pages
   - Content type: unknown; dates: unknown
   - Source evidence: evidence/0002.body types.page
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
8. **REST collection: Posts** — `rest-dc5aa2127387494cbe21` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/posts
   - Content type: unknown; dates: unknown
   - Source evidence: evidence/0002.body types.post
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
