from os import listdir
import random

root_path = r'\\NAS2021_4TB\music\Best of Hare Krishna Kirtans'

def ext(f):
    return f.split('.')[-1]

dirty_names = listdir(root_path)
file_names = []
for f in dirty_names:
    if ext(f) == 'mp3':
        file_names.append(f)
number_songs = len(file_names)

# print(file_names)

for playlist in range(1,21):
    playlist_name = f'krsna random playlist {playlist:0>2}.m3u'
    playlist_text = ""
    song_taken = set()
    for song in range(number_songs):
        rando = random.randint(0, number_songs-1)
        while rando in song_taken:
            rando = random.randint(0, number_songs-1)
        playlist_text += f'{file_names[rando]}\n'
        song_taken.add(rando)
    with open(root_path + '\\' + playlist_name, 'w') as g:
        g.write(playlist_text)