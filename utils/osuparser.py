import zipfile

DICT_WITH_SPACE = ['General', 'Editor']
DICT_WITHOUT_SPACE = ['Metadata', 'Difficulty']
LIST = ['Events', 'TimingPoints', 'HitObjects']
DICT_WITH_2_SPACES = ['Colours']

class BeatMap:
    def __init__(self, filename=None, file=None):
        # self.file = file if file != None else open(filename, 'r', encoding='utf-8').read()
        if filename:
            self.file = open(filename, 'r', encoding='utf-8').read()
        elif file:
            self.file = file.replace('\r\n', '\n')
        # self.file = open(filename, 'r', encoding='utf-8').read()
        self.version = ''
        self.sectors = None

    def __clear_spaces(self, l):
        ret = []
        for c in l:
            if c == '':
                continue
            ret.append(c)
        return ret

    def get_sectors(self):
        ret = {}
        self.version = self.file.split('\n')[0]
        for c in self.file.split('[')[1:]:
            main_key = c.split('\n')[0][:-1]
            r_dict = {}
            r_list = []
            for d in self.__clear_spaces(c.split('\n')[1:]):
                if d[:2] == '//':
                    continue
                if main_key in LIST:
                    r_list.append(d.split(','))
                else:
                    r_dict.update({d.split(':')[0].strip(): d.split(':', maxsplit=1)[1].strip()})
            if main_key in DICT_WITH_SPACE or main_key in DICT_WITHOUT_SPACE or main_key in DICT_WITH_2_SPACES:
                ret.update({main_key: r_dict})
            elif main_key in LIST:
                ret.update({main_key: r_list})
        
        self.sectors = ret
    
    def get_metadata(self):
        metadata = self.sectors['Metadata']
        objects = self.sectors['HitObjects']
        return {
            'title': metadata['Title'],
            'artist': metadata['Artist'],
            'version': metadata['Version'],
            'creator': metadata['Creator'],
            'objects_count': len(objects)
        }

class BeatMapSet:
    def __init__(self, filename):
        self.file = zipfile.ZipFile(filename, 'r')
        self.beatmaps = []
        self.map_names = []
        for c in self.file.namelist():
            if c.split('.')[-1] == 'osu':
                map = BeatMap(file=self.file.read(c).decode('utf-8'))
                map.get_sectors()
                self.beatmaps.append(map)
                self.map_names.append(c.removesuffix('.osu'))
    
    def get_audio(self, map):
        audio_name = map.sectors['General']['AudioFilename']
        a = self.file.read(audio_name)
        open(audio_name, 'wb').write(a)
        return audio_name

