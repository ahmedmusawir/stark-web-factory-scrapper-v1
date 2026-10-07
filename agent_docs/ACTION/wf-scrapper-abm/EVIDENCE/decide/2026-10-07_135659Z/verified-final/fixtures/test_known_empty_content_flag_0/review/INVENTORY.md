# DECIDE — numbered review inventory

**FRESH_BOUNDED_RECON**; mode `sitemap`.
Version: `1598b94ac8ba7df3475cd949be15d580d3cacc114ae9cccb3f65fbcd07760e4a`. All choices initially UNDECIDED.

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
   - Gaps: content\_not\_requested\_in\_recon, content\_type\_unknown, historical\_rest\_content\_rendered\_empty, needs\_HTML\_review\_if\_selected.
   - Evidence: evidence/0003.body — $\[0\]
   - Evidence: /home/moose/PYTHON/stark-web-factory-scrapper-v1/agent\_docs/ACTION/wf-scrapper-abm/EVIDENCE/decide/2026-10-07\_135659Z/verified-final/fixtures/test\_known\_empty\_content\_flag\_0/saved/attempts/8a7e187d7e566318c43bbb40/4341ab64550a408290d1836ed96bb2e9/body — historical REST content.rendered
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
