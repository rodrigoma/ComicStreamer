import os
import re

from whoosh import index
from whoosh.fields import *
from comicstreamerlib.folders import AppFolders
from comicstreamerlib.database import DataManager, Comic

schema = Schema(
    id=ID(stored=True, unique=True),
    title=TEXT,
    authors=KEYWORD(stored=True, commas=True, lowercase=True),
    characters=KEYWORD(stored=True, commas=True, lowercase=True))

ix_dir = os.path.join(AppFolders.appData(), "whoosh-idx")
if not os.path.exists(ix_dir):
    os.makedirs(ix_dir)

if not index.exists_in(os.path.join(ix_dir)):
    ix = index.create_in(ix_dir, schema)
    print "Creating index in %s" % ix_dir
else:
    ix = index.open_dir(ix_dir)
    print "Opening index in %s" % ix_dir


dm = DataManager()
s = dm.Session()
writer = ix.writer()
for comic in s.query(Comic).all():
    ch_list = ",".join([re.sub(r'\s+', '_', c) for c in comic.characters]) or unicode("")
    person_list = ",".join([re.sub(r'\s+', '_', a) for a in comic.persons]) or unicode("")
    print "Adding comic id [%s] (%s) (%s)" % (comic.id, ch_list, person_list)
    writer.update_document(
        id=unicode(comic.id),
        title=comic.title,
        characters=ch_list,
        authors=person_list)

writer.commit()