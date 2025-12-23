## Problem

Ubuntu recordings were generating events with `frame_index: -1`, causing false positives in deep checks:

1. **Gap Detection False Positive**: All non-move actions were grouped into "frame -1", resulting in `gap_max_actions_per_frame: 44` (threshold: 12), causing the `python_system_config_checks` deep check to fail.

2. **Cursor Verification False Positive**: The cursor verification script was checking frames 0-2 (from the ±100ms buffer around frame -1) instead of the actual click frames (e.g., frame 119 at 3.97s), leading to a suspicious 100% match rate.

## Root Cause

The recording code was not properly extracting or setting `frame_index` values from the video frame synchronization data. When `frame_index` was unavailable, it defaulted to `-1`, which was then used as a valid frame index in verification scripts.

## Solution

Added `self.update_current_frame_index(frame_index)` call to update the shared frame counter in real-time as frames are processed, ensuring events captured at that moment get the correct `frame_index` value.

## Before/After Results

### Before (Submission 223,368)

**Deep Check Results:**
- ❌ `python_system_config_checks`: **FAILED**
- `gap_max_actions_per_frame`: **44** (threshold: 12) ❌
- `actual_match` (cursor): **1.0** (100%) ⚠️ (suspicious - false positive)
- `keypress_verification_rate`: **0.9091** (90.91%) ✅

**Events.jsonl:**
```json
{"time_stamp_ms": 8601980.356278, "frame_index": -1, "action": "move", "x": 808.0, "y": 299.0, "second_in_video": 3.4423891949988903}
{"time_stamp_ms": 8602508.413825, "frame_index": -1, "action": "click", "x": 244.0, "y": 410.0, "button": "left", "pressed": true, "second_in_video": 3.9704467419981957}
```

**Issue:**
- All events had `frame_index: -1`
- Gap detection grouped all 44 non-move actions into "frame -1"
- Cursor verification checked wrong frames (0-2 instead of actual click frames)

### After (Submission 223,478)

**Deep Check Results:**
- ✅ `python_system_config_checks`: **PASSED**
- `gap_max_actions_per_frame`: **2** (threshold: 12) ✅
- `actual_match` (cursor): **1.0** (100%) ✅ (legitimate - verified)
- `keypress_verification_rate`: **0.9545** (95.45%) ✅

**Events.jsonl:**
```json
{"time_stamp_ms": 1883207.7025829998, "frame_index": 112, "action": "click", "x": 813.0, "y": 43.0, "button": "left", "pressed": true, "second_in_video": 3.728436628999654}
{"time_stamp_ms": 1883703.559145, "frame_index": 127, "action": "click", "x": 874.0, "y": 184.0, "button": "left", "pressed": false, "second_in_video": 4.224293190999888}
```

**Verification:**
- All events now have valid `frame_index` values (112, 127, 137, etc.)
- Gap detection correctly identifies frame distribution (max 2 actions per frame)
- Cursor verification checks correct frames and achieves legitimate 100% match:
  - Click 0 @ 3.73s: Expected (813, 43) → Detected (828, 58) - Distance: 20.8px ✅
  - Click 1 @ 4.55s: Expected (874, 184) → Detected (891, 198) - Distance: 21.8px ✅
  - Click 2 @ 5.07s: Expected (852, 185) → Detected (869, 199) - Distance: 21.9px ✅
  - Click 3 @ 12.43s: Expected (1784, 11) → Detected (1791, 15) - Distance: 8.4px ✅
  - Click 4 @ 13.99s: Expected (1786, 77) → Detected (1810, 104) - Distance: 36.1px ✅

### Impact

- ✅ Eliminates false positives in gap detection
- ✅ Enables accurate cursor verification
- ✅ Maintains compatibility with existing verification scripts
- ✅ No breaking changes to the events.jsonl format

## Testing

- [x] Verified with Ubuntu 24.04 recordings
- [x] Confirmed deep checks pass with corrected frame indices
- [x] Validated cursor verification results are legitimate
- [x] Tested backward compatibility with existing submissions
