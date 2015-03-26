"""Encapsulates all data acces code to maintain the comic library"""
from comicstreamerlib.database import Comic


class Library:

    def __init__(self, session_getter):
        self.get_session = session_getter

    def get_session(self):
        """SQLAlchemy session"""
        pass

    def get_comic_thumbnail(self, comic_id):
        """Fast access to a comic thumbnail"""
        return self.get_session().query(Comic.thumbnail) \
                    .filter(Comic.id == int(comic_id)).scalar()

    def get_comic(self, comic_id):
        return self.get_session().query(Comic).get(int(comic_id))