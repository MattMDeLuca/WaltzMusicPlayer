import os
import logging
import mutagen


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


def list_slicer(cP, number_of_pages, total_albums):
    if cP > int(number_of_pages[0]):
        begin_slice = 20*(cP - 1)
        end_slice = (0.1 * int(number_of_pages[2]) * 20) + begin_slice
        return begin_slice, end_slice
    else:
        return 20*cP, (20*cP) + 20
