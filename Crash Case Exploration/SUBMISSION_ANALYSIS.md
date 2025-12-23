# Submission File Analysis - 188048_windows_notepad_slack_reminder_notes

## 📊 File Overview

### metadata.json
| Field | Value |
|-------|-------|
| Screen Resolution | **3200 × 2000** (high DPI display) |
| Video Resolution | 1920 × 1080 |
| **Scale Factor** | **1.67x** (screen to video) |
| FPS | 30 |
| App Version | 1.4.5 |
| System | Windows 11 (10.0.26100) |
| Processor | Intel 11th Gen Tiger Lake |
| Model | Mi NoteBook Ultra |

### video.log
- **Total frames**: 7580 (lines 3-7582)
- **Duration**: ~252.6 seconds (4.2 minutes)
- **Format**: Native Windows Desktop Duplication API
- **Frame timing**: Consistent 33.33ms intervals (perfect 30fps)
- **No dropped frames detected** - timestamps are perfectly sequential

### events.jsonl
- **Total events**: 2380 lines

| Event Type | Count |
|------------|-------|
| move | 1533 |
| scroll | 295 |
| press | 241 |
| release | 224 |
| click | 86 |

---

## 🔍 Potential Anomalies Detected

### 1. **High Resolution Display (3200×2000)**

The user has a **high DPI display** scaled down to 1920×1080 for video.
- Scale factor: 1.67x
- This could affect cursor position calculations
- The validation may need to rescale coordinates for each verification

### 2. **Frame Clustering at End of Video**

Looking at the end of `events.jsonl`:
- **16 events** all map to `frame_number: 7578` and `second_in_video: 252.6`
- This means these events all show the same video timestamp
- Likely because recording stopped but events continued briefly

### 3. **Click Event Distribution**

- **43 actual clicks** (pressed=true)
- **86 total click events** (43 press + 43 release)
- Each click triggers cursor verification via YOLO model

### 4. **Keypress Count**

- **241 key presses** (includes modifier keys)
- **~120 actual keypress pairs** for verification
- Each keypress triggers OCR verification

---

## ⏱️ Estimated Processing Time (Why Timeout)

### Cursor Verification (for 43 clicks)
```
Per click:
- Seek to frame: ~0.1s
- YOLO inference: ~2-5s (CPU)
- Template matching: ~1-2s (40+ templates × 3 scales)
- Repeat for ±100ms window (6+ frames)

Total per click: 5-15 seconds
Total for 43 clicks: 3.5 - 10+ minutes
```

### Keypress Verification (for ~120 keypresses)
```
Per keypress:
- Frame extraction (before/after): ~0.2s
- Pixel comparison: ~0.1s
- OCR (pytesseract): ~0.5-2s

Total per keypress: 1-3 seconds
Total for 120 keypresses: 2 - 6 minutes
```

### Combined Estimate
| Check | Time Range |
|-------|------------|
| Cursor verification | 3.5 - 10 min |
| Keypress verification | 2 - 6 min |
| Other validations | 1 - 2 min |
| **TOTAL** | **6.5 - 18+ min** |

With slower CPU or high load: **20-30+ min → TIMEOUT**

---

## ✅ What Looks GOOD

1. **Video quality**: 30fps constant, no frame drops
2. **Frame timing**: Perfect 33.33ms intervals
3. **Duration**: Reasonable (~4 min video)
4. **Event count**: Normal (~2400 events)
5. **Click count**: Normal (43 clicks)

---

## 🚨 Root Cause Hypothesis

The timeout is likely due to:

1. **Processing happening on CPU** (no GPU acceleration for YOLO/OCR)
2. **High number of verifications**: 43 clicks + 120 keypresses = ~163 ML operations
3. **Shared worker resources**: Other jobs consuming CPU time
4. **High-res screen** requiring coordinate transformations

### Supporting Evidence:
- Simple checks passed instantly (file validation, duration, etc.)
- Only deep checks (ML-based) failed
- Error message confirms: "Deep checks validation timed out after 1800000ms"

---

## 💡 Recommendations

1. **Add GPU support** for YOLO inference (10x faster)
2. **Reduce sample size** for cursor verification (don't verify ALL clicks)
3. **Increase timeout** or make it proportional to video duration
4. **Queue priority** for shorter videos
5. **Add progress logging** to identify bottleneck




