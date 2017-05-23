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
        self.librarySize = len(self.albumDict)

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
        self.albumImage = None
        self.songList = []
        self.errorsFound = []

    def updateAlbumMetadata (self, album, musicLocation):
        trackList = os.listdir(os.path.join(musicLocation, album))
        for song in trackList:
            if '.jpg' in song: continue
            if '.log' in song: continue
            if '.DS_Store' in song: continue
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
            if self.albumImage is None and 'albumImage' not in self.errorsFound:
                try:
                    for item in songMetadata.pictures:
                        if 'jpeg' in item.mime:
                            artfilepath = os.path.join(musicLocation, album, "{}_album_art.jpg".format("".join(songMetadata['album'])))
                            albumartFile = open(artfilepath, 'wb')
                            albumartFile.write(item.data)
                            self.albumImage = artfilepath
                except:
                    self.errorsFound.append('Missing Album Image')

    def errorReporting(self):
        return self.errorsFound


def albumListSlicer(cP, numberofPages, totalAlbums):
    if cP > int(numberofPages[0]):
        beginSlice = 20*(cP - 1)
        endSlice = (0.1*int(numberofPages[2])*20) + beginSlice
        return (beginSlice, endSlice)
    else:
        return (20*cP, (20*cP)+20)



MDsMusic = musicLibrary('/usr/media')
MDsMusic.listAlbums()

for k in MDsMusic.albumDict.keys():
    MDsMusic.updateAlbumDict(k, album())
    MDsMusic.albumDict[k].updateAlbumMetadata(k, MDsMusic.musicLocation)

MDsMusic.sortbyAlbum()
MDsMusic.sortbyArtist()
MDsMusic.sortbyYear()



waltz = Flask(__name__)

waltz.secret_key='notsecret'

@waltz.route("/")
def main():
    session['currentPage'] = 0
    print(session['currentPage'])
    return render_template('newsite.html', song_list_sorted=MDsMusic.albumSorted[0:20],
    library_dict=MDsMusic.albumDict, previousButton='/', moreButton='/more_albums')

@waltz.route('/more_albums')
def moreAlbums():
    if session['currentPage'] < int(len(MDsMusic.albumSorted)/20):
        session['currentPage'] +=1
    slices = albumListSlicer(session['currentPage'], str(len(MDsMusic.albumSorted)/20), MDsMusic.librarySize)
    print(session['currentPage'])
    return render_template('newsite.html', song_list_sorted=MDsMusic.albumSorted[slices[0]:slices[1]],
    library_dict=MDsMusic.albumDict, previousButton='/previous_albums', moreButton='/more_albums')

@waltz.route('/previous_albums')
def previousAlbums():
    if session['currentPage'] > 0:
        session['currentPage'] -=1
    slices = albumListSlicer(session['currentPage'], str(len(MDsMusic.albumSorted)/20), MDsMusic.librarySize)
    print(session['currentPage'])
    return render_template('newsite.html', song_list_sorted=MDsMusic.albumSorted[slices[0]:slices[1]],
    library_dict=MDsMusic.albumDict, previousButton='/previous_albums', moreButton='/more_albums')


@waltz.route('/artists')
def loadArtists():
    session['currentPage'] = 0
    print(session['currentPage'])
    return render_template('newsite.html', song_list_sorted=MDsMusic.artistSorted[0:20],
    library_dict=MDsMusic.albumDict, previousButton='/previous_artists', moreButton='/more_artists')

@waltz.route('/more_artists')
def moreArtists():
    if session['currentPage'] < int(len(MDsMusic.artistSorted)/20):
        session['currentPage'] +=1
    slices = albumListSlicer(session['currentPage'], str(len(MDsMusic.artistSorted)/20), MDsMusic.librarySize)
    print(session['currentPage'])
    return render_template('newsite.html', song_list_sorted=MDsMusic.artistSorted[slices[0]:slices[1]],
    library_dict=MDsMusic.albumDict, previousButton='/previous_artists', moreButton='/more_artists')

@waltz.route('/previous_artists')
def previousArtists():
    if session['currentPage'] > 0:
        session['currentPage'] -=1
    slices = albumListSlicer(session['currentPage'], str(len(MDsMusic.artistSorted)/20), MDsMusic.librarySize)
    print(session['currentPage'])
    return render_template('newsite.html', song_list_sorted=MDsMusic.artistSorted[slices[0]:slices[1]],
    library_dict=MDsMusic.albumDict, previousButton='/previous_artists', moreButton='/more_artists')


@waltz.route('/years')
def loadYears():
    session['currentPage'] = 0
    print(session['currentPage'])
    return render_template('newsite.html', song_list_sorted=MDsMusic.yearSorted[0:20],
    library_dict=MDsMusic.albumDict, previousButton='/previous_years', moreButton='/more_years')

@waltz.route('/more_years')
def moreYears():
    if session['currentPage'] < int(len(MDsMusic.yearSorted)/20):
        session['currentPage'] +=1
    print(session['currentPage'])
    slices = albumListSlicer(session['currentPage'], str(len(MDsMusic.yearSorted)/20), MDsMusic.librarySize)
    return render_template('newsite.html', song_list_sorted=MDsMusic.yearSorted[slices[0]:slices[1]],
    library_dict=MDsMusic.albumDict, previousButton='/previous_years', moreButton='/more_years')

@waltz.route('/previous_years')
def previousYears():
    if session['currentPage'] > 0:
        session['currentPage'] -=1
    print(session['currentPage'])
    slices = albumListSlicer(session['currentPage'], str(len(MDsMusic.yearSorted)/20), MDsMusic.librarySize)
    return render_template('newsite.html', song_list_sorted=MDsMusic.yearSorted[slices[0]:slices[1]],
    library_dict=MDsMusic.albumDict, previousButton='/previous_years', moreButton='/more_years')

if __name__ == '__main__':
    waltz.run()
