# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `534213ef313c8d4e8000f0f037b843d4b0b84e43144ce00300ae4dfefabeff24`. All choices initially UNDECIDED.

Row numbers refer ONLY to this saved version. HTML and REST require separate choices.
Stop: none; coverage gaps: none recorded; bounded scope only.

## WordPress metadata coverage

- post: advertised 166 records / 9 pages; enumerated 1 unique; status partial; gaps \['metadata\_page\_limit'\].
- book: advertised 0 records / 0 pages; enumerated 0 unique; status enumerated\_metadata; gaps \[\].

## Candidates

1. **\[title unknown\]** — `doc-48d3e943b1aa3c4105db` — document
   - URL: http://127.0.0.1:46779/a
   - Content type: unknown; dates: {'sitemap\_lastmod': '2026-10-01'}
   - REST item scope: not established
   - Gaps: content\_type\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[0\]
   - Evidence: evidence/0001.body — XML loc\[1\]
2. **Article 11945** — `doc-1ea2b8d54196c0aa2c78` — document
   - URL: http://127.0.0.1:46779/article-11945
   - Content type: unknown; dates: {'date': '2026-10-07T00:00:00'}
   - REST item scope: \['http://127.0.0.1:46779/wp-json/wp/v2/posts/11945'\]
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown.
   - Evidence: evidence/0003.body — $\[0\]
3. **\[title unknown\]** — `doc-fa37fdbd6dab7e7bc01f` — document
   - URL: http://127.0.0.1:46779/b
   - Content type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown, title\_unknown.
   - Evidence: evidence/0001.body — XML loc\[2\]
4. **REST collection: Books** — `rest-bec86c65068e1d5ec2ba` — rest_collection
   - URL: http://127.0.0.1:46779/wp-json/wp/v2/books
   - Content type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.book
5. **REST collection: Posts** — `rest-6e00e09a34ea5a001aca` — rest_collection
   - URL: http://127.0.0.1:46779/wp-json/wp/v2/posts
   - Content type: unknown; dates: unknown
   - REST item scope: not established
   - Gaps: content\_type\_unknown, dates\_unknown.
   - Evidence: evidence/0002.body — types.post
