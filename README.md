# osu! beatmaps to glyph converter
___
<p>This repository contains scripts that allow you to convert osu! beatmaps to label files, which in turn can be converted to ringtones for Nothing Phone.</p>

## What is osu?
___
osu! - is a rhythm game where you click on circles to the music. All the songs for osu! are called beatmaps. Bitmaps store data about at what point in time, and where the circle is located. There's also beatmapsets. They are distributed as zip archives, they contain a song and some beatmaps.

## Usage
___

- Web version
You can use the web version of this project: https://taiixu.com/osu

- Clone the repo
```
git clone https://github.com/taiixu/osu-to-glyph
cd osu-to-glyph
```

- Download some osu! beatmapset
You can download beatmapsets on this page: https://osu.ppy.sh/beatmapsets?m=0 (registration needed)

- Convert beatmapset to label.txt
<b>Get the maps that are in beatmapset.</b>
```
python3 GlyphV1.py --osz /path/to/osz/file
```

<b>Convert beatmapset</b>
```
python3 GlyphV1.py --osz /path/to/osz/file -n 1 -o /output/path/to/label.txt
```
In the `-n` argument specify the number of the bitmap you want to convert.

<b>Convert beatmapset with audio extraction</b>
```
python3 GlyphV1.py --osz /path/to/osz/file -n 1 -o /path/to/label.txt -a
```

<b>If you want the glyphs to switch faster</b>
```
python3 GlyphV1.py --osz /path/to/osz/file -n 1 -o /path/to/label.txt -s 28
```
The higher the value of `-s` argument, the faster the glyphs are switched

##Difference between GlyphV1 and GlyphV2

- GlyphV1
With GlyphV1 you can only make ringtones for Nothing Phone 1.
GlyphV1 displays circles on the first two glyphs ( on top), and sliders on the bottom three glyphs.

Here's an example of what it looks like: 
https://github.com/taiixu/osu-to-glyph/assets/156664940/6ecd5c99-b6d5-4fef-8e0b-48d7f18f4097
<p>Map: https://osu.ppy.sh/beatmapsets/647105#osu/1370878</p>

- GlyphV2
GlyphV2 can make ringtones for Nothing Phone 1 and Nothing Phone 2.
This version of the script breaks the map into tacts, and depending on the number of objects in a tact, uses patterns (which you can find at the path: utils/glypheffets.py).
Also new arguments have been added to this script:
`--np2` or `-2` - creates a label file for Nothing Phone 2
`--seed` or `-e` - Sets seed

Here's an example of what it looks like on NP1: 
https://github.com/taiixu/osu-to-glyph/assets/156664940/f531832e-797e-4d08-b74e-d4f088f6a85a
<p>Map: https://osu.ppy.sh/beatmapsets/1742920#osu/3617161</p>

Example, how it looks on NP2:
https://github.com/taiixu/osu-to-glyph/assets/156664940/12754988-3730-4d44-8836-a32c45d6f43c
<p>Map: https://osu.ppy.sh/beatmapsets/1614335#osu/4556061</p>

## What to do with label.txt
You can use [custom-nothing-glyph-tools](https://github.com/SebiAi/custom-nothing-glyph-tools) by [SebiAi](https://github.com/SebiAi)
Or use the web version: https://taiixu/tools

- Clone the repo
```
git clone https://github.com/SebiAi/custom-nothing-glyph-tools.git
cd custom-nothing-glyph-tools
```

- Install dependencies
```
pip3 install -r requirements.txt
```

- Make a ringtone!
```
python3 GlyphTranslator.py /path/to/label.txt
python3 GlyphModder.py -w /path/to/label.glypha /path/to/label.glyphc1 /path/to/audio.ogg
```

Read [README.md](https://github.com/SebiAi/custom-nothing-glyph-tools/blob/main/README.md) of this project if you encounter any problems
