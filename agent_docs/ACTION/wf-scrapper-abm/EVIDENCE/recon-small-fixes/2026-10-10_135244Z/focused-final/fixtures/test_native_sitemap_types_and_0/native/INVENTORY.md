# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `e61084ab5268551ab1b1ecf3898ad341bddd9e7f547fd8f9bd80860211238e26`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- post: advertised 166 records / 9 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- book: advertised 0 records / 0 pages; enumerated 0 unique; status enumerated\_metadata; gaps \[\].

## Candidates

1. **\[title unknown\]** — `doc-017ca5031ae71d653f23` — document
   - URL: http://127.0.0.1:39857/a
   - HTTP content type: unknown; WordPress type: unknown; dates: {'sitemap\_lastmod': '2026-10-01'}
   - REST item scope: not established
   - Gaps: content\_type\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[0\]
   - Evidence: evidence/0001.body — XML loc\[1\]
2. **Article 11945** — `doc-ce0625f8ee2f7e535fc0` — document
   - URL: http://127.0.0.1:39857/article-11945
   - HTTP content type: unknown; WordPress type: post; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:39857/wp-json/wp/v2/posts/11945'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0003.body — $\[0\]
3. **\[title unknown\]** — `doc-554375c138acf02e124c` — document
   - URL: http://127.0.0.1:39857/b
   - HTTP content type: unknown; WordPress type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[2\]
4. **REST collection: Books** — `rest-b617fbdcb2da66ffb206` — rest_collection
   - URL: http://127.0.0.1:39857/wp-json/wp/v2/books
   - HTTP content type: unknown; WordPress type: book; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.book
5. **REST collection: Posts** — `rest-4e5f679df1b42f256b9c` — rest_collection
   - URL: http://127.0.0.1:39857/wp-json/wp/v2/posts
   - HTTP content type: unknown; WordPress type: post; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.post
