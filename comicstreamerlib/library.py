"""Encapsulates all data acces code to maintain the comic library"""
import dateutil
import os

from sqlalchemy import func, distinct
from sqlalchemy.orm import subqueryload

import comicstreamerlib.utils as utils
from comicstreamerlib.database import Comic, DatabaseInfo, Person, Role, Credit, Character, GenericTag, Team, Location, \
    StoryArc, Genre
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

    def getComicPage(self, comic_id, page_number, max_height = None):
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

        # resize image
        if max_height is not None:
            try:
                image_data = utils.resizeImage(int(max_height), image_data)
            except Exception as e:
                #logging.error(e)
                pass
        return image_data

    def getStats(self):
        stats = {}
        session = self.getSession()
        stats['total'] = session.query(Comic).count()

        dbinfo = session.query(DatabaseInfo).first()
        stats['uuid'] = dbinfo.uuid
        stats['last_updated'] = dbinfo.last_updated
        stats['created'] = dbinfo.created

        stats['series'] = session.query(func.count(distinct(Comic.series))).scalar()
        stats['persons'] = session.query(Person).count()

        return stats

    def recentlyAddedComics(self, limit = 10):
        return self.getSession().query(Comic)\
                   .order_by(Comic.added_ts.desc())\
                   .limit(limit)

    def recentlyReadComics(self, limit = 10):
        return self.getSession().query(Comic)\
                   .filter(Comic.lastread_ts != "")\
                   .order_by(Comic.lastread_ts.desc())\
                   .limit(limit)

    def getRoles(self):
        return self.getSession().query(Role).all()

    def randomComic(self):
        # SQLite specific random call
        return self.getSession().query(Comic)\
                   .order_by(func.random()).limit(1).first()

    def list(self, criteria={}, paging=None):
        if paging is None:
            paging = {'per_page': 1, 'offset': 10}

        query = self.getSession().query(Comic)

        query = self.processComicQueryArgs(query, criteria)
        query, total_results = self.processPagingArgs(query, paging)
        query = query.options(subqueryload('characters_raw'))
        query = query.options(subqueryload('storyarcs_raw'))
        query = query.options(subqueryload('locations_raw'))
        query = query.options(subqueryload('teams_raw'))
        #query = query.options(subqueryload('credits_raw'))
        query = query.options(subqueryload('generictags_raw'))

        return query.all(), total_results

    def processPagingArgs(self, query, paging):
        per_page = paging.get(u"per_page", None)
        offset = paging.get(u"offset", None)
        # offset and max_results should be processed last

        total_results = None
        if per_page is not None:
            total_results = query.distinct().count()
            try:
                max = 0
                max = int(per_page)
                if total_results > max:
                    query = query.limit(max)
            except:
                pass

        if offset is not None:
            try:
                off = 0
                off = int(offset)
                query = query.offset(off)
            except:
                pass

        return query, total_results

    def processComicQueryArgs(self, query, criteria):
        def hasValue(obj):
            return obj is not None and obj != ""

        keyphrase_filter = criteria.get(u"keyphrase", None)
        series_filter = criteria.get(u"series", None)
        path_filter = criteria.get(u"path", None)
        folder_filter = criteria.get(u"folder", "")
        title_filter = criteria.get(u"title", None)
        start_filter = criteria.get(u"start_date", None)
        end_filter = criteria.get(u"end_date", None)
        added_since = criteria.get(u"added_since", None)
        modified_since = criteria.get(u"modified_since", None)
        lastread_since = criteria.get(u"lastread_since", None)
        order = criteria.get(u"order", None)
        character = criteria.get(u"character", None)
        team = criteria.get(u"team", None)
        location = criteria.get(u"location", None)
        storyarc = criteria.get(u"storyarc", None)
        volume = criteria.get(u"volume", None)
        publisher = criteria.get(u"publisher", None)
        credit_filter = criteria.get(u"credit", None)
        tag = criteria.get(u"tag", None)
        genre = criteria.get(u"genre", None)

        if folder_filter is not None and folder_filter != "":
            folder_filter = os.path.normcase(os.path.normpath(folder_filter))

        person = None
        role = None
        if hasValue(credit_filter):
            credit_info = credit_filter.split(":")
            if len(credit_info[0]) != 0:
                person = credit_info[0]
                if len(credit_info) > 1:
                    role = credit_info[1]

        if hasValue(person):
            query = query.join(Credit)\
                         .filter(Person.name.ilike(person.replace("*", "%"))) \
                         .filter(Credit.person_id == Person.id)
            if role is not None:
                query = query.filter(Credit.role_id == Role.id) \
                             .filter(Role.name.ilike(role.replace("*", "%")))
            #query = query.filter( Comic.persons.contains(unicode(person).replace("*","%") ))

        if hasValue(keyphrase_filter):
            keyphrase_filter = unicode(keyphrase_filter).replace("*", "%")
            keyphrase_filter = "%" + keyphrase_filter + "%"
            query = query.filter( Comic.series.ilike(keyphrase_filter)
                                | Comic.title.ilike(keyphrase_filter)
                                | Comic.publisher.ilike(keyphrase_filter)
                                | Comic.path.ilike(keyphrase_filter)
                                | Comic.comments.ilike(keyphrase_filter)
                                #| Comic.characters_raw.any(Character.name.ilike(keyphrase_filter))
                                #| Comic.teams_raw.any(Team.name.ilike(keyphrase_filter))
                                #| Comic.locations_raw.any(Location.name.ilike(keyphrase_filter))
                                #| Comic.storyarcs_raw.any(StoryArc.name.ilike(keyphrase_filter))
                                | Comic.persons_raw.any(Person.name.ilike(keyphrase_filter))
                            )

        def addQueryOnScalar(query, obj_prop, filt):
            if hasValue(filt):
                filt = unicode(filt).replace("*","%")
                return query.filter( obj_prop.ilike(filt))
            else:
                return query

        def addQueryOnList(query, obj_list, list_prop, filt):
            if hasValue(filt):
                filt = unicode(filt).replace("*","%")
                return query.filter( obj_list.any(list_prop.ilike(filt)))
            else:
                return query

        query = addQueryOnScalar(query, Comic.series, series_filter)
        query = addQueryOnScalar(query, Comic.title, title_filter)
        query = addQueryOnScalar(query, Comic.path, path_filter)
        query = addQueryOnScalar(query, Comic.folder, folder_filter)
        query = addQueryOnScalar(query, Comic.publisher, publisher)
        query = addQueryOnList(query, Comic.characters_raw, Character.name, character)
        query = addQueryOnList(query, Comic.generictags_raw, GenericTag.name, tag)
        query = addQueryOnList(query, Comic.teams_raw, Team.name, team)
        query = addQueryOnList(query, Comic.locations_raw, Location.name, location)
        query = addQueryOnList(query, Comic.storyarcs_raw, StoryArc.name, storyarc)
        query = addQueryOnList(query, Comic.genres_raw, Genre.name, genre)

        if hasValue(volume):
            try:
                vol = 0
                vol = int(volume)
                query = query.filter(Comic.volume == vol)
            except:
                pass

        if hasValue(start_filter):
            try:
                dt = dateutil.parser.parse(start_filter)
                query = query.filter(Comic.date >= dt)
            except:
                pass

        if hasValue(end_filter):
            try:
                dt = dateutil.parser.parse(end_filter)
                query = query.filter(Comic.date <= dt)
            except:
                pass

        if hasValue(modified_since):
            try:
                dt = dateutil.parser.parse(modified_since)
                query = query.filter(Comic.mod_ts >= dt)
            except:
                pass

        if hasValue(added_since):
            try:
                dt = dateutil.parser.parse(added_since)
                query = query.filter(Comic.added_ts >= dt)
            except:
                pass

        if hasValue(lastread_since):
            try:
                dt = dateutil.parser.parse(lastread_since)
                query = query.filter(Comic.lastread_ts >= dt, Comic.lastread_ts != "")
            except:
                pass

        order_key = None
        # ATB temp hack to cover "slicing" bug where
        # if no order specified, the child collections
        # get chopped off sometimes
        if not hasValue(order):
            order = "id"

        if hasValue(order):
            if order[0] == "-":
                order_desc = True
                order = order[1:]
            else:
                order_desc = False
            if order == "id":
                order_key = Comic.id
            if order == "series":
                order_key = Comic.series
            elif order == "modified":
                order_key = Comic.mod_ts
            elif order == "added":
                order_key = Comic.added_ts
            elif order == "lastread":
                order_key = Comic.lastread_ts
            elif order == "volume":
                order_key = Comic.volume
            elif order == "issue":
                order_key = Comic.issue_num
            elif order == "date":
                order_key = Comic.date
            elif order == "publisher":
                order_key = Comic.publisher
            elif order == "title":
                order_key = Comic.title
            elif order == "path":
                order_key = Comic.path

        if order_key is not None:
            if order_desc:
                order_key = order_key.desc()
            query = query.order_by(order_key)

        return query

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