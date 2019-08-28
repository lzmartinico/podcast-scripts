#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This script will copy the first playlist in Podcast Addict into AntennaPod's queue
# CAUTION: the script is not yet working. It creates an AntennaPod database containing the Queue as intended, and can be imported in AntennaPod, but the database is never succesfully loaded
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
import os
import sys
import sqlite3
#

db = 'podcastAddict.db' # PodcastAddict database file (relative to script)
export_db = 'Export' # AntennaPod file

# Key-constants
KEY_ID = "id"
KEY_TITLE = "title"
KEY_CUSTOM_TITLE = "custom_title"
KEY_NAME = "name"
KEY_LINK = "link"
KEY_DESCRIPTION = "description"
KEY_FILE_URL = "file_url"
KEY_DOWNLOAD_URL = "download_url"
KEY_PUBDATE = "pubDate"
KEY_READ = "read"
KEY_DURATION = "duration"
KEY_POSITION = "position"
KEY_SIZE = "filesize"
KEY_MIME_TYPE = "mime_type"
KEY_IMAGE = "image"
KEY_IMAGE_URL = "image_url"
KEY_FEED = "feed"
KEY_MEDIA = "media"
KEY_DOWNLOADED = "downloaded"
KEY_LASTUPDATE = "last_update"
KEY_FEEDFILE = "feedfile"
KEY_REASON = "reason"
KEY_SUCCESSFUL = "successful"
KEY_FEEDFILETYPE = "feedfile_type"
KEY_COMPLETION_DATE = "completion_date"
KEY_FEEDITEM = "feeditem"
KEY_CONTENT_ENCODED = "content_encoded"
KEY_PAYMENT_LINK = "payment_link"
KEY_START = "start"
KEY_LANGUAGE = "language"
KEY_AUTHOR = "author"
KEY_HAS_CHAPTERS = "has_simple_chapters"
KEY_TYPE = "type"
KEY_ITEM_IDENTIFIER = "item_identifier"
KEY_FLATTR_STATUS = "flattr_status"
KEY_FEED_IDENTIFIER = "feed_identifier"
KEY_REASON_DETAILED = "reason_detailed"
KEY_DOWNLOADSTATUS_TITLE = "title"
KEY_CHAPTER_TYPE = "type"
KEY_PLAYBACK_COMPLETION_DATE = "playback_completion_date"
KEY_AUTO_DOWNLOAD = "auto_download"
KEY_KEEP_UPDATED = "keep_updated"
KEY_AUTO_DELETE_ACTION = "auto_delete_action"
KEY_PLAYED_DURATION = "played_duration"
KEY_USERNAME = "username"
KEY_PASSWORD = "password"
KEY_IS_PAGED = "is_paged"
KEY_NEXT_PAGE_LINK = "next_page_link"
KEY_HIDE = "hide"
KEY_LAST_UPDATE_FAILED = "last_update_failed"
KEY_HAS_EMBEDDED_PICTURE = "has_embedded_picture"
KEY_LAST_PLAYED_TIME = "last_played_time"
KEY_INCLUDE_FILTER = "include_filter"
KEY_EXCLUDE_FILTER = "exclude_filter"

# Table names
TABLE_NAME_FEEDS = "Feeds"
TABLE_NAME_FEED_ITEMS = "FeedItems"
TABLE_NAME_FEED_IMAGES = "FeedImages"
TABLE_NAME_FEED_MEDIA = "FeedMedia"
TABLE_NAME_DOWNLOAD_LOG = "DownloadLog"
TABLE_NAME_QUEUE = "Queue"
TABLE_NAME_SIMPLECHAPTERS = "SimpleChapters"
TABLE_NAME_FAVORITES = "Favorites"

TABLE_PRIMARY_KEY = KEY_ID + " INTEGER PRIMARY KEY AUTOINCREMENT ,"

# Create statements
CREATE_TABLE_FEEDS = "CREATE TABLE " + TABLE_NAME_FEEDS + " (" + TABLE_PRIMARY_KEY + KEY_TITLE    + " TEXT," + KEY_CUSTOM_TITLE + " TEXT," + KEY_FILE_URL + " TEXT," + KEY_DOWNLOAD_URL + " TEXT,"    + KEY_DOWNLOADED + " INTEGER," + KEY_LINK + " TEXT,"    + KEY_DESCRIPTION + " TEXT," + KEY_PAYMENT_LINK + " TEXT,"    + KEY_LASTUPDATE + " TEXT," + KEY_LANGUAGE + " TEXT," + KEY_AUTHOR    + " TEXT," + KEY_IMAGE_URL + " TEXT," + KEY_TYPE + " TEXT,"    + KEY_FEED_IDENTIFIER + " TEXT," + KEY_AUTO_DOWNLOAD + " INTEGER DEFAULT 1,"    + KEY_FLATTR_STATUS + " INTEGER,"    + KEY_USERNAME + " TEXT,"    + KEY_PASSWORD + " TEXT,"    + KEY_INCLUDE_FILTER + " TEXT DEFAULT '',"    + KEY_EXCLUDE_FILTER + " TEXT DEFAULT '',"    + KEY_KEEP_UPDATED + " INTEGER DEFAULT 1,"    + KEY_IS_PAGED + " INTEGER DEFAULT 0,"    + KEY_NEXT_PAGE_LINK + " TEXT,"    + KEY_HIDE + " TEXT,"    + KEY_LAST_UPDATE_FAILED + " INTEGER DEFAULT 0,"    + KEY_AUTO_DELETE_ACTION + " INTEGER DEFAULT 0)"
CREATE_TABLE_FEED_ITEMS = "CREATE TABLE "    + TABLE_NAME_FEED_ITEMS + " (" + TABLE_PRIMARY_KEY + KEY_TITLE    + " TEXT," + KEY_CONTENT_ENCODED + " TEXT," + KEY_PUBDATE    + " INTEGER," + KEY_READ + " INTEGER," + KEY_LINK + " TEXT,"    + KEY_DESCRIPTION + " TEXT," + KEY_PAYMENT_LINK + " TEXT,"    + KEY_MEDIA + " INTEGER," + KEY_FEED + " INTEGER,"    + KEY_HAS_CHAPTERS + " INTEGER," + KEY_ITEM_IDENTIFIER + " TEXT,"    + KEY_FLATTR_STATUS + " INTEGER,"    + KEY_IMAGE_URL + " TEXT,"    + KEY_AUTO_DOWNLOAD + " INTEGER)"
CREATE_TABLE_QUEUE  = "CREATE TABLE " + TABLE_NAME_QUEUE + "(" + KEY_ID + " INTEGER PRIMARY KEY," + KEY_FEEDITEM + " INTEGER," + KEY_FEED + " INTEGER)"

# Insert statements
INSERT_STUB = "INSERT INTO {} values ({})"

def initialise_export(db):
    '''
    Creates database and tables for insertation in AntennaPod
    SQL drawn from core/src/main/java/de/danoeh/antennapod/core/storage/PodDBAdapter.java
    '''

    conn = sqlite3.connect(db) or die ("Couldn't open %s" % db)
    conn.execute(CREATE_TABLE_FEEDS)
    conn.execute(CREATE_TABLE_FEED_ITEMS)
    conn.execute(CREATE_TABLE_QUEUE)
    return conn

def fetch_thumbnail_url(connection, url_id):
    '''Fetch the url for a thumbnail in the PodcastAddict database given its id'''
    row = connection.execute("SELECT url FROM bitmaps where _id is ?", (url_id,)).fetchone()
    if row is not None:
        return row['url']
    else:
        return None

def fetch_feed_values(podcast_info_object, podcast_id, thumbnail_url):
    # Given a podcast id, return tuple with informations about the podcast using the FEED table scheme
    values = []
    values.append(podcast_id)  # ...podcast_info['_id']?
    values.append(podcast_info_object['name'])  #KEY_TITLE
    values.append(podcast_info_object['custom_name'])  #KEY_CUSTOM_TITLE
    values.append("/storage/emulated/0/Android/data/de.danoeh.antennapod/files/cache/feed-" + podcast_info_object['name']) #KEY_FILE_URL
    values.append(podcast_info_object['feed_url'])  #KEY_DOWNLOAD_URL
    values.append(1)  # KEY_DOWNLOADED
    values.append(podcast_info_object['homepage'])  # KEY_LINK
    values.append(podcast_info_object['description'])  # KEY_DESCRIPTION
    values.append("")  # KEY_PAYMENT_LINK
    values.append("Mon, 17 Jun 2019 12:00:00 GMT")  # KEY_LAST_UPDATE
    values.append("en" if podcast_info_object['language'] == "English" else podcast_info_object['language'])
    values.append(podcast_info_object["author"])
    values.append(thumbnail_url) # KEY_IMAGE_URL
    values.append("rss")
    values.append("")  # feed_identifier
    values.append(1)  # auto_download
    values.append(0)  # flattr status
    values.append("")
    values.append("")
    values.append("")
    values.append("")
    values.append(1)
    values.append(0)
    values.append("")
    values.append("")
    values.append(0)
    values.append(0)
    return values

def fetch_feed_item_values(episode_id, podcast_info_object, thumbnail_url):
    values = []
    values.append(episode_id)
    values.append(podcast_info_object['name'])
    values.append(podcast_info_object['content'])
    values.append(podcast_info_object['publication_date'])
    values.append(0)   # KEY_READ
    values.append("")   # KEY_LINK
    values.append(podcast_info_object['description'])
    values.append("")
    values.append("")
    values.append(podcast_info_object['podcast_id'])
    values.append(0)  # KEY_HAS_SIMPLE_CHAPTERS
    values.append(podcast_info_object['download_url'])
    values.append(0)  # KEY_FLATTR_STATUS
    values.append(thumbnail_url)
    values.append(1)  # KEY_AUTO_DOWNLOAD
    return values

def fetch_queue_values(queue_id, feed_id, feed_item_id):
    return (queue_id, feed_id, feed_item_id)

def main():

    # Open Database
    conn = sqlite3.connect(db) or die ("Couldn't open %s" % db)
    conn.row_factory = sqlite3.Row

    # Read Podcast URLS from database
    ORDERED_LIST_QUERY = "SELECT id FROM ordered_list GROUP BY rank HAVING (COUNT(rank) = 1)"
    uniq_episodes = conn.execute(ORDERED_LIST_QUERY).fetchall()
    ordered_episodes = []
    for row in uniq_episodes:
        ordered_episodes.append(conn.execute("SELECT * FROM episodes WHERE _id is " + str(row[0])).fetchone())

    podcast_feeds = {}
    exp_conn = initialise_export(export_db)
    for key_id, ep in enumerate(ordered_episodes):
        # if podcast does not exist, create new feed
        # probably store in dictionary on feed title
        podcast_id = ep['podcast_id']
        if not podcast_id in podcast_feeds:
            podcast_feeds[podcast_id] = key_id
            podcast_info = conn.execute("SELECT * FROM podcasts where _id is ?", (podcast_id,)).fetchone()
            thumbnail_url = fetch_thumbnail_url(conn,podcast_info['thumbnail_id'])
            values = fetch_feed_values(dict(podcast_info), podcast_id, thumbnail_url)
            INSERT_FEED =  INSERT_STUB.format(TABLE_NAME_FEEDS, ", ".join('?' * len(values)))
            exp_conn.execute(INSERT_FEED, values)
        # insert new episode into Feed
        thumbnail_url = fetch_thumbnail_url(conn, ep['thumbnail_id'])
        values = fetch_feed_item_values(key_id, ep, thumbnail_url)
        INSERT_FEED_ITEM = INSERT_STUB.format(TABLE_NAME_FEED_ITEMS, ", ".join('?' * len(values)))
        exp_conn.execute(INSERT_FEED_ITEM, values)
        #TODO: should also make a FeedMedia table and insert files
        values = fetch_queue_values(key_id, podcast_id, key_id)
        INSERT_QUEUE_ITEM = INSERT_STUB.format(TABLE_NAME_QUEUE, ", ".join('?' * len(values)))
        exp_conn.execute(INSERT_QUEUE_ITEM, values)
        exp_conn.commit()

    # Close Database
    exp_conn.close()
    conn.close()

if __name__ == "__main__":
    main()
