#!/usr/bin/env python

from urllib.parse import urlencode
from xml.etree.ElementTree import fromstring
import json
from snulogin import login
import librtmp
from optparse import OptionParser


def __get_stream_url(session, video_id, as_settSeq):
    '''[Internal]'''
    r = session.post(
        'http://etl.snu.ac.kr/mod/vod/vod_ajax.php',
        data={'action': 'get_video', 'video': video_id}
    )
    data = json.loads(r.text)
    for k in data.keys():
        r = session.post(
            'http://etl.snu.ac.kr/mod/vod/rest.php',
            data={
                'rest': 'http://147.47.106.152:8080/rest/file/view/%s' % (
                    data[k]['fileseq'])})
        tree = fromstring(r.text)
        for stream in tree.find('streamList').findall('stream'):
            if stream.find('settSeq').text == as_settSeq:
                return data[k]['instanceid'], stream.find('url').text


def __get_base_url(session, iid):
    '''[Internal]'''
    data = {'rest': 'http://147.47.106.152:8080/rest/stream/url/rtmp/' + iid}
    r = session.post(
        'http://etl.snu.ac.kr/mod/vod/rest.php?' + urlencode(data),
        data=data)
    tree = fromstring(r.text)
    return tree.find('url').text


def __get_constants(session, url):
    '''[Internal]'''
    r = session.get(url)
    start_idx = r.text.find('var video = ')
    video_id = int(r.text[start_idx + 12:r.text.find(';', start_idx)])
    start_idx = r.text.find('var as_settSeq = ')
    as_settSeq = r.text[start_idx + 17:r.text.find(';', start_idx)]
    return video_id, as_settSeq


def __make_rtmp_stream(rtmp_url, pageurl):
    '''[Internal]'''
    conn = librtmp.RTMP(
        rtmp_url,
        playpath=rtmp_url[rtmp_url.find('mp4:'):],
        tcurl=rtmp_url,
        app=rtmp_url[rtmp_url.find('streams'):],
        swfurl='http://147.47.106.152:8080/common/jwplayer/player.swf',
        pageurl=pageurl)
    conn.connect()
    return conn.create_stream()


def download(url, userid, password, filename):
    """Download flv video file from url via rtmp protocol

    :param url: SNU eTL Video URL
    :param userid: MySNU User ID
    :param password: MySNU User Password
    :param filename: Video file name

    Usage::

        >>> from snu-etl-video-downloader import download
        >>> download(
        >>>     'http://etl.snu.ac.kr/mod/vod/viewer.php?i=4380',
        >>>     'userid',
        >>>     'password',
        >>>     'DATABASE_2014_FALL_2014-09-01.mp4')
    """
    s = login(userid, password)

    video_id, as_settSeq = __get_constants(s, url)
    instance_id, stream_url = __get_stream_url(s, video_id, as_settSeq)
    base_url = __get_base_url(s, instance_id)

    stream = __make_rtmp_stream(base_url + stream_url, url)
    with open(filename, 'wb') as f:
        while True:
            data = stream.read(1024)
            f.write(data)
            if len(data) == 0:
                break


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--f",
                      dest="filename", help="write video to file")
    parser.add_option("-u", "--userid",
                      dest="userid", help="MySNU User ID")
    parser.add_option("-p", "--password",
                      dest="password", help="MySNU Password")
    options, args = parser.parse_args()

    download(args[0], options.userid, options.password, options.filename)
