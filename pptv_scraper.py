# -*- coding: utf-8 -*-

import sqlite3
import requests

from common import *
from movies import Movies

KODI_DATABASE_PATH = 'D:\\Program Files (x86)\\Kodi17\\portable_data\\userdata\\Database\\'


class PPTVClass(object):
    HOMEHOST = 'tv.api.pptv.com'
    LISTHOST = 'epg.androidtv.cp61.ott.cibntv.net'
    DETAILHOST = 'epg.api.cp61.ott.cibntv.net'
    RELATEHOST = 'recommend.cp61.ott.cibntv.net'
    APPHOST = 'market.ott.cdn.pptv.com'
    TOPICHOST = 'tv.api.cp61.ott.cibntv.net'
    HOMEAPI = 'http://' + HOMEHOST + '/ppos/'
    LISTAPI = 'http://' + LISTHOST + '/'
    DETAILAPI = 'http://' + DETAILHOST + '/'
    RELATEAPI = 'http://' + RELATEHOST + '/'
    APPAPI = 'http://' + APPHOST + '/api/v2/'
    SHOPAPI = 'http://' + HOMEHOST + '/shop/'
    TOPICAPI = 'http://' + TOPICHOST + '/atvcibn/special/'
    PPI = 'AgACAAAAAgAATksAAAACAAAAAFhhPoA6c6A7DfvkYyt22APc1w5-U9eq5FEUyr9iLBpUpnnnNllkZwqRN9RI3cu6j9lIVJKHmXQgCh4K15mHQ1Cd8drT'

    def __init__(self, LocalDebug=False):
        self.LOCAL_DEBUG = LocalDebug

    def get_home_content(self):
        return requests.get(self.HOMEAPI + 'four/home?version={version}&channel_id={channel_id}&ppi={ppi}'.format(version="4.0.3", channel_id="1110141", ppi=self.PPI)).json()

    def get_recommended_config(self):
        return requests.get(self.HOMEAPI + 'rcmdNavConfig?version={version}&channel_id={channel_id}&ppi={ppi}'.format(version="4.0.3", channel_id="1110141", ppi=self.PPI), use_qua=False).json()

    def get_channel_config(self):
        return requests.get(self.HOMEAPI + 'channel_config?version={version}&channel_id={channel_id}&ppi={ppi}'.format(version="4.0.3", channel_id="1110141", ppi=self.PPI), use_qua=False).json()

    def get_channel_list(self, typeId, pn=1, ps=32, str_filter=None, sortType='hot'):
        url = self.LISTAPI + \
            'newList.api?auth={auth}&appver={appver}&canal={canal}&appid={appid}&appplt={appplt}&hasVirtual={hasVirtual}&typeId={typeId}&ps={ps}&pn={pn}&sortType={sortType}&contype={contype}&coverPre={coverPre}&ppi={ppi}&format={format}&isShowNav={isShowNav}&cannelSource={cannelSource}&ver={ver}'
        url = url.format(
            auth="1",
            appver="4.0.4",
            canal="CIBN",
            appid="PPTVLauncherSafe",
            appplt="launcher",
            hasVirtual=False,
            typeId=typeId,
            ps=ps,
            pn=pn,
            sortType=sortType,
            contype=0,
            coverPre="sp160",
            ppi=self.PPI,
            format="json",
            isShowNav="true",
            cannelSource="VST",
            ver="1"
        )
        if str_filter:
            url = url + '&' + str_filter
        return requests.get(url).json()

    def get_video_detail(self, cid):
        url = self.DETAILAPI + \
            'detail.api?auth={auth}&virtual={virtual}&ppi={ppi}&token={token}&appplt={appplt}&appid={appid}&appver={appver}&username={username}&type={type}&platform={platform}&vid={vid}&ver={ver}&lang={lang}&vvid={vvid}&gslbversion={gslbversion}&userLevel={userLevel}&coverPre={coverPre}&format=json'
        url = url.format(
            auth="1",
            virtual="0",
            ppi=self.PPI,
            token="",
            appplt="launcher",
            appid="com.pptv.launcher",
            appver="4.0.3",
            username="",
            type="ppbox.launcher",
            platform="launcher",
            vid=cid,
            ver="3",
            lang="zh_CN",
            vvid="90f1d8a5-106c-48d4-b806-fec3e5fa58fe",
            gslbversion="2",
            userLevel="0",
            coverPre="sp423")
        return requests.get(url).json()

    def get_video_relate(self, cid):
        url = self.RELATEAPI + \
            'recommend?appplt={appplt}&appid={appid}&appver={appver}&src={src}&video={video}&uid={uid}&num={num}&ppi={ppi}&extraFields={extraFields}&userLevel={userLevel}&vipUser={vipUser}&format=json'
        url = url.format(
            appplt="launcher",
            appid="pptvLauncher",
            appver="4.0.4",
            src="34",
            video=cid,
            uid="pptv",
            num=7,
            ppi=self.PPI,
            extraFields="douBanScore,isPay,vt,vipPrice,coverPic,isVip,score,epgCatas",
            userLevel="1",
            vipUser="0")
        return requests.get(url).json()

    def get_playinfo(self, vid):
        pass

    def get_userinfo(self):
        pass

    def get_video_subscribe(self, vid):
        pass

    def get_video_topic(self, tid):
        return requests.get(self.TOPICAPI + tid + '?version={version}&channel_id={channel_id}&user_level={user_level}'.format(version="4.0.3", channel_id="200026", user_level="0")).json()


def item_remap(item):
    pptv = PPTVClass()
    pptv_id = item['vid']
    isVST = pptv_id < 0
    detail = dict() if isVST else pptv.get_video_detail(pptv_id)['v']
    return {
        "title": item.get('title'),
        "dateadded": item.get('updatetime'),
        "writer": '',
        "director": ' / '.join(item.get('director').split(',')),
        "actors": item.get('act').split(','),
        "genres": item.get('catalog').split(','),
        "genre": ' / '.join(item.get('catalog').split(',')),
        "tags": [],
        "plot": detail.get('content'),
        "tagline": '',
        "rating": item.get('douBanScore'),
        "year": item.get('year'),
        "runtime": item.get('durationSecond'),
        "country": item.get('area'),
        "studio": '',
        "sorttitle": get_sorttitle(item.get('title')),
        "shortplot": item.get('subTitle'),
        "trailer": '',
        "mpaa": '',
        "source_type": 'VST' if isVST else "pptv",
        "source_id": item['uuid'] if isVST else pptv_id,
        "id": item['uuid'] if isVST else pptv_id,
        "playurl": "plugin://plugin.video.bigmovies/play/" + str(pptv_id),
        "path": "plugin://plugin.video.bigmovies/",
        "artwork": {
            "poster": item['imgurl']
        }
    }


def setitem_remap(set_item):
    item = set_item['_attributes']
    pptv_id = item['id']
    detail = pptv.get_video_detail(pptv_id)['v']
    return {
        "title": item.get('title'),
        "dateadded": detail.get('onlinetime'),
        "writer": '',
        "director": ' / '.join(detail.get('director').split(',')),
        "actors": detail.get('act').split(','),
        "genres": detail.get('catalog').split(','),
        "genre": ' / '.join(detail.get('catalog').split(',')),
        "tags": [],
        "plot": detail.get('content'),
        "tagline": '',
        "rating": detail.get('douBanScore'),
        "year": detail.get('year'),
        "runtime": detail.get('durationSecond'),
        "country": detail.get('area'),
        "studio": '',
        "sorttitle": get_sorttitle(item.get('title')),
        "shortplot": detail.get('subTitle'),
        "trailer": '',
        "mpaa": '',
        "source_type": "pptv",
        "source_id": pptv_id,
        "id": pptv_id,
        "playurl": "plugin://plugin.video.bigmovies/play/" + str(pptv_id),
        "path": "plugin://plugin.video.bigmovies/",
        "artwork": {
            "poster": item['imgurl']
        }
    }


if __name__ == "__main__":
    with sqlite3.connect(KODI_DATABASE_PATH + "MyVideos107.db", 120) as kodi_conn,\
            sqlite3.connect(KODI_DATABASE_PATH + "pptv.db", 120) as pp_conn:
        cursor = kodi_conn.cursor()
        pptv_cursor = pp_conn.cursor()
        mo = Movies(cursor, pptv_cursor)
        pptv = PPTVClass()
        try:
            # mo.update_artist_artwork()
            s = pptv.get_channel_list(1, pn=1, ps=1000)
            total_count = s['count']
            page_count = s['page_count']
            for index, item in enumerate(s['videos']):
                print_progress(item['title'].encode("gbk"), index, 1000, "Working: ")
                if item['vt'] == 22:  # movie set
                    set_detail = pptv.get_video_detail(item['vid'])['v']
                    if "video_list" not in set_detail:
                        continue
                    movielist = set_detail['video_list']['playlink2']
                    if isinstance(movielist, dict):
                        movielist = [movielist]
                    boxset = {
                        "name": item["title"],
                        "id": item['vid'],
                        "artwork": {"poster": item['imgurl']},
                        "items": map(setitem_remap, movielist)
                    }
                    mo.add_updateBoxset(boxset)
                mo.add_update(item_remap(item))
        except Exception as e:
            import traceback
            traceback.print_exc()
        pp_conn.commit()
        kodi_conn.commit()
