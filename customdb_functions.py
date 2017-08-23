# -*- coding: utf-8 -*-

#################################################################################################

import logging
from sqlite3 import OperationalError

##################################################################################################

log = logging.getLogger("LD."+__name__)

##################################################################################################


class Customdb_Functions():

    def verify_emby_database(self):
        # Create the tables for the emby database
        # emby, view, version
        self.custom_cursor.execute(
            """CREATE TABLE IF NOT EXISTS source(
            source_id TEXT UNIQUE, media_folder TEXT, source_type TEXT, media_type TEXT,
            kodi_id INTEGER, kodi_fileid INTEGER, kodi_pathid INTEGER, parent_id INTEGER,
            checksum INTEGER)""")
        self.custom_cursor.execute(
            """CREATE TABLE IF NOT EXISTS view(
            view_id TEXT UNIQUE, view_name TEXT, media_type TEXT, kodi_tagid INTEGER)""")
        self.custom_cursor.execute("CREATE TABLE IF NOT EXISTS version(idVersion TEXT)")

    def __init__(self, custom_cursor):

        self.custom_cursor = custom_cursor
        self.verify_emby_database()

    def get_version(self, version=None):

        if version is not None:
            self.custom_cursor.execute("DELETE FROM version")
            query = "INSERT INTO version(idVersion) VALUES (?)"
            self.custom_cursor.execute(query, (version,))
        else:
            query = "SELECT idVersion FROM version"
            self.custom_cursor.execute(query)
            try:
                version = self.custom_cursor.fetchone()[0]
            except TypeError:
                pass

        return version

    def getViews(self):

        views = []

        query = ' '.join((

            "SELECT view_id",
            "FROM view"
        ))
        self.custom_cursor.execute(query)
        rows = self.custom_cursor.fetchall()
        for row in rows:
            views.append(row[0])
        
        return views

    def getView_source_id(self, item_id):
        # Returns ancestors using source_id
        url = "{server}/source/Items/%s/Ancestors?UserId={UserId}&format=json" % item_id

        try:
            view_list = self.download(url)
        except Exception as error:
            log.info("Error getting views: " + str(error))
            view_list = []

        if view_list is None:
            view_list = []

        for view in view_list:

            if view['Type'] == "CollectionFolder":
                # Found view
                view_id = view['Id']
                break
        else: # No view found
            return [None, None]

        # Compare to view table in source database
        query = ' '.join((

            "SELECT view_name",
            "FROM view",
            "WHERE view_id = ?"
        ))
        self.custom_cursor.execute(query, (view_id,))
        try:
            view_name = self.custom_cursor.fetchone()[0]
        except TypeError:
            view_name = None

        return [view_name, view_id]

    def getView_byId(self, viewid):


        query = ' '.join((

            "SELECT view_name, media_type, kodi_tagid",
            "FROM view",
            "WHERE view_id = ?"
        ))
        self.custom_cursor.execute(query, (viewid,))
        view = self.custom_cursor.fetchone()
        
        return view

    def getView_byType(self, mediatype):

        views = []

        query = ' '.join((

            "SELECT view_id, view_name",
            "FROM view",
            "WHERE media_type = ?"
        ))
        self.custom_cursor.execute(query, (mediatype,))
        rows = self.custom_cursor.fetchall()
        for row in rows:
            views.append({

                'id': row[0],
                'name': row[1]
            })

        return views

    def getView_byName(self, tagname):

        query = ' '.join((

            "SELECT view_id",
            "FROM view",
            "WHERE view_name = ?"
        ))
        self.custom_cursor.execute(query, (tagname,))
        try:
            view = self.custom_cursor.fetchone()[0]
        
        except TypeError:
            view = None

        return view

    def addView(self, source_id, name, mediatype, tagid):

        query = (
            '''
            INSERT INTO view(
                view_id, view_name, media_type, kodi_tagid)

            VALUES (?, ?, ?, ?)
            '''
        )
        self.custom_cursor.execute(query, (source_id, name, mediatype, tagid))

    def updateView(self, name, tagid, mediafolderid):

        query = ' '.join((

            "UPDATE view",
            "SET view_name = ?, kodi_tagid = ?",
            "WHERE view_id = ?"
        ))
        self.custom_cursor.execute(query, (name, tagid, mediafolderid))

    def removeView(self, viewid):

        query = ' '.join((

            "DELETE FROM view",
            "WHERE view_id = ?"
        ))
        self.custom_cursor.execute(query, (viewid,))

    def getItem_byId(self, source_id):

        query = ' '.join((

            "SELECT kodi_id, kodi_fileid, kodi_pathid, parent_id, media_type, source_type",
            "FROM source",
            "WHERE source_id = ?"
        ))
        try:
            self.custom_cursor.execute(query, (source_id,))
            item = self.custom_cursor.fetchone()
            return item
        except: return None

    def getItem_byWildId(self, source_id):

        query = ' '.join((

            "SELECT kodi_id, media_type",
            "FROM source",
            "WHERE source_id LIKE ?"
        ))
        self.custom_cursor.execute(query, (source_id+"%",))
        return self.custom_cursor.fetchall()

    def getItem_byView(self, mediafolderid):

        query = ' '.join((

            "SELECT kodi_id",
            "FROM source",
            "WHERE media_folder = ?"
        ))
        self.custom_cursor.execute(query, (mediafolderid,))
        return self.custom_cursor.fetchall()

    def get_item_by_view(self, view_id):

        query = ' '.join((

            "SELECT source_id",
            "FROM source",
            "WHERE media_folder = ?"
        ))
        self.custom_cursor.execute(query, (view_id,))
        return self.custom_cursor.fetchall()

    def getItem_byKodiId(self, kodiid, mediatype):

        query = ' '.join((

            "SELECT source_id, parent_id, media_folder",
            "FROM source",
            "WHERE kodi_id = ?",
            "AND media_type = ?"
        ))
        self.custom_cursor.execute(query, (kodiid, mediatype,))
        return self.custom_cursor.fetchone()

    def getItem_byParentId(self, parentid, mediatype):

        query = ' '.join((

            "SELECT source_id, kodi_id, kodi_fileid",
            "FROM source",
            "WHERE parent_id = ?",
            "AND media_type = ?"
        ))
        self.custom_cursor.execute(query, (parentid, mediatype,))
        return self.custom_cursor.fetchall()

    def getItemId_byParentId(self, parentid, mediatype):

        query = ' '.join((

            "SELECT source_id, kodi_id",
            "FROM source",
            "WHERE parent_id = ?",
            "AND media_type = ?"
        ))
        self.custom_cursor.execute(query, (parentid, mediatype,))
        return self.custom_cursor.fetchall()

    def get_checksum(self, mediatype):

        query = ' '.join((

            "SELECT source_id, checksum",
            "FROM source",
            "WHERE source_type = ?"
        ))
        self.custom_cursor.execute(query, (mediatype,))
        return self.custom_cursor.fetchall()

    def get_checksum_by_view(self, media_type, view_id):

        query = ' '.join((

            "SELECT source_id, checksum",
            "FROM source",
            "WHERE source_type = ?",
            "AND media_folder = ?"
        ))
        self.custom_cursor.execute(query, (media_type, view_id,))
        return self.custom_cursor.fetchall()

    def getMediaType_byId(self, source_id):

        query = ' '.join((

            "SELECT source_type",
            "FROM source",
            "WHERE source_id = ?"
        ))
        self.custom_cursor.execute(query, (source_id,))
        try:
            itemtype = self.custom_cursor.fetchone()[0]
        
        except TypeError:
            itemtype = None

        return itemtype

    def sortby_mediaType(self, itemids, unsorted=True):

        sorted_items = {}
        
        for itemid in itemids:
            
            mediatype = self.getMediaType_byId(itemid)
            if mediatype:
                sorted_items.setdefault(mediatype, []).append(itemid)
            elif unsorted:
                sorted_items.setdefault('Unsorted', []).append(itemid)

        return sorted_items

    def addReference(self, source_id, kodiid, sourcetype, mediatype, fileid=None, pathid=None,
                        parentid=None, checksum=None, mediafolderid=None):
        query = (
            '''
            INSERT OR REPLACE INTO source(
                source_id, kodi_id, kodi_fileid, kodi_pathid, source_type, media_type, parent_id,
                checksum, media_folder)

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        )
        self.custom_cursor.execute(query, (source_id, kodiid, fileid, pathid, sourcetype, mediatype,
            parentid, checksum, mediafolderid))

    def updateReference(self, source_id, checksum):

        query = "UPDATE source SET checksum = ? WHERE source_id = ?"
        self.custom_cursor.execute(query, (checksum, source_id))

    def updateParentId(self, source_id, parent_kodiid):
        
        query = "UPDATE source SET parent_id = ? WHERE source_id = ?"
        self.custom_cursor.execute(query, (parent_kodiid, source_id))

    def removeItems_byParentId(self, parent_kodiid, mediatype):

        query = ' '.join((

            "DELETE FROM source",
            "WHERE parent_id = ?",
            "AND media_type = ?"
        ))
        self.custom_cursor.execute(query, (parent_kodiid, mediatype,))

    def removeItem_byKodiId(self, kodiid, mediatype):

        query = ' '.join((

            "DELETE FROM source",
            "WHERE kodi_id = ?",
            "AND media_type = ?"
        ))
        self.custom_cursor.execute(query, (kodiid, mediatype,))

    def removeItem(self, source_id):

        query = "DELETE FROM source WHERE source_id = ?"
        self.custom_cursor.execute(query, (source_id,))

    def removeWildItem(self, source_id):

        query = "DELETE FROM source WHERE source_id LIKE ?"
        self.custom_cursor.execute(query, (source_id+"%",))
        