from __future__ import unicode_literals

import base64

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    int_or_none,
    urlencode_postdata,
)


class SharedBaseIE(InfoExtractor):
    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage, urlh = self._download_webpage_handle(url, video_id)

        if self._FILE_NOT_FOUND in webpage:
            raise ExtractorError(
                'Video %s does not exist' % video_id, expected=True)

        video_url = self._extract_video_url(webpage, video_id, url)

        title = base64.b64decode(self._html_search_meta(
            'full:title', webpage, 'title').encode('utf-8')).decode('utf-8')
        filesize = int_or_none(self._html_search_meta(
            'full:size', webpage, 'file size', fatal=False))

        return {
            'id': video_id,
            'url': video_url,
            'ext': 'mp4',
            'filesize': filesize,
            'title': title,
        }


class SharedIE(SharedBaseIE):
    IE_DESC = 'shared.sx'
    _VALID_URL = r'https?://shared\.sx/(?P<id>[\da-z]{10})'
    _FILE_NOT_FOUND = '>File does not exist<'

    _TEST = {
        'url': 'http://shared.sx/0060718775',
        'md5': '106fefed92a8a2adb8c98e6a0652f49b',
        'info_dict': {
            'id': '0060718775',
            'ext': 'mp4',
            'title': 'Bmp4',
            'filesize': 1720110,
        },
    }

    def _extract_video_url(self, webpage, video_id, url):
        download_form = self._hidden_inputs(webpage)

        video_page = self._download_webpage(
            url, video_id, 'Downloading video page',
            data=urlencode_postdata(download_form),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': url,
            })

        video_url = self._html_search_regex(
            r'data-url=(["\'])(?P<url>(?:(?!\1).)+)\1',
            video_page, 'video URL', group='url')

        return video_url


class VivoIE(SharedBaseIE):
    IE_DESC = 'vivo.sx'
    _VALID_URL = r'https?://vivo\.sx/(?P<id>[\da-z]{10})'
    _FILE_NOT_FOUND = '>The file you have requested does not exists or has been removed'

    _TEST = {
        'url': 'http://vivo.sx/d7ddda0e78',
        'md5': '15b3af41be0b4fe01f4df075c2678b2c',
        'info_dict': {
            'id': 'd7ddda0e78',
            'ext': 'mp4',
            'title': 'Chicken',
            'filesize': 528031,
        },
    }

    def _extract_video_url(self, webpage, video_id, *args):
        return self._parse_json(
            self._search_regex(
                r'InitializeStream\s*\(\s*(["\'])(?P<url>(?:(?!\1).)+)\1',
                webpage, 'stream', group='url'),
            video_id,
            transform_source=lambda x: base64.b64decode(
                x.encode('ascii')).decode('utf-8'))[0]
