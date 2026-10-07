# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `f495f9db89a145c5328734c014e567bf7706897dd8af29799b9669a750c0dc8e`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- post: advertised 166 records / 9 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- book: advertised 0 records / 0 pages; enumerated 0 unique; status enumerated\_metadata; gaps \[\].

## Candidates

1. **\[title unknown\]** — `doc-6495321a294d167e025b` — document
   - URL: http://127.0.0.1:43467/a
   - HTTP content type: unknown; WordPress type: unknown; dates: {'sitemap\_lastmod': '2026-10-01'}
   - REST item scope: not established
   - Gaps: content\_type\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[0\]
   - Evidence: evidence/0001.body — XML loc\[1\]
2. **Article 11945** — `doc-6722590fd0d94a757cf6` — document
   - URL: http://127.0.0.1:43467/article-11945
   - HTTP content type: unknown; WordPress type: post; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:43467/wp-json/wp/v2/posts/11945'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0003.body — $\[0\]
3. **\[title unknown\]** — `doc-9e0edb4557080f440e60` — document
   - URL: http://127.0.0.1:43467/b
   - HTTP content type: unknown; WordPress type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[2\]
4. **REST collection: Books** — `rest-39453ad8f8e363a252d0` — rest_collection
   - URL: http://127.0.0.1:43467/wp-json/wp/v2/books
   - HTTP content type: unknown; WordPress type: book; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.book
5. **REST collection: Posts** — `rest-704316ff9803f0f57347` — rest_collection
   - URL: http://127.0.0.1:43467/wp-json/wp/v2/posts
   - HTTP content type: unknown; WordPress type: post; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.post
