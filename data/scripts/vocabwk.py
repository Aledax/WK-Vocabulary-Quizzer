import requests, vlc

# Vocabulary class
class Item:
    def __init__(self, id: int, kanji: str, readings: list, meanings: list, audio_url: str):
        self.id = id
        self.data = {
            'Kanji': kanji,
            'Readings': readings,
            'Meanings': meanings
        }
        self.audio_url = audio_url

    def info(self, components):
        lines = []
        if 'kanji' in components: lines.append(f"Kanji: {self.data['kanji']}")
        if 'readings' in components: lines.append(f"Readings: {' / '.join(self.data['readings'])}")
        if 'meanings' in components: lines.append(f"Meanings: {' / '.join(self.data['meanings'])}")
        return '\n'.join(lines)

    def sound(self):
        if not self.audio_url: return vlc.MediaPlayer()
        return vlc.MediaPlayer(self.audio_url)

TOKEN = ''
BASE = 'https://api.wanikani.com/v2/'
HEADERS = {'Authorization': 'Bearer ' + TOKEN}

def json_to_obj(json):
    id = json['id']
    data = json['data']
    kanji = data['characters']
    readings = [reading['reading'] for reading in sorted(data['readings'], key=lambda reading: reading['primary'], reverse=True)]
    meanings = [meaning['meaning'] for meaning in sorted(data['meanings'], key=lambda meaning: meaning['primary'], reverse=True)]
    audio_url = None if ('pronunciation_audios' not in data or data['pronunciation_audios'] == []) else data['pronunciation_audios'][0]['url']

    return Item(id, kanji, readings, meanings, audio_url)

def extract(type, levels):
    vocabulary = []
    for level in levels:
        resource_path = 'subjects'
        params = {'types': [type], 'levels': [level]}
        response = requests.get(BASE + resource_path, params=params, headers=HEADERS).json()
        data = response['data']
        vocabulary += [json_to_obj(v) for v in data]
    return vocabulary