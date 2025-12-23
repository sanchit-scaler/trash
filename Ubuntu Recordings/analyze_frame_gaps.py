#!/usr/bin/env python3
"""
Analyze events.jsonl to check if there are really 44 actions in a single frame.
Since frame_index is -1 for all events, we'll analyze by time windows.
"""

import json
from collections import defaultdict

# Video FPS from metadata
FPS = 30
FRAME_DURATION_MS = 1000 / FPS  # ~33.33ms per frame

# Read events
events = []
with open('mac_firefox_bookmark_shortcuts_guide/events.jsonl', 'r') as f:
    for line in f:
        if line.strip():
            events.append(json.loads(line))

print(f"Total events: {len(events)}")
print(f"Video FPS: {FPS} (frame duration: {FRAME_DURATION_MS:.2f}ms)")
print()

# Group events by time windows (simulating frames)
# Since frame_index is -1, we'll use time-based grouping
frame_groups = defaultdict(list)

for event in events:
    timestamp_ms = event['time_stamp_ms']
    # Calculate which "frame" this event belongs to based on time
    # Using first event as reference
    if events:
        first_timestamp = events[0]['time_stamp_ms']
        relative_time_ms = timestamp_ms - first_timestamp
        # Group into ~33.33ms windows (one frame at 30fps)
        frame_number = int(relative_time_ms / FRAME_DURATION_MS)
        frame_groups[frame_number].append(event)

# Find frames with most actions
max_actions = 0
max_frame = None
action_counts = []

for frame_num, frame_events in frame_groups.items():
    action_count = len(frame_events)
    action_counts.append((frame_num, action_count))
    if action_count > max_actions:
        max_actions = action_count
        max_frame = frame_num

# Sort by action count
action_counts.sort(key=lambda x: x[1], reverse=True)

print(f"Frame with most actions: Frame {max_frame} with {max_actions} actions")
print(f"\nTop 10 frames by action count:")
for frame_num, count in action_counts[:10]:
    frame_time_start = frame_num * FRAME_DURATION_MS
    frame_time_end = (frame_num + 1) * FRAME_DURATION_MS
    print(f"  Frame {frame_num}: {count} actions (time: {frame_time_start:.2f}ms - {frame_time_end:.2f}ms)")

print(f"\n{'='*60}")
print(f"Analysis: Is there a frame with 44+ actions?")
if max_actions >= 44:
    print(f"  YES - Found frame {max_frame} with {max_actions} actions")
    print(f"  Events in that frame:")
    for i, event in enumerate(frame_groups[max_frame][:10], 1):
        print(f"    {i}. {event['action']} at {event['time_stamp_ms']:.2f}ms")
    if len(frame_groups[max_frame]) > 10:
        print(f"    ... and {len(frame_groups[max_frame]) - 10} more")
else:
    print(f"  NO - Maximum is {max_actions} actions in a single frame")
    print(f"  The deep check might be using a different calculation method")

# Also check if there are rapid bursts of events
print(f"\n{'='*60}")
print("Checking for rapid event bursts (events within 33.33ms windows):")
bursts = []
for i, event in enumerate(events):
    window_start = event['time_stamp_ms']
    window_end = window_start + FRAME_DURATION_MS
    # Count events in this window
    events_in_window = [e for e in events if window_start <= e['time_stamp_ms'] < window_end]
    if len(events_in_window) > 10:  # More than 10 events in one frame
        bursts.append((window_start, len(events_in_window), events_in_window))

if bursts:
    print(f"Found {len(bursts)} time windows with 10+ events:")
    for start_time, count, window_events in sorted(bursts, key=lambda x: x[1], reverse=True)[:5]:
        print(f"  Window starting at {start_time:.2f}ms: {count} events")
        print(f"    Actions: {', '.join([e['action'] for e in window_events[:10]])}")
        if len(window_events) > 10:
            print(f"    ... and {len(window_events) - 10} more")
else:
    print("  No significant bursts found using time-based windows")

