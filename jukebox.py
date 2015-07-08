#!/usr/bin/env python
# -*- coding: utf8 -*-

import cmd
import logging
import os
import threading
import time

from spotify import ArtistBrowser, Link, ToplistBrowser, SpotifyError
from spotify.audiosink import import_audio_sink
from spotify.manager import (
    SpotifySessionManager, SpotifyPlaylistManager, SpotifyContainerManager)

AudioSink = import_audio_sink()
container_loaded = threading.Event()


class JukeboxUI(cmd.Cmd, threading.Thread):

    prompt = "jukebox> "

    def __init__(self, jukebox):
        cmd.Cmd.__init__(self)
        threading.Thread.__init__(self)
        self.jukebox = jukebox
        self.playlist = None
        self.track = None
        self.results = False

    def run(self):
        container_loaded.wait()
        container_loaded.clear()
        try:
            self.cmdloop()
        finally:
            self.do_quit(None)

    def do_logout(self, line):
        self.jukebox.session.logout()

    def do_quit(self, line):
        self.jukebox.stop()
        self.jukebox.disconnect()
        print "Goodbye!"
        return True

    def do_list(self, line):
        """ List the playlists, or the contents of a playlist """
        if not line:
            i = -1
            for i, p in enumerate(self.jukebox.ctr):
                if p.is_loaded():
                    if Link.from_playlist(p).type() == Link.LINK_STARRED:
                        name = "Starred by %s" % p.owner()
                    else:
                        name = p.name()
                    print "%3d %s" % (i, name)
                else:
                    print "%3d %s" % (i, "loading...")
            print "%3d Starred tracks" % (i + 1,)

        else:
            try:
                p = int(line)
            except ValueError:
                print "that's not a number!"
                return
            if p < 0 or p > len(self.jukebox.ctr):
                print "That's out of range!"
                return
            print "Listing playlist #%d" % p
            if p < len(self.jukebox.ctr):
                playlist = self.jukebox.ctr[p]
            else:
                playlist = self.jukebox.starred
            for i, t in enumerate(playlist):
                if t.is_loaded():
                    print "%3d %s - %s [%s]" % (
                        i, t.artists()[0].name(), t.name(),
                        self.pretty_duration(t.duration()))
                else:
                    print "%3d %s" % (i, "loading...")

    def pretty_duration(self, milliseconds):
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        duration = '%02d:%02d' % (minutes, seconds)
        return duration

    def do_browse(self, line):
        if not line or not line.startswith("spotify:"):
            print "Invalid id provided"
            return
        l = Link.from_string(line)
        if not l.type() in [Link.LINK_ALBUM, Link.LINK_ARTIST]:
            print "You can only browse albums and artists"
            return

        def browse_finished(browser, userdata):
            print "Browse finished, %s" % (userdata)

        self.jukebox.browse(l, browse_finished)

    def print_search_results(self):
        print "Artists:"
        for a in self.results.artists():
            print "    ", Link.from_artist(a), a.name()
        print "Albums:"
        for a in self.results.albums():
            print "    ", Link.from_album(a), a.name()
        print "Tracks:"
        for a in self.results.tracks():
            print "    ", Link.from_track(a, 0), a.name()
        print self.results.total_tracks() - len(self.results.tracks()), \
            "Tracks not shown"

    def do_search(self, line):
        if not line:
            if self.results is False:
                print "No search is in progress"
            elif self.results is None:
                print "Searching is in progress"
            else:
                print "Artists:"
                for a in self.results.artists():
                    print "    ", Link.from_artist(a), a.name()
                print "Albums:"
                for a in self.results.albums():
                    print "    ", Link.from_album(a), a.name()
                print "Tracks:"
                for a in self.results.tracks():
                    print "    ", Link.from_track(a, 0), a.name()
                print "%d tracks not shown" % (
                    self.results.total_tracks() - len(self.results.tracks()))
        else:
            line = line.decode('utf-8')
            self.results = None

            def search_finished(results, userdata):
                print "\nSearch results received"
                self.results = results
                self.print_search_results()

            self.jukebox.search(line, search_finished)

    def emptyline(self):
        pass

    def do_shell(self, line):
        self.jukebox.shell()

    do_ls = do_list
    do_EOF = do_quit


class JukeboxPlaylistManager(SpotifyPlaylistManager):
    def tracks_added(self, p, t, i, u):
        print 'Tracks added to playlist %s' % p.name()

    def tracks_moved(self, p, t, i, u):
        print 'Tracks moved in playlist %s' % p.name()

    def tracks_removed(self, p, t, u):
        print 'Tracks removed from playlist %s' % p.name()

    def playlist_renamed(self, p, u):
        print 'Playlist renamed to %s' % p.name()


class JukeboxContainerManager(SpotifyContainerManager):
    def container_loaded(self, c, u):
        container_loaded.set()

    def playlist_added(self, c, p, i, u):
        print 'Container: playlist "%s" added.' % p.name()

    def playlist_moved(self, c, p, oi, ni, u):
        print 'Container: playlist "%s" moved.' % p.name()

    def playlist_removed(self, c, p, i, u):
        print 'Container: playlist "%s" removed.' % p.name()


class Jukebox(SpotifySessionManager):
    queued = False
    playlist = 2
    track = 0
    appkey_file = os.path.join(os.path.dirname(__file__), 'spotify_appkey.key')

    def __init__(self, *a, **kw):
        SpotifySessionManager.__init__(self, *a, **kw)
        self.audio = AudioSink(backend=self)
        self.ui = JukeboxUI(self)
        self.ctr = None
        self.playing = False
        self._queue = []
        self.playlist_manager = JukeboxPlaylistManager()
        self.container_manager = JukeboxContainerManager()
        self.track_playing = None
        print "Logging in, please wait..."

    def new_track_playing(self, track):
        self.track_playing = track

    def logged_in(self, session, error):
        if error:
            print error
            return
        print "Logged in!"
        self.ctr = session.playlist_container()
        self.container_manager.watch(self.ctr)
        self.starred = session.starred()
        if not self.ui.is_alive():
            self.ui.start()

    def logged_out(self, session):
        print "Logged out!"

    def load_track(self, track):
        print u"Loading track..."
        while not track.is_loaded():
            time.sleep(0.1)
        if track.is_autolinked():  # if linked, load the target track instead
            print "Autolinked track, loading the linked-to track"
            return self.load_track(track.playable())
        if track.availability() != 1:
            print "Track not available (%s)" % track.availability()
        if self.playing:
            self.stop()
        self.new_track_playing(track)
        self.session.load(track)
        print "Loaded track: %s" % track.name()

    def load(self, playlist, track):
        if self.playing:
            self.stop()
        if 0 <= playlist < len(self.ctr):
            pl = self.ctr[playlist]
        elif playlist == len(self.ctr):
            pl = self.starred
        spot_track = pl[track]
        self.new_track_playing(spot_track)
        self.session.load(spot_track)
        print "Loading %s from %s" % (spot_track.name(), pl.name())

    def load_playlist(self, playlist):
        if self.playing:
            self.stop()
        if 0 <= playlist < len(self.ctr):
            pl = self.ctr[playlist]
        elif playlist == len(self.ctr):
            pl = self.starred
        print "Loading playlist %s" % pl.name()
        if len(pl):
            print "Loading %s from %s" % (pl[0].name(), pl.name())
            self.new_track_playing(pl[0])
            self.session.load(pl[0])
        for i, track in enumerate(pl):
            if i == 0:
                continue
            self._queue.append((playlist, i))

    def shell(self):
        import code
        shell = code.InteractiveConsole(globals())
        shell.interact()

if __name__ == '__main__':
    import optparse
    op = optparse.OptionParser(version="%prog 0.1")
    op.add_option("-u", "--username", help="Spotify username")
    op.add_option("-p", "--password", help="Spotify password")
    op.add_option(
        "-v", "--verbose", help="Show debug information",
        dest="verbose", action="store_true")
    (options, args) = op.parse_args()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    session_m = Jukebox(options.username, options.password, True)
    session_m.connect()
