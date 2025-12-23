# Deep Checks Timeout Analysis

## Confirmed Timeline
- Worker picked up job: ~7:24 PM
- Deep checks timed out: ~7:54 PM
- **Exact 30 minute timeout**

---

## What the Python Script Does

Looking at `run_validation.py`, the script runs these steps in order:

### Step 1: Processing (`process_taggr_143.py`)
```python
results["processing"] = run_processor(task_dir, source_type, metadata)
```
- Parses video.log (~7,500-8,000 lines)
- Updates events.jsonl timestamps (~2,380 events)
- Gets video FPS via ffprobe
- Runs coordinate fix

**Estimated time: < 10 seconds** (just file I/O and parsing)

---

### Step 2: Validation Checks (`validation_checks.py`)
```python
results["validations"]["validation_checks"] = validation_checks.validate(task_dir)
```
- Duration validation
- Idle time detection
- Copy/paste analysis
- Spam detection

**Estimated time: < 5 seconds** (just parses events.jsonl)

---

### Step 3: Cursor Verification (`verify_cursor.py`) ⚠️ **LIKELY CULPRIT**
```python
results["validations"]["cursor"] = verify_cursor.verify(
    task_dir,
    templates=templates,
    sample_size=0,  # Verify ALL clicks <-- THIS IS THE PROBLEM
)
```

**This verifies EVERY click event against the video:**
- **86 clicks** for submission 188,048
- **84 clicks** for submission 187,999

**For EACH click**, it does:
1. Opens video, seeks to frame
2. Tries YOLO detection (neural network inference)
3. Tries template matching (40+ templates × 3 scales)
4. Tries pattern analysis
5. Tries brightness detection
6. Tries Hough circle detection
7. Checks ±100ms window around each frame (6+ frames per click at 30fps)

**Estimated time per click:**
- YOLO inference: ~0.5-2 seconds per frame
- Template matching: ~0.2-0.5 seconds per frame
- Multiple frames checked per click: 6+ frames
- **Total per click: 3-15+ seconds**

**Total for 86 clicks: 4-20+ MINUTES**

---

### Step 4: Gap Detection (`gap_detection.py`)
```python
results["validations"]["gap_detection"] = gap_detection.detect(task_dir)
```
- Analyzes action clustering in events.jsonl

**Estimated time: < 2 seconds**

---

### Step 5: Keypress Verification (`verify_keypress.py`)
```python
results["validations"]["keypress"] = verify_keypress.verify(task_dir)
```
- Verifies keypress events against OCR/screen content
- May involve frame extraction and OCR

**Estimated time: 1-10 minutes** (depends on implementation)

---

## Root Cause Analysis

### 🔴 **Primary Suspect: Cursor Verification with `sample_size=0`**

From `run_validation.py` line 216-219:
```python
results["validations"]["cursor"] = verify_cursor.verify(
    task_dir,
    templates=templates,
    sample_size=0,  # Verify ALL clicks <-- ⚠️ PROBLEM
)
```

**`sample_size=0` means verify ALL 86 clicks!**

Each click verification:
1. Opens video frame at click timestamp
2. Runs YOLO neural network inference
3. Runs template matching with 40+ templates × 3 scales
4. Checks multiple frames in ±100ms window

**Conservative estimate:**
- 86 clicks × 6 frames/click × (1 YOLO + 40 templates × 3 scales)
- = 516 frame reads × (1 + 120) template operations
- = 62,000+ image processing operations

---

### 🔴 **Secondary Suspect: Keypress Verification** (Also very slow!)

From `verify_keypress.py` analysis:
- **241 key presses** for submission 188,048
- **172 key presses** for submission 187,999

For EACH keypress, it does:
1. Seeks to frame at release_time - 100ms (before frame)
2. Seeks to frame at release_time + 60ms (after frame)
3. Compares both frames for pixel differences
4. Runs **OCR (pytesseract)** on detected contours to verify character
5. Classifies as verified/suspicious/scene_change

**Estimated time per keypress:**
- Frame extraction: ~0.1 seconds
- Frame comparison: ~0.05 seconds
- OCR (if enabled): ~0.5-2 seconds per keypress!

**Total for 241 keypresses: 2-8+ MINUTES** (if OCR enabled)

---

### 🟢 **Not the Issue:**
- Processing (fast file parsing)
- Validation checks (fast event analysis)
- Gap detection (fast event analysis)

---

## Solution Options

### Option 1: Reduce Sample Size (Quick Fix)
Change `sample_size=0` to `sample_size=10` or `sample_size=20`:
```python
results["validations"]["cursor"] = verify_cursor.verify(
    task_dir,
    templates=templates,
    sample_size=20,  # Only verify 20 clicks, not all
)
```

### Option 2: Skip YOLO When Not Available/Slow
Add a timeout or skip YOLO if it's taking too long:
```python
# Add timeout to YOLO inference
with timeout(seconds=1):
    result = detect_cursor_yolo(frame, expected_x, expected_y)
```

### Option 3: Reduce Template Scales
Instead of `scales: List[float] = [0.8, 1.0, 1.2]`, use just `[1.0]`:
```python
def detect_cursor_template(..., scales: List[float] = [1.0]):  # Single scale
```

### Option 4: Skip Early on Match
Already implemented - but check if it's working correctly:
```python
# If we found a good match, no need to check more frames
if distance <= tolerance_px:
    break
```

### Option 5: Use Frame Sampling
Instead of checking ±100ms (6 frames), check fewer frames:
```python
frame_buffer = 2  # Instead of int((100 / 1000.0) * video_fps)
```

### Option 6: Parallel Processing
Use multiprocessing to verify clicks in parallel.

---

## Recommended Fix

### Immediate (Config Change):
Change `sample_size` from 0 to 20 in `run_validation.py`:
```python
results["validations"]["cursor"] = verify_cursor.verify(
    task_dir,
    templates=templates,
    sample_size=20,  # Verify 20 representative clicks instead of all
)
```

This should reduce cursor verification time from 20+ minutes to ~2-3 minutes.

### Medium-term (Code Optimization):
1. Add per-click timeout (5 seconds max)
2. Reduce template scales to just [1.0]
3. Reduce frame buffer from 100ms to 50ms
4. Cache video capture object between clicks

### Long-term (Architecture):
1. Make cursor verification optional or async
2. Store verification results separately, don't block submission
3. Use batch GPU inference for YOLO (all frames at once)

---

## Investigation Command

To test locally and confirm, run:
```bash
cd /Users/apple/Github/taggrops/python
time python3 run_validation.py "/Users/apple/Github/trash/Crash Case Exploration/extracted/188048_windows_notepad_slack_reminder_notes"
```

This will show exactly which step is taking the longest.

