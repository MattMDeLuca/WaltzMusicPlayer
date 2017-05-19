from flask import Flask, render_template, session
import mutagen
import os


class musicLibrary:
    def __init__(self, musicLocation):
        self.albumDict = {}
        self.musicLocation = musicLocation
        self.albumSorted = []
        self.artistSorted = []
        self.yearSorted = []
        self.librarySize = None

    def listAlbums(self):
        albumList = os.listdir(self.musicLocation)
        if '.DS_Store' in albumList: albumList.remove('.DS_Store')
        for album in albumList:
            self.albumDict[album] = None
        self.librarySize = len(self.albumDict)

    def updateAlbumDict(self, album, instance):
        self.albumDict[album] = instance

    def sortbyAlbum(self):
        count = 0
        for key in sorted(self.albumDict.keys()):
            count +=1
            self.albumSorted.append((count, key))

    def sortbyArtist(self):
        artistList = []
        count = 0
        for key in self.albumDict.keys():
            if self.albumDict[key].albumArtist is None: continue
            artistList.append((self.albumDict[key].albumArtist, key))
        for item in sorted(artistList, key=lambda tup: tup[0]):
            count +=1
            self.artistSorted.append((count, item[1]))

    def sortbyYear(self):
        yearList = []
        count = 0
        for key in self.albumDict.keys():
            if self.albumDict[key].albumYear is None: continue
            yearList.append((self.albumDict[key].albumYear, key))
        for item in sorted(yearList, key=lambda tup: tup[0]):
            count +=1
            self.yearSorted.append((count, item[1]))


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

MDsMusic.sortbyAlbum()
MDsMusic.sortbyArtist()
MDsMusic.sortbyYear()



waltz = Flask(__name__)

@waltz.route("/")
def main():
    session['currentPage'] = 1
    session['totalPages'] = MDsMusic.librarySize/20
    return render_template('newsite.html', song_list_sorted=MDsMusic.albumSorted[0:20], library_dict=MDsMusic.albumDict)

@waltz.route('/more')
def moreSongs():
    currentPage = session.get('currentPage', None)
    totalPages = session.get('totalPages', None)
    if currentPage <= totalPages:
        return render_template('newsite.html', song_list_sorted=MDsMusic.albumSorted[(currentPage*20):(currentPage*20+20)],
        library_dict=MDsMusic.albumDict)
        session['currentPage'] += 1
    else:
        return render_template('newsite.html', song_list_sorted=MDsMusic.albumSorted[(currentPage*20):(currentPage*20+20)],
        library_dict=MDsMusic.albumDict)

waltz.secret_key='notsecret'

@waltz.route('/artists')
def loadArtists():
    session['currentPage'] = 1
    session['totalPages'] = MDsMusic.librarySize/20
    return render_template('newsite.html', song_list_sorted=MDsMusic.artistSorted[0:20], library_dict=MDsMusic.albumDict)

@waltz.route('/moreartists')
def loadMoreArtists():
    currentPage = session.get('currentPage', None)
    totalPages = session.get('totalPages', None)
    return render_template('newsite.html', song_list_sorted=MDsMusic.artistSorted[(currentPage*20):(currentPage*20+20)], library_dict=MDsMusic.albumDict)

#@waltz.route('/year')
#def loadYear():

#    return render_template('newsite.html', song_list_sorted=, library_dict=MDsMusic.albumDict)

#@waltz.route('/moreyears')
#def loadMoreYear():

#    return render_template('newsite.html', song_list_sorted=, library_dict=MDsMusic.albumDict)

if __name__ == '__main__':
    waltz.run()
