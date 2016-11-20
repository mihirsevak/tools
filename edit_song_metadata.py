from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TRCK, TALB, USLT, error
import subprocess
# ID3 info:
# APIC: picture
# TIT2: title
# TPE1: artist
# TRCK: track number
# TALB: album
# USLT: lyric
def id3_cook(directory, filename, item, track_num):
    pic_file = directory + '/cover.jpg' # pic file
    audio = MP3(filename, ID3=ID3)
    try:
        audio.add_tags()
    except:
        pass
    audio.tags.add(APIC(
        encoding=3,
        mime='image/jpeg',
        type=3,
        desc=u'Cover Picture',
        data=open(pic_file).read()
    ))
    audio.tags.add(TIT2(encoding=3, text=item['song'].decode('utf-8')))
    audio.tags.add(TALB(encoding=3, text=item['album'].decode('utf-8')))
    audio.tags.add(TPE1(encoding=3, text=item['artist'].decode('utf-8')))
    audio.tags.add(TRCK(encoding=3, text=str(track_num).decode('utf-8')))
    audio.tags.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=item['lyric'].decode('utf-8')))
    audio.save()


item = {'song': 'temp.mp3', 'album':'unknown', 'artist':'Lata Mangeshkar', 'lyric':'unknown'}

list_of_files=subprocess.Popen(['ls *.mp3'], shell=True, stdout=subprocess.PIPE)
while True:
    filename=list_of_files.stdout.readline()[:-1]
    if filename != '' :
        print filename
    else:
        break

    item['song'] = filename
    id3_cook('.',filename,item,5)
