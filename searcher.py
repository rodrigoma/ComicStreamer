
import sys
from whoosh import index, sorting
from whoosh.qparser import QueryParser

q = sys.argv[1]

print "Searching %s" % q

ix = index.open_dir('/home/davide/.ComicStreamer/whoosh-idx/')
qp = QueryParser('title', ix.schema)

query = qp.parse(q)
with ix.searcher() as s:
    facets = sorting.Facets()
    facets.add_field("authors", allow_overlap=True)
    facets.add_field("characters", allow_overlap=True)

    r = s.search(query, groupedby=facets, maptype=sorting.Count)
    print "Total: %s" % len(r)
    print r.groups('authors')
    print r.groups('characters')