# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `8806a47a06e2dc926c68ff047b82492d44eb4865bca13a5accea70a93583e57f`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- page: advertised 9 records / 3 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- post: advertised 4 records / 2 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- book: advertised 1 records / 1 pages; enumerated 1 unique; status enumerated\_metadata; gaps \[\].

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
   - HTTP content type: unknown; WordPress type: page; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/pages/1'\]
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
   - HTTP content type: unknown; WordPress type: book; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:9888/wp-json/wp/v2/books/3'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0005.body — $\[0\]
5. **\[title unknown\]** — `doc-44758ca80440b39a5f01` — document
   - URL: http://127.0.0.1:9888/b
   - HTTP content type: unknown; WordPress type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[2\]
6. **REST collection: Books** — `rest-6437f9963992b783c7cf` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/books
   - HTTP content type: unknown; WordPress type: book; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.book
7. **REST collection: Pages** — `rest-1d50b3e4f4962e3e4eb0` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/pages
   - HTTP content type: unknown; WordPress type: page; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.page
8. **REST collection: Posts** — `rest-dc5aa2127387494cbe21` — rest_collection
   - URL: http://127.0.0.1:9888/wp-json/wp/v2/posts
   - HTTP content type: unknown; WordPress type: post; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.post
