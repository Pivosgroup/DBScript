# -*- coding: utf-8 -*-

##################################################################################################
import logging
import _kodi_movies
from customdb_functions import Customdb_Functions

##################################################################################################
log = logging.getLogger("LD." + __name__)
##################################################################################################


class Movies():

    def __init__(self, kodicursor, sources_cursor, pdialog=None):

        self.kodicursor = kodicursor
        self.kodi_db = _kodi_movies.KodiMovies(self.kodicursor)
        self.sources_cursor = sources_cursor
        self.source_db = Customdb_Functions(self.sources_cursor)
        self.kodi_version = 17

    def _get_func(self, item_type, action):

        if item_type == "Movie":
            actions = {
                'added': self.add_movies,
                'update': self.add_update,
                'userdata': self.updateUserdata,
                'remove': self.remove
            }
        elif item_type == "BoxSet":
            actions = {
                'added': self.add_boxsets,
                'update': self.add_updateBoxset,
                'remove': self.remove
            }
        else:
            log.info("Unsupported item_type: %s", item_type)
            actions = {}

        return actions.get(action)

    def compare_all(self):
        # Pull the list of movies and boxsets in Kodi
        views = self.emby_db.getView_byType('movies')
        views += self.emby_db.getView_byType('mixed')
        log.info("Media folders: %s", views)

        # Process movies
        for view in views:

            if self.should_stop():
                return False

            if not self.compare_movies(view):
                return False

        # Process boxsets
        if not self.compare_boxsets():
            return False

        return True

    def compare_movies(self, view):

        view_id = view['id']
        view_name = view['name']

        if self.pdialog:
            self.pdialog.update(heading=lang(
                29999), message="%s %s..." % (lang(33026), view_name))

        movies = dict(self.emby_db.get_checksum_by_view("Movie", view_id))
        emby_movies = self.emby.getMovies(
            view_id, basic=True, dialog=self.pdialog)

        return self.compare("Movie", emby_movies['Items'], movies, view)

    def compare_boxsets(self):

        if self.pdialog:
            self.pdialog.update(heading=lang(29999), message=lang(33027))

        boxsets = dict(self.emby_db.get_checksum('BoxSet'))
        emby_boxsets = self.emby.getBoxset(dialog=self.pdialog)

        return self.compare("BoxSet", emby_boxsets['Items'], boxsets)

    def add_movies(self, items, total=None, view=None):

        for item in self.added(items, total):
            if self.add_update(item, view):
                self.content_pop(item.get('Name', "unknown"))

    def add_boxsets(self, items, total=None):

        for item in self.added(items, total):
            self.add_updateBoxset(item)

    def add_update(self, item, view=None):

        # If the item already exist in the local Kodi DB we'll perform a full item update
        # If the item doesn't exist, we'll add it to the database
        update_item = True
        title = item['title']
        itemid = item['source_id']
        source_type = item['source_type']
        source_item = self.source_db.getItem_byId(itemid)
        try:
            movieid = source_item[0]
            fileid = source_item[1]
            pathid = source_item[2]
        except TypeError:
            update_item = False
            movieid = self.kodi_db.create_entry()
        else:
            if self.kodi_db.get_movie(movieid) is None:
                # item is not found, let's recreate it.
                update_item = False
                log.info("movieid : %s missing from Kodi, repairing the entry", movieid)


        # fileId information
        dateadded = item.get('dateadded')
        # item details
        writer = item.get('writer')
        director = item.get('director')
        directors = director.split(" / ")
        genre = item.get('genre')
        genres = item.get('genres')
        plot = item.get('plot')
        tagline = item.get('tagline')
        votecount = 0
        rating = item.get('rating')
        year = item.get('year')
        runtime = item.get('runtime')
        country = item.get('country')
        studio = item.get('studios')
        sorttitle = item['sorttitle']
        shortplot = item['shortplot']
        mpaa = item['mpaa']
        imdb = item.get('imdb')
        trailer = item['trailer']

        ##### GET THE FILE AND PATH #####
        filename = item.get('playurl')
        path = item.get('path')

        ##### UPDATE THE MOVIE #####
        if update_item:
            # log.info("UPDATE movie itemid: %s - Title: %s", itemid, title)

            # update new ratings Kodi 17
            if self.kodi_version >= 17:
                ratingid = self.kodi_db.get_ratingid(movieid)

                self.kodi_db.update_ratings(
                    movieid, "movie", "default", rating, votecount, ratingid)

            # update new uniqueid Kodi 17
            if self.kodi_version >= 17:
                uniqueid = self.kodi_db.get_uniqueid(movieid)

                self.kodi_db.update_uniqueid(
                    movieid, "movie", "imdb_id", "imdb", uniqueid)

            # Update the movie entry
            if self.kodi_version >= 17:
                self.kodi_db.update_movie_17(title, plot, shortplot, tagline, votecount, uniqueid,
                                             writer, year, uniqueid, sorttitle, runtime, mpaa, genre,
                                             director, title, studio, trailer, country, year,
                                             movieid)
            else:
                self.kodi_db.update_movie(title, plot, shortplot, tagline, votecount, rating,
                                          writer, year, imdb, sorttitle, runtime, mpaa, genre,
                                          director, title, studio, trailer, country, movieid)

            # Update the checksum in emby table
            # emby_db.updateReference(itemid, checksum)

        ##### OR ADD THE MOVIE #####
        else:
            # log.info("ADD movie itemid: %s - Title: %s", itemid, title)

            # add new ratings Kodi 17
            if self.kodi_version >= 17:
                ratingid = self.kodi_db.create_entry_rating()

                self.kodi_db.add_ratings(
                    ratingid, movieid, "movie", "default", rating, votecount)

            # add new uniqueid Kodi 17
            if self.kodi_version >= 17:
                uniqueid = self.kodi_db.create_entry_uniqueid()

                self.kodi_db.add_uniqueid(
                    uniqueid, movieid, "movie", "pptvid3", "imdb")

            # Add path
            pathid = self.kodi_db.add_path(path)
            # Add the file
            fileid = self.kodi_db.add_file(filename, pathid)

            # Create the movie entry
            if self.kodi_version >= 17:
                self.kodi_db.add_movie_17(movieid, fileid, title, plot, shortplot, tagline,
                                          votecount, uniqueid, writer, year, uniqueid, sorttitle,
                                          runtime, mpaa, genre, director, title, studio, trailer,
                                          country, year)
            else:
                self.kodi_db.add_movie(movieid, fileid, title, plot, shortplot, tagline,
                                       votecount, rating, writer, year, imdb, sorttitle,
                                       runtime, mpaa, genre, director, title, studio, trailer,
                                       country)

            # Create the reference in emby table
            self.source_db.addReference(itemid, movieid, source_type, "movie", fileid, pathid, None,
                                 "checksum")

        # Update the path
        self.kodi_db.update_path(pathid, path, "movies", "metadata.local")
        # Update the file
        self.kodi_db.update_file(fileid, filename, pathid, dateadded)

        # Process countries  --ignore
        # if 'ProductionLocations' in item:
        #     self.kodi_db.add_countries(movieid, item['ProductionLocations'])
        # Process cast
        # print([{"type": "actor", "name": actor} for actor in item['actors']])
        people = [{"type": "actor", "name": actor} for actor in item['actors']]
        people += [{"type": "director", "name": name} for name in directors]
        self.kodi_db.add_people(movieid, people, "movie")
        # Process genres
        self.kodi_db.add_genres(movieid, genres, "movie")
        # Process artwork
        self.kodi_db.add_artwork(item['artwork'], movieid, "movie")
        # Process stream details
        # streams = API.get_media_streams()
        # self.kodi_db.add_streams(fileid, streams, runtime)
        # Process studios
        # self.kodi_db.add_studios(movieid, studios, "movie")
        # Process tags: view, emby tags
        # tags = [viewtag]
        # tags.extend(item['tags'])

        self.kodi_db.add_tags(movieid, item['tags'], "movie")
        # Process playstates

        return True

    def add_updateBoxset(self, boxset):

        boxsetid = boxset['id']
        title = boxset['name']
        setartwork = boxset['artwork']
        dbitem = self.source_db.getItem_byId(boxsetid)
        try:
            setid = dbitem[0]
            self.kodi_db.update_boxset(setid, title)
        except TypeError:
            setid = self.kodi_db.add_boxset(title)

        # Process artwork
        self.kodi_db.add_artwork(setartwork, setid, "set")

        # Process movies inside boxset
        current_movies = self.source_db.getItemId_byParentId(setid, "movie")
        process = []
        try:
            # Try to convert tuple to dictionary
            current = dict(current_movies)
        except ValueError:
            current = {}

        # Sort current titles
        for current_movie in current:
            process.append(current_movie)

        # New list to compare
        for movie in boxset['items']:

            itemid = movie['id']

            if not current.get(itemid):
                # Assign boxset to movie
                movie_item = self.source_db.getItem_byId(itemid)
                try:
                    movieid = movie_item[0]
                except TypeError:
                    log.info("Failed to add: %s to boxset", movie['title'])
                    continue

                log.info("New addition to boxset %s: %s", title, movie['title'])
                self.kodi_db.set_boxset(setid, movieid)
                # Update emby reference
                self.source_db.updateParentId(itemid, setid)
            else:
                # Remove from process, because the item still belongs
                process.remove(itemid)

        # Process removals from boxset
        for movie in process:
            movieid = current[movie]
            log.info("Remove from boxset %s: %s", title, movieid)
            self.kodi_db.remove_from_boxset(movieid)
            # Update emby reference
            self.source_db.updateParentId(movie, None)

        # Update the reference in the emby table
        self.source_db.addReference(boxsetid, setid, "BoxSet", mediatype="set")

    def update_artist_artwork(self):
        people = self.kodi_db.get_no_artwork_person()
        for person in people:
            if self.kodi_db.update_artwork_from_douban(person[1], 'actor', person[0]):
                print((person[1] + "\t\tOK!").encode('gbk'))
            else:
                print((person[1] + "\t\tFail!").encode('gbk'))

    def updateUserdata(self, item):
        # This updates: Favorite, LastPlayedDate, Playcount, PlaybackPositionTicks
        # Poster with progress bar
        pass

    def remove(self, itemid):
        # Remove movieid, fileid, emby reference

        emby_dbitem = self.source_db.getItem_byId(itemid)
        try:
            kodiid = emby_dbitem[0]
            fileid = emby_dbitem[1]
            mediatype = emby_dbitem[4]
            log.info("Removing %sid: %s fileid: %s", mediatype, kodiid, fileid)
        except TypeError:
            return

        # Remove the emby reference
        self.source_db.removeItem(itemid)
        # Remove artwork
        self.kodi_db.delete_artwork(kodiid, mediatype)

        if mediatype == "movie":
            self.kodi_db.remove_movie(kodiid, fileid)

        elif mediatype == "set":
            # Delete kodi boxset
            boxset_movies = emby_db.getItem_byParentId(kodiid, "movie")
            for movie in boxset_movies:
                embyid = movie[0]
                movieid = movie[1]
                self.kodi_db.remove_from_boxset(movieid)
                # Update emby reference
                emby_db.updateParentId(embyid, None)

            self.kodi_db.remove_boxset(kodiid)

        log.info("Deleted %s %s from kodi database", mediatype, itemid)
