from flask import Flask, render_template, session
import datetime
import os
import logging
from libs import albums


class MusicLibrary:
    def __init__(self, music_location):
        logging.basicConfig(filename='{}.log'.format(datetime.date.today()),
                            format="[%(levelname)8s] %(message)s",
                            level=logging.DEBUG
                            )
        self.album_dict = {}
        self.music_location = music_location
        self.album_sorted = []
        self.artist_sorted = []
        self.year_sorted = []
        self.library_size = len(self.album_dict)

    def main(self):
        self.list_albums()

        for key in self.album_dict.keys():
            self.update_album_dict(key, albums.Album())
            self.album_dict[key].update_metadata(key, self.music_location)

        self.sort_by_album()
        self.sort_by_artist()
        self.sort_by_year()

    def list_albums(self):
        album_list = os.listdir(self.music_location)
        if '.DS_Store' in album_list:
            album_list.remove('.DS_Store')
        for album in album_list:
            self.album_dict[album] = {}
        self.library_size = len(self.album_dict)

    def update_album_dict(self, album, instance):
        self.album_dict[album] = instance

    def sort_by_album(self):
        count = 0
        for album in sorted(self.album_dict.keys()):
            count += 1
            self.album_sorted.append((count, album))

    def sort_by_artist(self):
        artist_list = []
        count = 0
        for album in self.album_dict.keys():
            if self.album_dict[album].artist is None:
                continue
            artist_list.append((self.album_dict[album].artist, album))
        for item in sorted(artist_list, key=lambda tup: tup[0]):
            count += 1
            self.artist_sorted.append((count, item[1]))

    def sort_by_year(self):
        year_list = []
        count = 0
        for album in self.album_dict.keys():
            if self.album_dict[album].year is None:
                continue
            year_list.append((self.album_dict[album].year, album))
        for item in sorted(year_list, key=lambda tup: tup[0]):
            count += 1
            self.year_sorted.append((count, item[1]))


waltz = Flask(__name__)
waltz.secret_key = 'notsecret'


@waltz.route("/")
def home():
    session['currentPage'] = 0
    print(session['currentPage'])
    return render_template(
        'newsite.html',
        song_list_sorted=player.album_sorted[0:20],
        library_dict=player.album_dict,
        previousButton='/',
        moreButton='/more_albums'
    )


@waltz.route('/more_albums')
def more_albums():
    if session['currentPage'] < int(len(player.album_sorted) / 20):
        session['currentPage'] += 1
    slices = albums.list_slicer(session['currentPage'], str(len(player.album_sorted) / 20), player.library_size)
    print(session['currentPage'])

    return render_template(
        'newsite.html',
        song_list_sorted=player.album_sorted[slices[0]:slices[1]],
        library_dict=player.album_dict,
        previousButton='/previous_albums',
        moreButton='/more_albums'
    )


@waltz.route('/previous_albums')
def previous_album():
    if session['currentPage'] > 0:
        session['currentPage'] -= 1
    slices = albums.list_slicer(session['currentPage'], str(len(player.album_sorted) / 20), player.library_size)
    print(session['currentPage'])

    return render_template(
        'newsite.html',
        song_list_sorted=player.album_sorted[slices[0]:slices[1]],
        library_dict=player.album_dict,
        previousButton='/previous_albums',
        moreButton='/more_albums'
    )


@waltz.route('/artists')
def load_artists():
    session['currentPage'] = 0
    print(session['currentPage'])

    return render_template(
        'newsite.html',
        song_list_sorted=player.artist_sorted[0:20],
        library_dict=player.album_dict,
        previousButton='/previous_artists',
        moreButton='/more_artists'
    )


@waltz.route('/more_artists')
def more_artists():
    if session['currentPage'] < int(len(player.artist_sorted) / 20):
        session['currentPage'] += 1
    slices = albums.list_slicer(session['currentPage'], str(len(player.artist_sorted) / 20), player.library_size)
    print(session['currentPage'])

    return render_template(
        'newsite.html',
        song_list_sorted=player.artist_sorted[slices[0]:slices[1]],
        library_dict=player.album_dict,
        previousButton='/previous_artists',
        moreButton='/more_artists'
    )


@waltz.route('/previous_artists')
def previous_artists():
    if session['currentPage'] > 0:
        session['currentPage'] -= 1
    slices = albums.list_slicer(session['currentPage'], str(len(player.artist_sorted) / 20), player.library_size)
    print(session['currentPage'])

    return render_template(
        'newsite.html',
        song_list_sorted=player.artist_sorted[slices[0]:slices[1]],
        library_dict=player.album_dict,
        previousButton='/previous_artists',
        moreButton='/more_artists'
    )


@waltz.route('/years')
def load_years():
    session['currentPage'] = 0
    print(session['currentPage'])

    return render_template(
        'newsite.html',
        song_list_sorted=player.year_sorted[0:20],
        library_dict=player.album_dict,
        previousButton='/previous_years',
        moreButton='/more_years'
    )


@waltz.route('/more_years')
def more_years():
    if session['currentPage'] < int(len(player.year_sorted) / 20):
        session['currentPage'] += 1
    print(session['currentPage'])
    slices = albums.list_slicer(session['currentPage'], str(len(player.year_sorted) / 20), player.library_size)

    return render_template(
        'newsite.html',
        song_list_sorted=player.year_sorted[slices[0]:slices[1]],
        library_dict=player.album_dict,
        previousButton='/previous_years',
        moreButton='/more_years'
    )


@waltz.route('/previous_years')
def previous_years():
    if session['currentPage'] > 0:
        session['currentPage'] -= 1
    print(session['currentPage'])
    slices = albums.list_slicer(session['currentPage'], str(len(player.year_sorted) / 20), player.library_size)

    return render_template(
        'newsite.html',
        song_list_sorted=player.year_sorted[slices[0]:slices[1]],
        library_dict=player.album_dict,
        previousButton='/previous_years',
        moreButton='/more_years'
    )

if __name__ == '__main__':
    player = MusicLibrary('/home/shawn/Music')
    player.main()
    waltz.run()
