# Chromat – MIDI to Generative Visual Art

Chromat is an audiovisual system that transforms MIDI performances into generative visual art. Musical tempo, pitch, and articulation control the placement, color, and persistence of visual elements, allowing users to “paint” music visually.

---

## Demo Video

Watch a demo of Chromat in action:  
[YouTube Playlist](https://www.youtube.com/playlist?list=PLT9PAj_E8_wniJ5gWTZbajqatTqdJyxMi)

---

## Features

- Real-time MIDI visualization using **pygame**.  
- Time → horizontal position, pitch → vertical position, velocity/loop index → color intensity.  
- Loop-based visualization reveals repetition, density, and musical form.  
- Optional MIDI output to external instruments for synchronized audiovisual performance.  
- Tkinter-based UI for selecting MIDI files, adjusting BPM, colors, and gridlines.  

---

## System Architecture

1. **MIDI Parsing**  
   - Loads standard MIDI files using `mido`.  
   - Extracts note-on/off events, pitch, velocity, and timing.  
   - Converts MIDI tick timing into continuous musical time.  

2. **Temporal Looping Engine**  
   - Creates a layered 4-bar visual loop for emergent musical patterns.  
   - BPM scaling allows speed adjustment while preserving visual layering.  

3. **Visual Mapping (Music → Canvas)**  
   - Time → Horizontal position (left → right).  
   - Pitch → Vertical position (keyboard range mapped to screen height).  
   - Velocity / Loop index → Color assignment.  
   - Note duration → Persistence of visual marks.  

4. **Rendering Engine**  
   - Built with `pygame` for real-time graphics.  
   - Notes rendered as glowing, brush-like circles.  
   - Optional gridlines emphasize rhythmic structure.  

5. **Optional MIDI Output**  
   - Sends note events to an external MIDI port.  
   - Enables synchronized sound generation.  

---

## Dependencies

- Python ≥ 3.8  
- `pygame`  
- `mido`  
- `tkinter` (built-in)  

You can install dependencies with:

```bash
pip install pygame mido
