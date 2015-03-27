"""Encapsulates all data acces code to maintain the comic library"""
from comicstreamerlib.database import Comic
from comicstreamerlib.folders import AppFolders
from comicapi.comicarchive import ComicArchive

class Library:

    def __init__(self, session_getter):
        self.getSession = session_getter
        self.comicArchiveList = []

    def getSession(self):
        """SQLAlchemy session"""
        pass

    def getComicThumbnail(self, comic_id):
        """Fast access to a comic thumbnail"""
        return self.getSession().query(Comic.thumbnail) \
                   .filter(Comic.id == int(comic_id)).scalar()

    def getComic(self, comic_id):
        return self.getSession().query(Comic).get(int(comic_id))

    def getComicPage(self, comic_id, page_number):
        (path, page_count) = self.getSession().query(Comic.path, Comic.page_count) \
                                 .filter(Comic.id == int(comic_id)).first()

        image_data = None
        default_img_file = AppFolders.imagePath("default.jpg")

        if path is not None:
            if int(page_number) < page_count:
                ca = self.getComicArchive(path)
                image_data = ca.getPage(int(page_number))

        if image_data is None:
            with open(default_img_file, 'rb') as fd:
                image_data = fd.read()

        return image_data

    def getComicArchive(self, path):
        # should also look at modified time of file
        for ca in self.comicArchiveList:
            if ca.path == path:
                # remove from list and put at end
                self.comicArchiveList.remove(ca)
                self.comicArchiveList.append(ca)
                return ca
        else:
            ca = ComicArchive(path, default_image_path=AppFolders.imagePath("default.jpg"))
            self.comicArchiveList.append(ca)
            if len(self.comicArchiveList) > 10:
                self.comicArchiveList.pop(0)
            return ca