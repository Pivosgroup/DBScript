# -*- coding: utf-8 -*-
import requests


class DoubanArtwork(object):

    def __init__(self):
        pass

    @staticmethod
    def search(text):
        API = "https://movie.douban.com/j/subject_suggest?q=%s" % text
        data = requests.get(API).json()
        return data

    @classmethod
    def get_artist_artwork(cls, name):
        assert name != ""
        item = cls.search(name)
        if len(item) > 0 and item[0]['type'] == 'celebrity':
            return item[0]['img'].replace('/small/', '/large/')
        else:
            return ''

    @classmethod
    def get_movie(cls, title):
        assert title != ""
        item = cls.search(title)
        if len(item) > 0 and item[0]['type'] == 'celebrity':
            return item[0]['img'].replace('/small/', '/large/')
        else:
            return ''


if __name__ == "__main__":
    img = DoubanArtwork.get_artist_artwork("王大陆")
    print(img)
