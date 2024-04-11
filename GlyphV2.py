from utils import osuparser
from utils.glypheffects import effects_np1, effects_np2
from math import ceil
import random
import argparse
import sys

def bin8(i):
    return (('0' * (8 - len(bin(i).split('b')[1]))) + bin(i).split('b')[1])[::-1]


def ms_to_bpm(x):
    return 1 / x * 1000 * 60


def get_timing_points(map):
    bpm_timing = [[]]
    sm_timing = []
    for c in map.sectors['TimingPoints']:
        if c[1][0] == '-':
            sm_timing.append([float(c[0]) / 1000, float(c[1][1:])])
        else:
            bpm_timing.append([float(c[0]) / 1000, float(c[1]), int(c[2])])
    bpm_timing[0] = [0, bpm_timing[1][1], bpm_timing[1][2]]
    return bpm_timing, sm_timing


def bpm_list(map, bpm_timing, sm_timing, note_size, sm):
    ranges = []
    o = bin8(int(map.sectors['HitObjects'][-1][3]))
    time = int(map.sectors['HitObjects'][-1][2]) / 1000
    if o[0] == '1':
        last_time = time + (1 / float(map.sectors['HitObjects'][-1][2]) * 1000 / note_size)
    elif o[1] == '1':
        sv = sm_timing[-1][1]
        last_time = time + (int(float(map.sectors['HitObjects'][-1][7]) / (sm * 100 * (1 / sv + 1)) * int(map.sectors['HitObjects'][-1][2])) / 1000)
    elif o[3] == '1':
        last_time = time + int(map.sectors['HitObjects'][-1][5]) / 1000

    for c in range(len(bpm_timing)):
        bpm = bpm_timing[c]
        try:
            next_time = bpm_timing[c + 1][0]
        except:
            next_time = last_time
        ranges.append([bpm[0], next_time, bpm[1]])
    
    ret = []
    last_object = 0
    for timing in ranges:
        ret.append(f"bpm,{timing[0]},{timing[2]}")
        for c in range(last_object, len(map.sectors['HitObjects'])):
            object = map.sectors['HitObjects'][c]
            if timing[0] <= int(object[2]) / 1000 and timing[1] >= int(object[2]) / 1000:
                type_of_object = bin8(int(object[3]))
                time = int(object[2]) / 1000
                sv = 1
                for d in sm_timing[::-1]:
                    if time >= d[0]:
                        sv = d[1]
                        break
                type_o = ''
                if type_of_object[0] == '1': # Circle
                    end_time = time + (1 / timing[2] * 1000 / note_size)
                    type_o = 'circle'
                elif type_of_object[1] == '1': # Slider
                    type_o = 'slider'
                    slides = int(object[6])
                    sl_end_time = (int(float(object[7]) / (sm * 100 * (1 / sv + 1)) * timing[2]) / 1000) / slides
                    sl_time = time
                    for c in range(1, slides + 1):
                         end_time = sl_time + sl_end_time * c
                         ret.append(f"object,{type_o},{time},{end_time}")
                         sl_time = end_time
                    continue
                elif type_of_object[3] == '1': # Spinner
                    end_time = int(object[5]) / 1000
                    type_o = 'spinner'
                ret.append(f"object,{type_o},{time},{end_time}")
            else:
                last_object = c
                break
    return ret, ranges


def split_to_bars(m, ranges):
    ret = []
    start_time = 0
    bpm = 0
    bar = []
    for c in ranges:
        for d in range(ceil((c[1] - c[0]) / (c[2] / 1000))):
            ret.append([])
    
    for c in m:
        object = c.split(',')
        if c.split(',')[0] == 'bpm':
            start_time = float(c.split(',')[1])
            bpm = float(c.split(',')[2])
            continue
        try:
            ret[ceil((float(object[2]) * 1000 - start_time) / bpm)].append(c)
        except:
            pass
        
    for c in range(len(ret) -1, -1, -1):
        if len(ret[c]) == 0:
            del ret[c]
        else:
            break

    return ret


def generate_effect(length, mode):
    if mode == 'np1':
        m_eff = [c for c in effects_np1][-1]
        eff = effects_np1
    else:
        m_eff = [c for c in effects_np2][-1]
        eff = effects_np2
    
    ret_ = []
    l = length
    while l != 0:
        random_value = random.randint(1, l) if l < m_eff else random.randint(1, m_eff)
        ret_.append(random_value)
        l -= random_value
    
    ret = []
    for c in ret_:
        random_effect = random.choice(eff[c])
        for d in random_effect:
            ret.append(d)
    return ret



def bars_to_glyph(bars, mode):
    ret = []
    for c in bars:
        if c == []:
            continue
        try:
            if mode == 'np1':
                eff = random.choice(effects_np1[len(c)])
            else:
                eff = random.choice(effects_np2[len(c)])
        except:
            eff = generate_effect(len(c), mode)

        for o_bar in zip(c, eff):
            start_time = float(o_bar[0].split(',')[2])
            end_time = float(o_bar[0].split(',')[3])
            for x in o_bar[1]:
                ret.append(f"{start_time}\t{end_time}\t{x}-100-100")
    ret.append(f"{end_time + 0.1}\t{end_time + 0.1}\tEND")
    return ret


def get_args():
    parser = argparse.ArgumentParser(description='Converts osu! beatmaps or beatmapsets to label file for custom nothing glyph tools\nThis is a second version of osu to glyph converter')
    parser.add_argument('--osz', help='Path to the osz file', type=str, metavar='osz_file')
    parser.add_argument('--osu', help='Path to the osu file', type=str, metavar='osu_file')
    parser.add_argument('--output', '-o', help='Output file', type=str, metavar='out_file')
    parser.add_argument('--number', '-n', help='Select a map. (Only uses with the --osz argument) To find out the map numbering, enter the command with the --osz argument without the --number argument.', type=int)
    parser.add_argument('--audio', '-a', help='Extract audio file from osz', action='store_true')
    parser.add_argument('--note-size', '-s', help='The higher the value, the faster the glyphs are switched (Default: 24)', type=int, default=24)
    parser.add_argument('--seed', '-e', help='Sets seed (Default seed: 1234)', type=int, default=1234)
    parser.add_argument('--np2', '-2', help='Sets Nothing Phone (2) mode', action='store_true')

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


def map_to_label(map, note_size, seed, mode):
    random.seed(seed)
    sm = float(map.sectors['Difficulty']['SliderMultiplier'])
    bpm_timing, sm_timing = get_timing_points(map)
    l, ranges = bpm_list(map, bpm_timing, sm_timing, note_size, sm)
    bars = split_to_bars(l, ranges)
    ret = bars_to_glyph(bars, mode)
    return ret

def main():
    args = get_args()
    map = get_map(args)
    mode = 'np2' if args.np2 else 'np1'
    label = map_to_label(map, args.note_size, args.seed, mode)
    if args.output == None:
        print("Error: specify the --output argument")
        return
    else:
        open(args.output, 'w', encoding='utf-8').write('\n'.join(label) + '\n')
        print(f'Wrote {len(label)} lines')

if __name__ == "__main__":
    main()