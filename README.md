Applefy
=======

Converts your Spotify playlist into an Apple music importable list of MP3s.

Setup
-----

    #Install homebrew
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    
    #Install stuff
    brew install python wget

    #Install pip
    easy_install pip
    
    #Download libspotify
    wget https://developer.spotify.com/download/libspotify/libspotify-12.1.51-Darwin-universal.zip
    unzip libspotify-12.1.51-Darwin-universal.zip
    rm libspotify-12.1.51-Darwin-universal.zip

    #Copy framework
    sudo cp -R libspotify-12.1.51-Darwin-universal/libspotify.framework /Library/Frameworks
    sudo ln -s /Library/Frameworks/libspotify.framework/libspotify /usr/local/lib/libspotify.dylib

    #Install eyeD3 for metadata tagging
    pip install eyeD3 --allow-external eyeD3 --allow-unverified eyeD3
 
    #Install pyspotify
    pip install pyspotify==1.11
    
    #Download project from GitHub
    git clone git://github.com/ryanb93/Applefy

    #Grab a developer key from Spotify (requires Premium)
    open https://devaccount.spotify.com/my-account/keys/
    
    #Copy the key into Applefy directory.
    cp ~/Downloads/spotify_appkey.key spotify_appkey.key
    
    


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

Credits
----
Based on [spotifyripper](https://github.com/robbeofficial/spotifyripper).
