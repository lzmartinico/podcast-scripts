#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import sys
import re
import sqlite3
import json
import urllib.request
#
CDX_BASE="http://web.arthive.org/cdx/search/cdx?output=json&url={}"
TIMESTAMPED_ADDRESS_BASE="https://web.archive.org/web/{}if_/{}"

def fetch_old(url):
    "Takes a podcast url and return its archival version"
    cdx_url = str.format(CDX_BASE,url)
    json_response = json.load(urllib.request.urlopen(cdx_url))
    if len(json_response) is 0:
        return None
    timestamp = json_response[1][json_response[0].index('timestamp')] 
    web_archive_url = str.format(TIMESTAMPED_ADDRESS_BASE,timestamp,url)
    try:
        request_url = urllib.request.urlopen(web_archive_url)
    except urllib.error.HTTPError as e:
        print("HTTP exception: " + e)
    if request_url is None:
        return None
    # Handle unfollowed redirection
    if request_url.geturl().endswith(url):
        pattern = "function go\(\) \{\s+document\.location\.href = \"(.*)\"" #\\n\\t\s+document.location.href=\"(.*)\""
        data = request_url.read().decode('utf-8')
        match = re.search(pattern,data) 
        if match is None:
            print("match error with " + url)
            return None
        return match.group(1)
    else:
        return request_url.geturl()

def main(title):
    conn = sqlite3.connect("AntennaPodBackup.db") or die ("Couldn't open database")
    conn.row_factory = sqlite3.Row
    Feed_id = conn.execute("SELECT id FROM Feeds WHERE title is ?", (title,)).fetchone()
    FeedItem_cursor = conn.execute("SELECT * FROM FeedItems where feed IS ?", Feed_id).fetchall()
    for FeedItem in FeedItem_cursor:
       replaced_url = re.match("https://web.archive.org/web/(\d+)if_/(.*)$",FeedItem['link'])
       new_url = fetch_old(FeedItem['link'])
       if new_url is not None:
           print(FeedItem["link"] + " -> " + new_url)
           conn.execute("UPDATE FeedItems SET link=? WHERE id is ?", (new_url, FeedItem["id"]))
           conn.execute("UPDATE FeedMedia SET download_url=? WHERE id is ?", (new_url, FeedItem["id"]))
           conn.commit()
       else:
           print(FeedItem["link"] + " is alone")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python replace_outdated.py PODCAST_NAME ")
        print("Must be run in the same directory as file AntennaPod.db")
    else:
        main(sys.argv[1])
