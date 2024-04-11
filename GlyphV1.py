from utils import osuparser
import sys
import argparse


def get_map_meta(map):
    metadata = map.sectors['Metadata']
    objects = map.sectors['HitObjects']
    return {
        'title': metadata['Title'],
        'artist': metadata['Artist'],
        'version': metadata['Version'],
        'creator': metadata['Creator'],
        'objects_count': len(objects)
    }


def bin8(i):
    return (('0' * (8 - len(bin(i).split('b')[1]))) + bin(i).split('b')[1])[::-1]


def get_args():
    parser = argparse.ArgumentParser(description='Converts osu! beatmaps or beatmapsets to label file for custom nothing glyph tools\nThis is a first version of osu to glyph converter')
    parser.add_argument('--osz', help='Path to the osz file', type=str, metavar='osz_file')
    parser.add_argument('--osu', help='Path to the osu file', type=str, metavar='osu_file')
    parser.add_argument('--output', '-o', help='Output file', type=str, metavar='out_file')
    parser.add_argument('--number', '-n', help='Select a map. (Only uses with the --osz argument) To find out the map numbering, enter the command with the --osz argument without the --number argument.', type=int)
    parser.add_argument('--audio', '-a', help='Extract audio file from osz', action='store_true')
    parser.add_argument('--note-size', '-s', help='The higher the value, the faster the glyphs are switched (Default: 24)', type=int, default=24)

    args = parser.parse_args()
    return args


def get_map(args):
    if args.osz and args.number == None:
        map = osuparser.BeatMapSet(args.osz)
        for c in range(len(map.beatmaps)):
            meta = map.beatmaps[c].get_metadata()
            print(f"{c + 1}. {meta['artist']} - {meta['title']} [{meta['version']} | by {meta['creator']}] ({meta['objects_count']} objects)")
        sys.exit()
    elif args.osz and args.number:
        beatmapset = osuparser.BeatMapSet(args.osz)
        map = beatmapset.beatmaps[args.number - 1]
        if args.audio:
            audio_name = beatmapset.get_audio(map)
            print(f"Audio Extracted. Filename: {audio_name}")
        meta = map.get_metadata()
        print(f"Map selected: {meta['artist']} - {meta['title']} [{meta['version']} | by {meta['creator']}] ({meta['objects_count']} objects)")
    elif args.osu:
        map = osuparser.BeatMap(args.osu)
        map.get_sectors()
        meta = map.get_metadata()
        print(f"Map selected: {meta['artist']} - {meta['title']} [{meta['version']} | by {meta['creator']}] ({meta['objects_count']} objects)")
    return map


def map_to_label(map, note_size):
    ret = []

    sm = float(map.sectors['Difficulty']['SliderMultiplier'])
    bpm_timing = [[0, 60, 4]]
    sm_timing = []
    for c in map.sectors['TimingPoints']:
        if c[1][0] == '-':
            sm_timing.append([float(c[0]) / 1000, float(c[1][1:])])
        else:
            bpm_timing.append([float(c[0]) / 1000, float(c[1])])
    
    for c in range(len(map.sectors['HitObjects'])):
        object = map.sectors['HitObjects'][c]
        try:
            next_c = int(map.sectors['HitObjects'][c + 1][2]) / 1000
        except:
            next_c = 1
        time = int(object[2]) / 1000
        sv = 1
        beatLength = 60
        for d in bpm_timing[::-1]:
            if time >= d[0]:
                beatLength = d[1]
                break
        
        for d in sm_timing[::-1]:
            if time >= d[0]:
                sv = d[1]
                break

        type_of_object = bin8(int(object[3]))
        if type_of_object[0] == '1': # Circle
            end_time = time + (1 / beatLength * 1000 / note_size)
            glyph_id = c % 2 + 1
            ret.append(f"{time}\t{end_time}\t{glyph_id}-100-100")
        elif type_of_object[1] == '1': # Slider
            end_time = time + (int(float(object[7]) / (sm * 100 * (1 / sv + 1)) * beatLength) / 1000)
            glyph_id = c % 3 + 1
            ret.append(f"{time}\t{end_time}\t{2 + glyph_id}-100-100")
        elif type_of_object[3] == '1': # Spinner
            end_time = int(object[5]) / 1000
            ret.append(f"{time}\t{end_time}\t1-100-0-LOG")
            ret.append(f"{time}\t{end_time}\t2-100-0-LOG")
            ret.append(f"{time}\t{end_time}\t3-100-0-LOG")
            ret.append(f"{time}\t{end_time}\t4-100-0-LOG")
            ret.append(f"{time}\t{end_time}\t5-100-0-LOG")
    ret.append(f"{end_time + 0.01}\t{end_time + 0.01}\tEND")
    return ret
    
def main():
    args = get_args()
    map = get_map(args)
    label = map_to_label(map, args.note_size)
    if args.output == None:
        print("Error: specify the --output argument")
        return
    else:
        open(args.output, 'w', encoding='utf-8').write('\n'.join(label) + '\n')
        print(f'Wrote {len(label)} lines')

if __name__ == "__main__":
    main()