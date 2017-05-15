from flask import Flask, render_template
import mutagen
import os


class musicLibrary:
    def __init__(self, musicLocation):
        self.albumDict = {}
        self.musicLocation = musicLocation

    def listAlbums(self):
        albumList = os.listdir(self.musicLocation)
        if '.DS_Store' in albumList: albumList.remove('.DS_Store')
        for album in albumList:
            self.albumDict[album] = None
    def updateAlbumDict(self, album, instance):
        self.albumDict[album] = instance


class album:
    def __init__(self):
        self.albumTitle = None
        self.albumYear = None
        self.albumGenre = None
        self.albumArtist = None
        self.songList = []

    def updateAlbumMetadata (self, album, musicLocation):
        trackList = os.listdir(os.path.join(musicLocation, album))
        for song in trackList:
            if '.jpg' in song: continue
            print(song)
            songMetadata = mutagen.File(os.path.join(musicLocation, album, song))
            if self.albumTitle is None:
                self.albumTitle = "".join(songMetadata['album'])
            if self.albumYear is None:
                self.albumYear = "".join(songMetadata['date'])
            if self.albumGenre is None:
                self.albumGenre = "".join(songMetadata['genre'])
            if self.albumArtist is None:
                self.albumArtist = "".join(songMetadata['artist'])
            self.songList.append((int("".join(songMetadata['tracknumber'])), song))

MDsMusic = musicLibrary('/usr/media')
MDsMusic.listAlbums()

for k in MDsMusic.albumDict.keys():
    MDsMusic.updateAlbumDict(k, album())
    MDsMusic.albumDict[k].updateAlbumMetadata(k, MDsMusic.musicLocation)
    print(MDsMusic.albumDict[k].albumTitle)

waltz = Flask(__name__)

@waltz.route("/")
def main():
    return render_template('newsite.html', song_list=MDsMusic.albumDict)


if __name__ == '__main__':
    waltz.run()
