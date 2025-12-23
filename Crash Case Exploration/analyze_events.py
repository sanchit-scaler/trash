#!/usr/bin/env python3
"""Analyze events.jsonl for anomalies that could cause timeout"""
import json
from collections import Counter

def analyze_submission(folder_name):
    base_path = f"/Users/apple/Github/trash/Crash Case Exploration/extracted/{folder_name}"
    
    print(f"\n{'='*60}")
    print(f"ANALYZING: {folder_name}")
    print(f"{'='*60}")
    
    # Load events
    events = []
    with open(f"{base_path}/events.jsonl", 'r') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line.strip()))
    
    # Load metadata
    with open(f"{base_path}/metadata.json", 'r') as f:
        meta = json.load(f)
    
    print(f"\n📺 VIDEO INFO:")
    print(f"  Screen resolution: {meta['screen_width']}x{meta['screen_height']}")
    print(f"  Video resolution: {meta['video_width']}x{meta['video_height']}")
    print(f"  Scale factor: {meta['screen_width'] / meta['video_width']:.2f}x")
    print(f"  FPS: {meta['video_fps']}")
    
    # Count video.log lines
    with open(f"{base_path}/video.log", 'r') as f:
        video_lines = sum(1 for _ in f) - 2  # Subtract header lines
    print(f"  Total frames: {video_lines}")
    print(f"  Duration: ~{video_lines/30:.1f}s")
    
    # Event breakdown
    action_counts = Counter(e.get('action') for e in events)
    print(f"\n📋 EVENT BREAKDOWN:")
    for action, count in action_counts.most_common():
        print(f"  {action}: {count}")
    print(f"  TOTAL EVENTS: {len(events)}")
    
    # Check frames with most events (stalls/freezes)
    frame_counts = Counter(e.get('frame_number') for e in events if 'frame_number' in e)
    print(f"\n🔴 FRAMES WITH MANY EVENTS (potential lag/stalls):")
    stalled = [(f, c) for f, c in frame_counts.most_common(10) if c > 5]
    if stalled:
        for frame, count in stalled:
            # Find time at this frame
            frame_events = [e for e in events if e.get('frame_number') == frame]
            time_range = (frame_events[0].get('second_in_video', 0), frame_events[-1].get('second_in_video', 0))
            print(f"  Frame {frame}: {count} events (video time: {time_range[0]:.1f}s)")
    else:
        print("  None found - good!")
    
    # Check for large time gaps
    print(f"\n⏱️ LARGE TIME GAPS (>500ms):")
    gaps = []
    for i in range(1, len(events)):
        prev_ts = events[i-1].get('time_stamp_ms', 0)
        curr_ts = events[i].get('time_stamp_ms', 0)
        if prev_ts and curr_ts:
            gap = curr_ts - prev_ts
            if gap > 500:
                gaps.append((i, gap, events[i].get('action'), events[i].get('second_in_video', 0)))
    
    if gaps:
        for idx, gap, action, sec in gaps[:10]:
            print(f"  Gap of {gap:.0f}ms at event {idx} (action: {action}, video time: {sec:.1f}s)")
        if len(gaps) > 10:
            print(f"  ... and {len(gaps) - 10} more gaps")
    else:
        print("  None found - good!")
    
    # Check for events with frame_index vs frame_number mismatch
    print(f"\n🔍 FRAME INDEX CONSISTENCY CHECK:")
    mismatches = []
    for e in events:
        fi = e.get('frame_index')
        fn = e.get('frame_number')
        if fi is not None and fn is not None:
            diff = fn - fi
            if diff > 10:  # Significant drift
                mismatches.append((e.get('second_in_video', 0), diff, e.get('action')))
    
    if mismatches:
        print(f"  Found {len(mismatches)} events with frame_number - frame_index > 10")
        print(f"  Max drift: {max(m[1] for m in mismatches)}")
    else:
        print("  No significant drift - good!")
    
    # Check for duplicate timestamps
    print(f"\n📍 CLICK EVENTS ANALYSIS (for cursor verification):")
    clicks = [e for e in events if e.get('action') == 'click']
    print(f"  Total clicks: {len(clicks)}")
    
    # Check unique click positions
    click_positions = [(e.get('x'), e.get('y')) for e in clicks]
    unique_positions = set(click_positions)
    print(f"  Unique click positions: {len(unique_positions)}")
    
    if len(clicks) > 0:
        # Check if clicks span full video duration
        click_times = [e.get('second_in_video', 0) for e in clicks]
        print(f"  Click time range: {min(click_times):.1f}s - {max(click_times):.1f}s")
    
    return len(events), action_counts.get('click', 0), action_counts.get('press', 0)

# Analyze both submissions
print("=" * 70)
print("CRASH CASE ANALYSIS - Looking for timeout causes")
print("=" * 70)

results = {}
for folder in ["188048_windows_notepad_slack_reminder_notes", "187999_gov1_eg90_5iza_c1kb"]:
    try:
        results[folder] = analyze_submission(folder)
    except Exception as e:
        print(f"Error analyzing {folder}: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
for folder, (events, clicks, presses) in results.items():
    print(f"\n{folder}:")
    print(f"  Total events: {events}")
    print(f"  Clicks to verify: {clicks} (YOLO model runs per click)")
    print(f"  Keypresses to verify: {presses // 2} (OCR runs per keypress)")
    total_verifications = clicks + (presses // 2)
    print(f"  TOTAL VERIFICATIONS: {total_verifications}")
    print(f"  Estimated time at 2-3s each: {total_verifications * 2.5 / 60:.1f} - {total_verifications * 3 / 60:.1f} minutes")




