Applefy
=============

Converts your Spotify playlist into an Apple music importable list of MP3s.

Usage
-----
Firstly obtain the link to the Spotify playlist you want to add to iTunes and run the python script.

    ./applefy.py [username] [password] [spotify_url]

This will create a folder containing the first second of each song within an MP3 file.

Create your playlist in Apple Music/iTunes and drag the MP3 files into that playlist.

Select all songs and right click in iTunes, add them to your "iCloud Music Library" so that they are synced with your account. You can now delete the MP3 files and then choose to redownload the music via your Apple Music subscription.

Example
--------
    "./applyfy.py user pass spotify:user:[user]:playlist:7HC9PMdSbwGBBn3EVTaCNx copies entire playlist

Prerequisites:
--------------
* libspotify (download at https://developer.spotify.com/technologies/libspotify/)

* pyspotify (sudo pip install -U pyspotify, requires python-dev)

* spotify binary appkey (download at developer.spotify.com and copy to wd, requires premium!)

* lame (sudo apt-get install lame)

* eyeD3 (sudo pip install eyeD3 --allow-external eyeD3 --allow-unverified eyeD3)

Credits
----
Based on spotifyripper.
