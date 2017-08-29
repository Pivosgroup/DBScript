# -*- coding: utf-8 -*-
import sqlite3
from movies import Movies

KODI_DATABASE_PATH = 'D:\\Program Files (x86)\\Kodi17\\portable_data\\userdata\\Database\\'

if __name__ == "__main__":
    with sqlite3.connect(KODI_DATABASE_PATH + "MyVideos107.db", 120) as kodi_conn,\
            sqlite3.connect(KODI_DATABASE_PATH + "pptv.db", 120) as pp_conn:
        cursor = kodi_conn.cursor()
        pptv_cursor = pp_conn.cursor()
        mo = Movies(cursor, pptv_cursor)
        try:
            mo.update_artist_artwork()
        except Exception as e:
            import traceback
            traceback.print_exc()
        kodi_conn.commit()
