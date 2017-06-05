import os
import math
import argparse
import subprocess
from time import sleep

parser = argparse.ArgumentParser()

## opciones del usuario

parser.add_argument("-f", "--folder", help="Folder with vv")
parser.add_argument("-n", "--number", help="limit to n viewer")
parser.add_argument("-r", "--reverse", help="reverse order",action='store_true')

parser.add_argument("-a", "--allscreen", help="fill all screen",action='store_true')
parser.add_argument("-o", "--only_resize", help="only resize",action='store_true')
args = parser.parse_args()

if(args.folder):
        folder = args.folder
else:
        folder = "./"

cmd = ['xrandr']
cmd2 = ['grep', '*']
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
p.stdout.close()
 
resolution_string, junk = p2.communicate()
resolution_string = str(resolution_string, 'utf-8')
resolution = resolution_string.split()[0]
print(resolution)
width, height = resolution.split('x')

w = int(width)
h = int(height)

files_vv = [y for y in os.listdir(folder) if y.find('.vv') >= 0]
files = [f for f in files_vv if os.stat(folder + '/' + f).st_size > 0]
files.sort()
if(args.reverse):
    files.sort(reverse=True)

if(args.number):
    files=files[0:int(args.number)]

total_files=len(files)
#folder="/home/darta/vv/"



for file in files:
    if file.endswith(".vv"):
        tmpfile=''
        with open(folder + '/' + file,"r+") as f:
            lines = f.readlines()
            for l in lines:
                if 'title=' in l:
                    l="\ttitle="+file.split('.')[0]+'\n'
                if 'fullscreen=1' in l:
                    l="\tfullscreen=0\n"
                if 'delete-this-file=1' in l:
                    l="\tdelete-this-file=0\n"
                tmpfile=tmpfile+l
            f.seek(0)
            f.write(tmpfile)
            f.truncate()
            f.close()

if args.only_resize == False:
    for file in files:
        subprocess.Popen(["remote-viewer", "-z", "10", "-k", folder+'/'+file])
    if args.allscreen:
        sleep(5)

x=1
y=0
up_offset=0
down_offset=150

y = y + up_offset
h = h - up_offset + down_offset

if(args.allscreen):

    num_rows=int(math.sqrt(total_files-0.001))+1
    num_cols=num_rows
    x_diff = w / num_rows
    y_diff = h / num_cols
    i=0
    for file in files:
        x=str(int((i%num_cols)*x_diff))
        y=str(int(int(i/num_rows)*y_diff))
        weight = x_diff
        height = h / (num_cols + 1)
        cmd = "wmctrl -r {} -e 0,{},{},{},{}".format(
                file.split('.')[0],
                x,
                y,
                int(weight),
                int(height))
        print(cmd)
        i=i+1
        subprocess.call(cmd,shell=True)
                #x=x+x_diff
                #y=y+y_diff

else:
    for file in files:
        subprocess.Popen(["wmctrl","-r",'"'+file.split('.')[0]+'"',"-e",str(x)+","+str(y)+",0,0,200,200"])
        x=x+5
        y=y+5

