from flask import Flask, render_template, session
import datetime
import mutagen
import os
import logging


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
            self.update_album_dict(key, Album())
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


class Album:
    def __init__(self):
        self.title = None
        self.year = None
        self.genre = None
        self.artist = None
        self.image = None
        self.song_list = []
        self.errors_found = []

    def update_metadata(self, album, music_location):
        track_list = os.listdir(os.path.join(music_location, album))

        # remove items that are not songs from the track_list
        track_list = [x for x in track_list for y in ['.jpg', '.log', '.DS_Store'] if y not in x]

        for song in track_list:
            song_metadata = mutagen.File(os.path.join(music_location, album, song))

            # It looks like you're assuming the metadata will be the same for all the tracks in an album.
            # Since self.errors_found isn't reset between tracks, if there's an error finding the title metadata for
            # track 2, it wont even attempt to retrieve the title metadata for the rest of the tracks (for example)
            if self.title is None and 'albumTitle' not in self.errors_found:
                try:
                    self.title = "".join(song_metadata['album'])
                except Exception as msg:
                    logging.exception(msg)
                    self.errors_found.append('albumTitle')
            if self.year is None and 'year' not in self.errors_found:
                try:
                    self.year = "".join(song_metadata['date'])
                except Exception as msg:
                    logging.exception(msg)
                    self.errors_found.append('year')

            if self.genre is None and 'genre' not in self.errors_found:
                try:
                    self.genre = "".join(song_metadata['genre'])
                except Exception as msg:
                    logging.exception(msg)
                    self.errors_found.append('genre')

            if self.artist is None and 'artist' not in self.errors_found:
                try:
                    self.artist = "".join(song_metadata['artist'])
                except Exception as msg:
                    logging.exception(msg)
                    self.errors_found.append('artist')
            try:
                self.song_list.append((int("".join(song_metadata['tracknumber'])), song))
            except Exception as msg:
                logging.exception(msg)
                self.errors_found.append('Missing Track Number')
                self.song_list.append(song)

            if self.image is None and 'image' not in self.errors_found:
                try:
                    for item in song_metadata.pictures:
                        if 'jpeg' in item.mime:
                            art_file_path = os.path.join(
                                music_location,
                                album,
                                "{}_album_art.jpg".format("".join(song_metadata['album']))
                            )

                            album_art_file = open(art_file_path, 'wb')
                            album_art_file.write(item.data)
                            self.image = art_file_path
                except Exception as msg:
                    logging.exception(msg)
                    self.errors_found.append('Missing Album Image')

    def error_reporting(self):
        return self.errors_found


def album_list_slicer(cP, number_of_pages, total_albums):
    if cP > int(number_of_pages[0]):
        begin_slice = 20*(cP - 1)
        end_slice = (0.1 * int(number_of_pages[2]) * 20) + begin_slice
        return begin_slice, end_slice
    else:
        return 20*cP, (20*cP)+20

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
    slices = album_list_slicer(session['currentPage'], str(len(player.album_sorted) / 20), player.library_size)
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
    slices = album_list_slicer(session['currentPage'], str(len(player.album_sorted) / 20), player.library_size)
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
    slices = album_list_slicer(session['currentPage'], str(len(player.artist_sorted) / 20), player.library_size)
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
    slices = album_list_slicer(session['currentPage'], str(len(player.artist_sorted) / 20), player.library_size)
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
    slices = album_list_slicer(session['currentPage'], str(len(player.year_sorted) / 20), player.library_size)

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
    slices = album_list_slicer(session['currentPage'], str(len(player.year_sorted) / 20), player.library_size)

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
