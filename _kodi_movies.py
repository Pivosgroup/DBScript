# -*- coding: utf-8 -*-

##################################################################################################

import logging

from _kodi_common import KodiItems

##################################################################################################

log = logging.getLogger("LD."+__name__)

##################################################################################################


class KodiMovies(KodiItems):


    def __init__(self, cursor):
        self.cursor = cursor

        KodiItems.__init__(self)

    def create_entry_uniqueid(self):
        self.cursor.execute("select coalesce(max(uniqueid_id),0) from uniqueid")
        kodi_id = self.cursor.fetchone()[0] + 1

        return kodi_id

    def create_entry_rating(self):
        self.cursor.execute("select coalesce(max(rating_id),0) from rating")
        kodi_id = self.cursor.fetchone()[0] + 1

        return kodi_id

    def create_entry(self):
        self.cursor.execute("select coalesce(max(idMovie),0) from movie")
        kodi_id = self.cursor.fetchone()[0] + 1

        return kodi_id

    def create_entry_set(self):
        self.cursor.execute("select coalesce(max(idSet),0) from sets")
        kodi_id = self.cursor.fetchone()[0] + 1

        return kodi_id

    def create_entry_country(self):
        self.cursor.execute("select coalesce(max(country_id),0) from country")
        kodi_id = self.cursor.fetchone()[0] + 1

        return kodi_id

    def get_movie(self, kodi_id):

        query = "SELECT * FROM movie WHERE idMovie = ?"
        self.cursor.execute(query, (kodi_id,))
        try:
            kodi_id = self.cursor.fetchone()[0]
        except TypeError:
            kodi_id = None

        return kodi_id

    def get_movie_by_title(self, title):
        query = "SELECT * FROM movie WHERE c00 = ?"
        self.cursor.execute(query, (title,))
        try:
            movie = self.cursor.fetchone()
        except TypeError:
            movie = None

        return movie

    def add_movie(self, *args):
        query = (
            '''
            INSERT INTO movie(
                idMovie, idFile, c00, c01, c02, c03, c04, c05, c06, c07,
                c09, c10, c11, c12, c14, c15, c16, c18, c19, c21)

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        )
        self.cursor.execute(query, (args))

    def add_movie_17(self, *args):
        # Create the movie entry
        query = (
            '''
            INSERT INTO movie(
                idMovie, idFile, c00, c01, c02, c03, c04, c05, c06, c07,
                c09, c10, c11, c12, c14, c15, c16, c18, c19, c21, premiered)

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
        )
        self.cursor.execute(query, (args))

    def update_movie(self, *args):
        query = ' '.join((

            "UPDATE movie",
            "SET c00 = ?, c01 = ?, c02 = ?, c03 = ?, c04 = ?, c05 = ?, c06 = ?,",
                "c07 = ?, c09 = ?, c10 = ?, c11 = ?, c12 = ?, c14 = ?, c15 = ?,",
                "c16 = ?, c18 = ?, c19 = ?, c21 = ?",
            "WHERE idMovie = ?"
        ))
        self.cursor.execute(query, (args))

    def update_movie_17(self, *args):
        query = ' '.join((

            "UPDATE movie",
            "SET c00 = ?, c01 = ?, c02 = ?, c03 = ?, c04 = ?, c05 = ?, c06 = ?,",
                "c07 = ?, c09 = ?, c10 = ?, c11 = ?, c12 = ?, c14 = ?, c15 = ?,",
                "c16 = ?, c18 = ?, c19 = ?, c21 = ?, premiered = ?",
            "WHERE idMovie = ?"
        ))
        self.cursor.execute(query, (args))

    def remove_movie(self, kodi_id, file_id):
        self.cursor.execute("DELETE FROM movie WHERE idMovie = ?", (kodi_id,))
        self.cursor.execute("DELETE FROM files WHERE idFile = ?", (file_id,))

    def get_ratingid(self, media_id):

        query = "SELECT rating_id FROM rating WHERE media_type = ? AND media_id = ?"
        self.cursor.execute(query, ("movie", media_id,))
        try:
            ratingid = self.cursor.fetchone()[0]
        except TypeError:
            ratingid = None

        return ratingid

    def add_ratings(self, *args):
        query = (
            '''
            INSERT INTO rating(
                rating_id, media_id, media_type, rating_type, rating, votes)

            VALUES (?, ?, ?, ?, ?, ?)
            '''
        )
        self.cursor.execute(query, (args))

    def update_ratings(self, *args):
        query = ' '.join((

            "UPDATE rating",
            "SET media_id = ?, media_type = ?, rating_type = ?, rating = ?, votes = ?",
            "WHERE rating_id = ?"
        ))
        self.cursor.execute(query, (args))

    def get_uniqueid(self, media_id):

        query = "SELECT uniqueid_id FROM uniqueid WHERE media_type = ? AND media_id = ?"
        self.cursor.execute(query, ("movie", media_id,))
        try:
            uniqueid = self.cursor.fetchone()[0]
        except TypeError:
            uniqueid = None

        return uniqueid

    def add_uniqueid(self, *args):
        query = (
            '''
            INSERT INTO uniqueid(
                uniqueid_id, media_id, media_type, value, type)

            VALUES (?, ?, ?, ?, ?)
            '''
        )
        self.cursor.execute(query, (args))

    def update_uniqueid(self, *args):
        query = ' '.join((

            "UPDATE uniqueid",
            "SET media_id = ?, media_type = ?, value = ?, type = ?",
            "WHERE uniqueid_id = ?"
        ))
        self.cursor.execute(query, (args))

    def add_countries(self, kodi_id, countries):

        if self.kodi_version > 14:

            for country in countries:
                country_id = self._get_country(country)

                query = (
                    '''
                    INSERT OR REPLACE INTO country_link(country_id, media_id, media_type)
                    VALUES (?, ?, ?)
                    '''
                )
                self.cursor.execute(query, (country_id, kodi_id, "movie"))
        else:
            # TODO: Remove Helix code when Krypton is RC
            for country in countries:
                query = ' '.join((

                    "SELECT idCountry",
                    "FROM country",
                    "WHERE strCountry = ?",
                    "COLLATE NOCASE"
                ))
                self.cursor.execute(query, (country,))

                try:
                    country_id = self.cursor.fetchone()[0]
                except TypeError:
                    # Create a new entry
                    self.cursor.execute("select coalesce(max(idCountry),0) from country")
                    country_id = self.cursor.fetchone()[0] + 1

                    query = "INSERT INTO country(idCountry, strCountry) values(?, ?)"
                    self.cursor.execute(query, (country_id, country))
                    log.debug("Add country to media, processing: %s", country)

                query = (
                    '''
                    INSERT OR REPLACE INTO countrylinkmovie(idCountry, idMovie)
                    VALUES (?, ?)
                    '''
                )
                self.cursor.execute(query, (country_id, kodi_id))

    def _add_country(self, country):

        country_id = self.create_entry_country()
        query = "INSERT INTO country(country_id, name) values(?, ?)"
        self.cursor.execute(query, (country_id, country))
        log.debug("Add country to media, processing: %s", country)

        return country_id

    def _get_country(self, country):
        query = ' '.join((

            "SELECT country_id",
            "FROM country",
            "WHERE name = ?",
            "COLLATE NOCASE"
        ))
        self.cursor.execute(query, (country,))
        try:
            country_id = self.cursor.fetchone()[0]
        except TypeError:
            country_id = self._add_country(country)

        return country_id

    def add_boxset(self, boxset):
        query = ' '.join((

            "SELECT idSet",
            "FROM sets",
            "WHERE strSet = ?",
            "COLLATE NOCASE"
        ))
        self.cursor.execute(query, (boxset,))
        try:
            set_id = self.cursor.fetchone()[0]
        except TypeError:
            set_id = self._add_boxset(boxset)

        return set_id

    def _add_boxset(self, boxset):

        set_id = self.create_entry_set()
        query = "INSERT INTO sets(idSet, strSet) values(?, ?)"
        self.cursor.execute(query, (set_id, boxset))
        log.debug("Adding boxset: %s", boxset)

        return set_id

    def update_boxset(self, set_id, boxset):
        query = ' '.join((

            "UPDATE sets",
            "SET strSet = ?",
            "WHERE idSet = ?"
        ))
        self.cursor.execute(query, (boxset, set_id,))

    def set_boxset(self, set_id, movie_id):
        query = ' '.join((

            "UPDATE movie",
            "SET idSet = ?",
            "WHERE idMovie = ?"
        ))
        self.cursor.execute(query, (set_id, movie_id,))

    def remove_from_boxset(self, movie_id):
        query = ' '.join((

            "UPDATE movie",
            "SET idSet = null",
            "WHERE idMovie = ?"
        ))
        self.cursor.execute(query, (movie_id,))

    def remove_boxset(self, kodi_id):
        self.cursor.execute("DELETE FROM sets WHERE idSet = ?", (kodi_id,))
