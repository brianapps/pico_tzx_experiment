
import argparse
from tzxlib.tzxfile import TzxbBlock, TzxFile
from tzxlib.saver import TapeSaver

parser = argparse.ArgumentParser("TZX to pulses")
parser.add_argument('tzxfile')

args = parser.parse_args()

f = TzxFile()
s = TapeSaver()
f.read(args.tzxfile)

print(f"Blocks in TZX file {len(f.blocks)}")

def playback(tzxFile : TzxFile, saver : TapeSaver):
    # Play all blocks in order and assume we have simple TZX file that
    # doesn't have stop or jumps or any fancy features.
    b : TzxbBlock
    for b in tzxFile.blocks:
        yield from b.playback(saver)
        

edges = []
cur = 0
coalesce = True


for x in playback(f, s):
    if x == 0:
        coalesce =  not coalesce
    else:
        if coalesce:
            coalesce = False
            cur += x
        else:
            if cur != 0:
                # tzxtools gives pulse widths in ns -- convert them to tstates.
                edges.append(round(cur * 0.0035))
            coalesce = False
            cur = x
            
edges.append(round(cur * 0.0035))

pulse_widths = {}

for x in edges:
    c = pulse_widths.get(x)
    if c is None:
        pulse_widths[x] = len(pulse_widths)
        
width_to_index = {v: k for k, v in pulse_widths.items()}

if len(pulse_widths) > 255:
    raise Exception(
        f"Too many pulse widths {len(pulse_widths)} to encode in a byte")

with open('pulses.c', 'w') as fp:
    fp.write("const unsigned int WIDTHS[] = {\n")
    for i in range(len(pulse_widths)):
        fp.write(f"     {width_to_index[i]},\n")
    fp.write("};\n\n")
    fp.write("const unsigned char PULSES[] = {")
    for b in range(0, len(edges), 32):
        fp.write("\n    ")
        for e in edges[b: b + 32]:
            fp.write(f"0x{pulse_widths[e]:02X}, ")
    fp.write("\n};\n")
    fp.write("const unsigned int PULSES_LENGTH = sizeof(PULSES) / sizeof(PULSES[0]);\n")