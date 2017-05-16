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
        self.errorsFound = []

    def updateAlbumMetadata (self, album, musicLocation):
        trackList = os.listdir(os.path.join(musicLocation, album))
        for song in trackList:
            if '.jpg' in song: continue
            if '.log' in song: continue
            songMetadata = mutagen.File(os.path.join(musicLocation, album, song))

            if self.albumTitle is None and 'albumTitle' not in self.errorsFound:
                try:
                    self.albumTitle = "".join(songMetadata['album'])
                except:
                    self.errorsFound.append('albumTitle')
            if self.albumYear is None and 'albumYear' not in self.errorsFound:
                try:
                    self.albumYear = "".join(songMetadata['date'])
                except:
                    self.errorsFound.append('albumYear')
            if self.albumGenre is None and 'albumGenre' not in self.errorsFound:
                try:
                    self.albumGenre = "".join(songMetadata['genre'])
                except:
                    self.errorsFound.append('albumGenre')
            if self.albumArtist is None and 'albumArtist' not in self.errorsFound:
                try:
                    self.albumArtist = "".join(songMetadata['artist'])
                except:
                    self.errorsFound.append('albumArtist')
            try:
                self.songList.append((int("".join(songMetadata['tracknumber'])), song))
            except:
                self.errorsFound.append('Missing Track Number')
                self.songList.append(song)

    def errorReporting(self):
        return self.errorsFound

MDsMusic = musicLibrary('/usr/media')
MDsMusic.listAlbums()

for k in MDsMusic.albumDict.keys():
    MDsMusic.updateAlbumDict(k, album())
    MDsMusic.albumDict[k].updateAlbumMetadata(k, MDsMusic.musicLocation)

firstV = []
secondV = []

for k, v in MDsMusic.albumDict.items():
    firstV.append(v)
    if len(firstV) == 20: break

for k, v in MDsMusic.albumDict.items():
    if v not in firstV:
        secondV.append(v)


waltz = Flask(__name__)

@waltz.route("/")
def main():
    return render_template('newsite.html', song_list=firstV)

@waltz.route('/more')
def moreSongs():
    song_list = secondV
    return render_template('newsite.html', song_list=secondV)


if __name__ == '__main__':
    waltz.run()
