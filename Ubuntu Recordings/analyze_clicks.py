#!/usr/bin/env python3
import json

clicks = []
with open('mac_firefox_bookmark_shortcuts_guide/events.jsonl', 'r') as f:
    for line in f:
        if line.strip():
            event = json.loads(line)
            if event.get('action') == 'click' and event.get('pressed') == True:
                clicks.append({
                    'x': event.get('x'),
                    'y': event.get('y'),
                    'second_in_video': event.get('second_in_video'),
                    'frame_index': event.get('frame_index'),
                    'time_stamp_ms': event.get('time_stamp_ms')
                })

print(f"Total clicks: {len(clicks)}")
print(f"\nClick events:")
for i, click in enumerate(clicks, 1):
    frame_calc = int(click['second_in_video'] * 30) if click['second_in_video'] else None
    print(f"  {i}. At {click['second_in_video']:.3f}s (frame ~{frame_calc}) - Position: ({click['x']}, {click['y']})")

print(f"\nAnalysis:")
print(f"  - Clicks span from {clicks[0]['second_in_video']:.3f}s to {clicks[-1]['second_in_video']:.3f}s")
print(f"  - That's {clicks[-1]['second_in_video'] - clicks[0]['second_in_video']:.3f} seconds")
print(f"  - At 30fps, that's approximately {int((clicks[-1]['second_in_video'] - clicks[0]['second_in_video']) * 30)} frames apart")
print(f"\n  If cursor verification used frame_index=-1:")
print(f"    - It would try to seek to frame -1")
print(f"    - The ±100ms buffer would check frames around -1 (frames -4 to +2)")
print(f"    - Frame 0-2 would be checked, which only covers 0-0.1 seconds")
print(f"    - But clicks are at 3.97s, 4.50s, 5.69s, 6.40s, 6.79s, 7.06s, 13.25s, 15.03s")
print(f"    - So it SHOULD NOT work if using frame_index=-1!")

