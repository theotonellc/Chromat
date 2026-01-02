import pygame
import mido
import time
import tkinter as tk
from tkinter import filedialog, simpledialog, colorchooser
MIDI_PORT_NAME="IAC Driver Bus 1"
LARGO=1440
SCREEN_HEIGHT =800
FPS= 60
MAX_POSITIONS= 500
dot_size=17
SHOW_GRIDLINES= False
root= tk.Tk()
root.withdraw()
MIDI_FILE_PATH = filedialog.askopenfilename(title="Select a MIDI file", filetypes=[("MIDI files", "*.mid")])
bpm_input= simpledialog.askstring("BPM Input","Enter BPM (e.g. 60):")
BPM= int(bpm_input) if bpm_input and bpm_input.isdigit() else 120
BASE_BPM=120
BPM_SCALE=BPM/BASE_BPM
bg= colorchooser.askcolor(title="Choose background color")[0]
BG_COLOR= tuple(map(int,bg)) if bg else (0,0,0)
LOOP_COLORS=[(255,255,255)]
editor=tk.Toplevel()
editor.title("Loop Color Editor")
editor.attributes("-topmost",True)
list_frame=tk.Frame(editor)
list_frame.pack(padx=10,pady=10)
def refresh_list():
    for w in list_frame.winfo_children():
        w.destroy()
    for i, color in enumerate(LOOP_COLORS):
        row= tk.Frame(list_frame)
        row.pack(fill="x", pady=2)
        swatch= tk.Canvas(row,width=30,height=20,bg=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",bd=1,relief="ridge")
        swatch.pack(side="left", padx=4)
        tk.Label(row,text=str(color)).pack(side="left",padx=4)
        def edit(idx=i):
            new =colorchooser.askcolor(title="Edit loop color")[0]
            if new:
                LOOP_COLORS[idx]=tuple(map(int,new))
                refresh_list()
        def remove(idx=i):
            if len(LOOP_COLORS)>1:
                LOOP_COLORS.pop(idx)
                refresh_list()
        tk.Button(row,text="Edit",command=edit,width=6).pack(side="right",padx=2)
        tk.Button(row,text="Remove",command=remove,width=6).pack(side="right")
def add_color():
    new =colorchooser.askcolor(title ="Add loop color")[0]
    if new:
        LOOP_COLORS.append(tuple(map(int,new)))
        refresh_list()
tk.Button(editor,text="Add Color",command=add_color).pack(pady=4)
tk.Button(editor,text="Done",command=editor.destroy).pack(pady=(0,8))
refresh_list()
editor.grab_set()
editor.wait_window()
grid_popup=tk.Toplevel()
grid_popup.title("Gridlines")
grid_popup.attributes("-topmost",True)
tk.Label(grid_popup,text ="Show beat / bar gridlines?",font=("Arial",11)).pack(padx=10,pady=(10,5))
def choose_gridlines(choice):
    global SHOW_GRIDLINES
    SHOW_GRIDLINES=choice
    grid_popup.destroy()
btn_frame=tk.Frame(grid_popup)
btn_frame.pack(pady=10)
tk.Button(btn_frame,text="Yes",width=10,command=lambda:choose_gridlines(True)).pack(side="left",padx=5)
tk.Button(btn_frame,text="No",width=10,command=lambda:choose_gridlines(False)).pack(side="right",padx=5)
grid_popup.grab_set()
grid_popup.wait_window()
ENABLE_MIDI_OUTPUT=True
midi_popup=tk.Toplevel()
midi_popup.title("MIDI Output")
midi_popup.attributes("-topmost",True)
tk.Label(midi_popup,text="Enable MIDI Output?", font=("Arial",12)).pack(pady=10)
def midi_yes():
    global ENABLE_MIDI_OUTPUT
    ENABLE_MIDI_OUTPUT= True
    midi_popup.destroy()
def midi_no():
    global ENABLE_MIDI_OUTPUT
    ENABLE_MIDI_OUTPUT= False
    midi_popup.destroy()
frame=tk.Frame(midi_popup)
frame.pack()
tk.Button(frame,text="Yes", width=10,command=midi_yes).pack(side="left",padx=10)
tk.Button(frame,text="No", width=10,command=midi_no).pack(side="right",padx=10)
midi_popup.grab_set()
midi_popup.wait_window()
BEATS_PER_BAR=4
BARS_IN_LOOP=4
BEATS_IN_LOOP=BEATS_PER_BAR*BARS_IN_LOOP
SECONDS_PER_BEAT=60 / BASE_BPM
LOOP_DURATION=BEATS_IN_LOOP*SECONDS_PER_BEAT
pygame.init()
pygame.mouse.set_visible(False)
display=pygame.display.set_mode((LARGO,SCREEN_HEIGHT))
pygame.display.set_caption("Chromat")
clock=pygame.time.Clock()
def draw_glowing_circle(surface,pos,color,radius=10,glow_radius=6):
    glow=pygame.Surface((radius*4,radius*4), pygame.SRCALPHA)
    for i in range(glow_radius,0,-1):
        alpha=int(255*(i/glow_radius)*0.2)
        pygame.draw.circle(glow,(*color,alpha),(radius*2,radius*2), radius+i)
    pygame.draw.circle(glow,(*color,255),(radius*2,radius*2), radius)
    surface.blit(glow,(pos[0]-radius*2,pos[1]-radius*2))
def draw_scanlines(surface,spacing=4):
    line =pygame.Surface((surface.get_width(),1), pygame.SRCALPHA)
    line.fill((0,0,0,40))
    for y in range(0,surface.get_height(),spacing):
        surface.blit(line,(0,y))
def draw_gridlines(surface):
    beat_w=LARGO / BEATS_IN_LOOP
    bar_w= beat_w * BEATS_PER_BAR
    for i in range(BEATS_IN_LOOP+1):
        x = int(i * beat_w)
        pygame.draw.line(surface,(255,255,255,40), (x,0), (x,12),1)
    for i in range(BARS_IN_LOOP+1):
        x=int(i*bar_w)
        pygame.draw.line(surface,(255,255,255,90), (x,0), (x,18),2)
midi=mido.MidiFile(MIDI_FILE_PATH)
note_list=[]
current_time=0
note_stack={}
for msg in midi:
    current_time+=msg.time
    if msg.type == "note_on" and msg.velocity>0:
        note_stack[msg.note]={
            "note":msg.note,
            "velocity":msg.velocity,
            "start":current_time,
            "end":None,
            "color":(255,255,255),
            "played": False,
            "positions":[]}
    elif msg.type in ("note_off","note_on") and msg.note in note_stack:
        note=note_stack.pop(msg.note)
        note["end"]=current_time
        note_list.append(note)
outport=None
if ENABLE_MIDI_OUTPUT:
    try:
        outport=mido.open_output(MIDI_PORT_NAME)
    except IOError:
        ENABLE_MIDI_OUTPUT=False
class Bar:
    def __init__(self):
        self.x=0
    def draw(self):
        pygame.draw.line(display, (255,0,0),(int(self.x), 0),(int(self.x),SCREEN_HEIGHT),2)
def game():
    start_time=time.time()
    bar=Bar()
    running=True
    while running:
        elapsed_real=time.time()-start_time
        elapsed_musical=elapsed_real*BPM_SCALE
        current_loop=int(elapsed_musical // LOOP_DURATION)
        if current_loop != getattr(game,"last_loop",-1):
            for note in note_list:
                note["played"]=False
            game.last_loop=current_loop
        fade=pygame.Surface((LARGO,SCREEN_HEIGHT), pygame.SRCALPHA)
        fade.fill((*BG_COLOR,18))
        canvas=pygame.Surface((LARGO,SCREEN_HEIGHT))
        canvas.blit(fade,(0,0))
        phase=(elapsed_musical % LOOP_DURATION) / LOOP_DURATION
        loop_index= int((elapsed_musical // LOOP_DURATION) % len(LOOP_COLORS))
        current_color=LOOP_COLORS[loop_index]
        bar.x=phase*LARGO
        if SHOW_GRIDLINES:
            draw_gridlines(canvas)
        for note in note_list:
            if note["start"] <= elapsed_musical <= note["end"]:
                if not note["played"]:
                    note["color"]=current_color
                    if ENABLE_MIDI_OUTPUT and outport:
                        outport.send(mido.Message("note_on",note=note["note"],velocity=note["velocity"]))
                    note["played"]=True
                y=SCREEN_HEIGHT-int((note["note"] - 21) / (108 - 21) * SCREEN_HEIGHT)
                x=int(phase * LARGO)
                note["positions"].append((x,y))
                if len(note["positions"])>MAX_POSITIONS:
                    note["positions"] =note["positions"][-MAX_POSITIONS:]

            for pos in note["positions"]:
                draw_glowing_circle(canvas,pos,note["color"], dot_size)
        draw_scanlines(canvas)
        display.blit(canvas,(0,0))
        bar.draw()
        for e in pygame.event.get():
            if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.k_ESCAPE):
                running=False
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
if __name__=="__main__":
    game()