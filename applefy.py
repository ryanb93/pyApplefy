#!/usr/bin/env python
# -*- coding: utf8 -*-

from subprocess import call
from spotify import Link
from jukebox import Jukebox, container_loaded
from shutil import copyfile
import os, sys
import threading
import time

def rip_init(session, track, playlist_name):
    silent = "5sec.mp3"
    mp3file = track.name() + ".mp3"
    copyfile(silent, get_path(playlist_name, mp3file))

def get_path(playlist, mp3):
    directory = os.path.join(os.getcwd(), playlist.replace("/", " "));
    if not os.path.exists(directory):
        os.makedirs(directory)
    fullPath = os.path.join(directory, mp3.replace("/", " "));
    return fullPath

def rip_id3(session, track, playlist_name): # write ID3 data
    
    mp3file = track.name() + ".mp3"

    num_track = "%02d" % (track.index(),)
    artist = track.artists()[0].name()
    album = track.album().name()
    title = track.name()
    year = track.album().year()

    # write id3 data
    cmd = "eyeD3" + \
          " -t \"" + title + "\"" + \
          " -a \"" + artist + "\"" + \
          " -A \"" + album + "\"" + \
          " -n " + str(num_track) + \
          " -Y " + str(year) + \
          " -Q " + \
          " \"" + get_path(playlist_name, mp3file) + "\""
    call(cmd, shell=True)

class RipperThread(threading.Thread):
    def __init__(self, ripper):
        threading.Thread.__init__(self)
        self.ripper = ripper

    def run(self):
        # wait for container
        container_loaded.wait()
        container_loaded.clear()

        # create track iterator
        link = Link.from_string(sys.argv[3])
        if link.type() == Link.LINK_PLAYLIST:
            playlist = link.as_playlist()
            print('Loading the playlist: ' + str(playlist))
            while not playlist.is_loaded():
                time.sleep(0.1)
            print('done')
            session = self.ripper.session
            name = str(playlist)
            print("name: " + name)
            for track in iter(playlist):
                self.ripper.load_track(track)
                rip_init(session, track, name)
                rip_id3(session, track, name)

            self.ripper.disconnect()

class Ripper(Jukebox):
    def __init__(self, *a, **kw):
        Jukebox.__init__(self, *a, **kw)
        self.ui = RipperThread(self) # replace JukeboxUI

if __name__ == '__main__':
    if len(sys.argv) == 4:
		ripper = Ripper(sys.argv[1],sys.argv[2]) # login
		ripper.connect()
    else:
		print "usage : \n"
		print "	  ./applefy.py [username] [password] [spotify_playlist_url]"
		print "example : \n"
		print "   ./applefy.py user pass spotify:user:username:playlist:4vkGNcsS8lRXj4q945NIA4 0 - clones entire playlist"
