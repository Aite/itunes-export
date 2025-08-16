from libpytunes import Library
from libpytunes import Playlist
from pathlib import Path
import datetime
import os
import argparse

parser = argparse.ArgumentParser(description="An utility application to export iTunes playlists in m3u format.")
parser.add_argument("--output", "-o", help="The outpout folder for exporting the playlists.", required=True)
parser.add_argument("--ignore", help="Ignore a specific playlist.", action='append')
parser.add_argument("--xml", "-x", help="The path to the iTunes Library XML.", default=str(Path.home().joinpath("Music/Music/iTunes Music Library.xml")))
parser.add_argument("--library", "-l", help="The path to the iTunes Library Folder.", default=str(Path.home().joinpath("Music/Music/Media")))
parser.add_argument("--export-genius-playlists", action='store_true', dest='exportGeniusPlaylists')
parser.add_argument("--export-smart-playlists", action='store_true', dest='exportSmartPlaylists')
args = parser.parse_args()

libraryPath = args.library
xmlPath = args.xml
playlistRootPath = Path(args.output)
ignoreList= args.ignore if args.ignore is not None else []

def cleanupPlaylistName(playlistName):
        return playlistName.replace("/", "").replace("\\", "").replace(":", "")

def exportPlaylist(playlist: Playlist, parentPath: Path, libraryPath: Path):
        if(playlist.is_genius_playlist and not args.exportGeniusPlaylists):
                return

        if(playlist.is_smart_playlist and not args.exportSmartPlaylists):
                return

        if(playlist.is_folder):
                # Create Folder
                currentPath = parentPath.joinpath(playlist.name)
                if(not currentPath.exists()):
                        currentPath.mkdir()

                for childPlaylist in playlists.values():
                        if(childPlaylist.parent_persistent_id == playlist.persistent_id):
                                exportPlaylist(childPlaylist, currentPath)
        else:
                playlistContent = "#EXTM3U\n"
                for track in playlist.tracks:
                        if track.location != None:
                                try:
                                        if track.total_time is None:
                                                total_time = -1
                                        else:
                                                t = datetime.datetime.strptime(track.total_time, "%H:%M:%S.%f")  # With milliseconds
                                                td = datetime.timedelta(
                                                        hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond
                                                )
                                                total_time = round(td.total_seconds())

                                        title = track.name if track.name is not None else ""
                                        artist = track.artist if track.artist is not None else ""
                                        playlistContent += f"#EXTINF:{total_time},{title} - {artist}\n"

                                        # Use relative path if possible
                                        playlistContent +=  os.path.relpath(track.location, start=libraryPath) + "\n"
                                except ValueError:
                                        print("Warning: Could not add the track \"" + track.location + "\" as relative path to the playlist \"" + playlistName + "\"; added the track as absolute path instead.")
                                        playlistContent += track.location + "\n"

                playlistPath = parentPath.joinpath(cleanupPlaylistName(playlist.name) + ".m3u")
                playlistPath.write_text(playlistContent, encoding="utf8")

playlists = {}

library = Library(xmlPath)
for playlistName in library.getPlaylistNames(ignoreList=[
        "Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts", "Audiobooks", "Downloaded"
] + ignoreList):
    playlist = library.getPlaylist(playlistName)
    playlists[playlist.persistent_id] = playlist

for playlist in playlists.values(): 
    if(playlist.parent_persistent_id == None) :
        exportPlaylist(playlist, playlistRootPath, libraryPath)