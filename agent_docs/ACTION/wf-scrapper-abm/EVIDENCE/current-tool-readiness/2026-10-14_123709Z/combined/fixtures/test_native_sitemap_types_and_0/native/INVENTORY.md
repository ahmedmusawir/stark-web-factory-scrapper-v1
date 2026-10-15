# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `190bc1397e431b97fcf071d33eaeae1d68c44154b9d4417ce2e9fe7d13fa2708`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- post: advertised 166 records / 9 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- book: advertised 0 records / 0 pages; enumerated 0 unique; status enumerated\_metadata; gaps \[\].

## Candidates

1. **\[title unknown\]** — `doc-0e90427c4c0676635a3b` — document
   - URL: http://127.0.0.1:40127/a
   - HTTP content type: unknown; WordPress type: unknown; dates: {'sitemap\_lastmod': '2026-10-01'}
   - REST item scope: not established
   - Gaps: content\_type\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[0\]
   - Evidence: evidence/0001.body — XML loc\[1\]
2. **Article 11945** — `doc-2b8c716c120279acbdb9` — document
   - URL: http://127.0.0.1:40127/article-11945
   - HTTP content type: unknown; WordPress type: post; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:40127/wp-json/wp/v2/posts/11945'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0003.body — $\[0\]
3. **\[title unknown\]** — `doc-2c573442a5e66c2a995c` — document
   - URL: http://127.0.0.1:40127/b
   - HTTP content type: unknown; WordPress type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[2\]
4. **REST collection: Books** — `rest-5022270c3ebaeaaf4d0d` — rest_collection
   - URL: http://127.0.0.1:40127/wp-json/wp/v2/books
   - HTTP content type: unknown; WordPress type: book; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.book
5. **REST collection: Posts** — `rest-3884c22c61fe024edc6c` — rest_collection
   - URL: http://127.0.0.1:40127/wp-json/wp/v2/posts
   - HTTP content type: unknown; WordPress type: post; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.post
