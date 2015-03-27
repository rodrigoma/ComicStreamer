"""Encapsulates all data acces code to maintain the comic library"""
from comicstreamerlib.database import Comic


class Library:

    def __init__(self, session_getter):
        self.getSession = session_getter

    def getSession(self):
        """SQLAlchemy session"""
        pass

    def getComicThumbnail(self, comic_id):
        """Fast access to a comic thumbnail"""
        return self.getSession().query(Comic.thumbnail) \
                   .filter(Comic.id == int(comic_id)).scalar()

    def getComic(self, comic_id):
        return self.getSession().query(Comic).get(int(comic_id))

