# Testing Checklist: `feat/hwaccel-sysreq-hybuf-letterbox`

## Overview
Testing checklist for the hardware acceleration, system requirements, hybrid buffer, and letterbox features.

**Branch:** `feat/hwaccel-sysreq-hybuf-letterbox`  
**Test Machines:** Windows, macOS, Ubuntu  
**Build Mode:** Dev mode with console  
**Already Tested:** ✅ System Requirements Check

---

## Pre-Testing Setup

### All Machines
- [ ] Build in dev mode with console: `python build.py --dev`
- [ ] Verify console output is visible
- [ ] Check logs directory for detailed logging
- [ ] Have Task Manager / Activity Monitor / System Monitor ready to check resource usage
- [ ] Prepare test recording scenarios:
  - [ ] Single monitor setup
  - [ ] Dual/Multi-monitor setup (if available)
  - [ ] Different aspect ratios (if possible)

### Test Data Collection
Create a test results folder structure:
```
test-results/
  ├── windows/
  │   ├── logs/
  │   ├── recordings/
  │   └── screenshots/
  ├── macos/
  │   ├── logs/
  │   ├── recordings/
  │   └── screenshots/
  └── ubuntu/
      ├── logs/
      ├── recordings/
      └── screenshots/
```

---

## 🪟 Windows Testing

### Hardware Acceleration Detection

#### GPU Detection
- [ ] **Launch app and check console output for GPU detection**
  - [ ] Look for log: `"Detected GPU vendor: [NVIDIA|AMD|Intel|Unknown]"`
  - [ ] Note detected GPU: _________________
  
#### Encoder Selection
- [ ] **Check encoder selection in console**
  - [ ] Look for log: `"Selected hardware encoder: [codec] ([type])"`
  - [ ] Note selected encoder: _________________
  - [ ] Expected encoders by GPU:
    - NVIDIA: `h264_nvenc` or `hevc_nvenc`
    - AMD: `h264_amf` or `hevc_amf`
    - Intel: `h264_qsv` or `hevc_qsv`
    - None/Unknown: `libx264` (software fallback)

#### Encoder Override Test
- [ ] **Test environment variable override**
  ```bash
  set TAGGR_FFMPEG_ENCODER=libx264
  # Run Taggr
  ```
  - [ ] Verify log shows: `"Using encoder from TAGGR_FFMPEG_ENCODER: libx264"`
  - [ ] Recording works with override
  - [ ] Remove override and verify hardware encoder is used again

#### Encoder Preset Verification
- [ ] **Check that correct presets are applied**
  - [ ] For NVENC: Look for `-preset p1` in ffmpeg command
  - [ ] For QSV: Look for `-preset veryfast` in ffmpeg command
  - [ ] For AMF: No preset (uses default)
  - [ ] For libx264: Look for `-preset ultrafast` in ffmpeg command
  - [ ] Check console logs for encoder arguments

#### FFmpeg Encoder Query
- [ ] **Verify encoder detection**
  - [ ] Look for: `"Available video encoders: [...]"` in console
  - [ ] No timeout warnings during encoder query (10s timeout)
  - [ ] Encoders list includes expected hardware encoders

### Recording Tests

#### Basic Recording
- [ ] **Start and stop a 30-second recording**
  - [ ] Recording starts without errors
  - [ ] Console shows frame capture progress
  - [ ] Check for log: `"⏱ Hardware requirements check took [X]s"`
  - [ ] Video file created: `video.mp4`
  - [ ] Events file created: `events.jsonl`
  - [ ] Metadata file created: `metadata.json`
  - [ ] Video plays successfully

#### Hardware Encoder Performance
- [ ] **Compare CPU usage between hardware and software encoding**
  - [ ] Record 1 min with hardware encoder, note CPU%: _____
  - [ ] Set `TAGGR_FFMPEG_ENCODER=libx264`, record 1 min, note CPU%: _____
  - [ ] Hardware encoding should use significantly less CPU

#### Windows-Specific: Hybrid Buffer (Cursor at Frame Time)
- [ ] **Test cursor synchronization**
  - [ ] During recording, move cursor rapidly in circles
  - [ ] Stop recording and play back video
  - [ ] Verify cursor position is smooth (not jittery/laggy)
  - [ ] Check `events.jsonl` has `cursor_pos` field in `FramePayload`
  - [ ] Check console for: `"None-frame count from dxcam: [X]"` (should be low, <5% of frames)
  - [ ] Check console for: `"Frame queue stalled [X] times waiting for encoder"` (should be 0)

#### Windows-Specific: Trackpad Scroll Events
- [ ] **Test trackpad scrolling (if available)**
  - [ ] Use two-finger scroll gestures on trackpad
  - [ ] Verify scroll events in `events.jsonl` have:
    - [ ] `frame_pts_seconds` present
    - [ ] `raw_x`, `raw_y` coordinates
  - [ ] Trackpad scroll uses same frame timing as mouse scroll

#### Windows-Specific: PTS-Based Timing
- [ ] **Verify PTS synchronization**
  - [ ] Check `events.jsonl` for events with:
    - [ ] `frame_pts_seconds` field (not null)
    - [ ] `second_in_video` field matches PTS
    - [ ] `raw_x` and `raw_y` fields present
  - [ ] Sample event structure:
    ```json
    {
      "time_stamp_ms": ...,
      "frame_index": ...,
      "frame_pts_seconds": 2.345,
      "second_in_video": 2.345,
      "action": "move",
      "x": 960, "y": 540,
      "raw_x": 1920, "raw_y": 1080
    }
    ```

### Letterbox Testing

#### Aspect Ratio Mismatch
- [ ] **Test with non-matching video resolution**
  - [ ] Set video output to 1280x720 (16:9)
  - [ ] Record on 1920x1200 monitor (16:10) or similar mismatch
  - [ ] Check `metadata.json` for letterbox fields:
    ```json
    "letterbox_scale": 0.xxx,
    "letterbox_pad_x": X,
    "letterbox_pad_y": Y,
    "letterbox_scaled_width": XXXX,
    "letterbox_scaled_height": XXXX
    ```
  - [ ] Verify video has black bars (top/bottom or sides)
  - [ ] Click on corners and edges during recording
  - [ ] Verify `events.jsonl` coordinates map correctly to visible area
  - [ ] Verify formula: `x = raw_x * letterbox_scale + letterbox_pad_x`

#### Letterbox Edge Cases
- [ ] **Same aspect ratio (no letterbox needed)**
  - [ ] Set video resolution with same aspect ratio as screen
  - [ ] Verify `letterbox_pad_x` and `letterbox_pad_y` are 0 (or minimal)
  - [ ] No black bars in video
  
- [ ] **Verify letterbox formula matches ffmpeg**
  - [ ] `letterbox_scale = min(video_w/screen_w, video_h/screen_h)`
  - [ ] `pad_x = (video_w - scaled_w) // 2` (integer division)
  - [ ] `pad_y = (video_h - scaled_h) // 2` (integer division)

#### Visual Letterbox Verification
- [ ] **Check video output visually**
  - [ ] Open recorded `video.mp4` in VLC/media player
  - [ ] With aspect ratio mismatch, verify:
    - [ ] Black bars visible (top/bottom OR left/right)
    - [ ] Screen content is centered
    - [ ] No stretching or distortion of content
  - [ ] Screenshot any issues for documentation

#### Multi-Monitor Desktop Dimensions
- [ ] **Test with multiple monitors (if available)**
  - [ ] Check console for: `"Desktop dimensions via GetSystemMetrics: [W]x[H]"`
  - [ ] Verify `metadata.json` has:
    ```json
    "screen_width": [total virtual width],
    "screen_height": [total virtual height]
    ```
  - [ ] Move cursor across monitors during recording
  - [ ] Verify coordinates in `events.jsonl` span full virtual desktop

#### Multi-Monitor Negative Coordinates
- [ ] **Test with monitor positioned LEFT of primary**
  - [ ] Position secondary monitor to LEFT in Display Settings
  - [ ] Start recording
  - [ ] Move cursor and click on secondary (left) monitor
  - [ ] Check `events.jsonl`:
    - [ ] `raw_x` values should be NEGATIVE on secondary monitor
  - [ ] Coordinates should still scale correctly with letterbox

- [ ] **Test with monitor positioned ABOVE primary**
  - [ ] Position secondary monitor ABOVE in Display Settings
  - [ ] Check `events.jsonl`:
    - [ ] `raw_y` values should be NEGATIVE on secondary monitor

### Video Quality & Duration

#### Output Validation
- [ ] **Check video output**
  - [ ] Open `video.mp4` in VLC/media player
  - [ ] Check video properties match expected resolution
  - [ ] Check framerate is 30fps (or configured value)
  - [ ] Audio: None (video-only)
  - [ ] Codec: Check with `ffprobe video.mp4`
    - [ ] Should show hardware codec (h264_nvenc, etc.) or libx264

#### Duration Accuracy
- [ ] **Verify duration matching**
  - [ ] Record for exactly 60 seconds
  - [ ] Check console logs for:
    - `"Capture duration: [X]s"`
    - `"encoded duration before scaling: [X]s"`
  - [ ] Check for warnings: `"Duration mismatch detected"` (should NOT appear, or <1s difference)
  - [ ] After remux, check for: `"Output duration mismatch"` (should NOT appear)
  - [ ] Verify `video.mp4` duration matches recording time (±1s)

#### video.log Format
- [ ] **Check video.log file**
  - [ ] Locate `video.log` in recording directory
  - [ ] Verify format: `frame_index: [N] pts_time:[X] perf_counter_ms:[Y]`
  - [ ] No corrupted lines
  - [ ] Frame count matches expected for duration

#### Large File Handling
- [ ] **Test with long recordings (10+ minutes)**
  - [ ] Record for 10+ minutes to create >500MB file
  - [ ] Remux should complete without timeout (timeout is 1200s / 20 min)
  - [ ] Console shows: `"✓ Remux successful! MP4: [X] MB"`
  - [ ] Final video plays correctly with accurate duration

### Error Handling

#### Graceful Fallbacks
- [ ] **Test encoder fallback**
  - [ ] Set invalid encoder: `TAGGR_FFMPEG_ENCODER=invalid_codec`
  - [ ] Verify warning in console and fallback to available encoder
  
- [ ] **Test with no GPU**
  - [ ] Disable GPU in Device Manager (or test on VM without GPU acceleration)
  - [ ] Verify fallback to `libx264` software encoding
  - [ ] Recording still works

---

## 🍎 macOS Testing

### Hardware Acceleration Detection

#### GPU Detection
- [ ] **Launch app and check console output**
  - [ ] Look for log: `"Detected GPU vendor: [Apple|AMD|Intel|NVIDIA]"`
  - [ ] Note detected GPU: _________________
  - [ ] On Apple Silicon (M1/M2/M3/M4): Should detect "Apple"
  - [ ] On Intel Mac: May detect Intel, AMD, or NVIDIA

#### Encoder Selection
- [ ] **Check encoder selection**
  - [ ] Expected encoder: `h264_videotoolbox` or `hevc_videotoolbox`
  - [ ] Note selected encoder: _________________
  - [ ] Look for log: `"Selected hardware encoder: [codec] (VideoToolbox [H.264|HEVC])"`
  - [ ] Reason should be: `"macOS VideoToolbox hardware acceleration"`

#### Encoder Override Test
- [ ] **Test environment variable override**
  ```bash
  export TAGGR_FFMPEG_ENCODER=libx264
  # Run Taggr
  ```
  - [ ] Verify override works
  - [ ] Recording completes with software encoder
  - [ ] Unset variable and verify VideoToolbox is used again

#### Encoder Preset Verification (macOS)
- [ ] **Check presets are applied**
  - [ ] VideoToolbox: No preset argument (uses default)
  - [ ] libx264 fallback: Should use `-preset ultrafast`
  - [ ] Check console logs for encoder arguments

### Recording Tests

#### Basic Recording
- [ ] **30-second test recording**
  - [ ] Recording starts without errors
  - [ ] Video file created successfully
  - [ ] Events and metadata files created
  - [ ] Video plays in QuickTime/VLC

#### VideoToolbox Performance
- [ ] **Compare encoding performance**
  - [ ] Record 1 min with VideoToolbox, note CPU% in Activity Monitor: _____
  - [ ] Record 1 min with libx264 (override), note CPU%: _____
  - [ ] VideoToolbox should be more efficient

#### macOS-Specific: Cursor Position via NSEvent
- [ ] **Test cursor coordinate accuracy**
  - [ ] Move cursor during recording
  - [ ] Check `events.jsonl` for:
    - [ ] `raw_x` and `raw_y` fields present
    - [ ] Coordinates are in correct range (not negative, within screen bounds)
  - [ ] Note: PTS timing may not be as precise as Windows (no native timing callback)

#### macOS-Specific: Frame Timing Fallback
- [ ] **Verify graceful fallback for PTS timing**
  - [ ] Check `events.jsonl` for:
    - [ ] `frame_pts_seconds` may be `null` or `-1` (expected on macOS)
    - [ ] `second_in_video` should still be present and calculated from timestamp
    - [ ] `frame_index` should still be present
  - [ ] No errors about missing frame timing
  - [ ] Recording should still work correctly

### Letterbox Testing

#### Aspect Ratio Handling
- [ ] **Test letterbox with resolution mismatch**
  - [ ] Record on Retina display with non-native video resolution
  - [ ] Check `metadata.json` for letterbox parameters
  - [ ] Verify coordinate mapping in `events.jsonl`
  - [ ] Click corners and verify coordinates map to visible area

#### Visual Letterbox Verification (macOS)
- [ ] **Check video output visually**
  - [ ] Open recorded `video.mp4` in QuickTime/VLC
  - [ ] Verify black bars visible if aspect ratio mismatch
  - [ ] Screen content is centered, no stretching or distortion
  - [ ] Screenshot any issues

#### Multi-Monitor (if available)
- [ ] **Test with external display**
  - [ ] Connect external monitor
  - [ ] Check console: `"Desktop dimensions via monitor bounding box: [W]x[H]"`
  - [ ] Verify total virtual desktop size in `metadata.json`
  - [ ] Move cursor across displays during recording
  - [ ] Verify coordinates span both displays

### System-Specific Checks

#### macOS Power Management
- [ ] **Check Low Power Mode detection (if on battery)**
  - [ ] Enable Low Power Mode in System Preferences
  - [ ] Launch app (should pass with warning if plugged in)
  - [ ] Check console for power state log

#### Retina Display Handling
- [ ] **Test on Retina/HiDPI display**
  - [ ] Verify screen dimensions detected correctly (not scaled)
  - [ ] Check `metadata.json` has physical pixels, not points
  - [ ] Coordinates should map to actual video pixels

---

## 🐧 Ubuntu/Linux Testing

### Hardware Acceleration Detection

#### GPU Detection
- [ ] **Launch app and check console output**
  - [ ] Look for log: `"Detected GPU vendor: [NVIDIA|AMD|Intel|Unknown]"`
  - [ ] Note detected GPU: _________________
  - [ ] Detection method:
    - [ ] via `lspci` command
    - [ ] Look for VGA/Display Controller entries

#### Encoder Selection
- [ ] **Check encoder selection**
  - [ ] NVIDIA GPU: Should select `h264_nvenc` or `hevc_nvenc`
  - [ ] Intel/AMD GPU: May select `h264_vaapi` or `hevc_vaapi`
  - [ ] Intel with QSV: `h264_qsv` or `hevc_qsv`
  - [ ] No GPU: `libx264` software fallback
  - [ ] Note selected encoder: _________________

#### VAAPI Device Detection (Intel/AMD)
- [ ] **Check for VAAPI render device**
  - [ ] Look for log: `"Found VAAPI device: /dev/dri/renderD128"`
  - [ ] If VAAPI selected, encoder args should include:
    - `-hwaccel vaapi`
    - `-vaapi_device /dev/dri/renderDXXX`

#### Encoder Override Test
- [ ] **Test environment variable override**
  ```bash
  export TAGGR_FFMPEG_ENCODER=libx264
  # Run Taggr
  ```
  - [ ] Verify override works
  - [ ] Unset and verify hardware encoder selected

#### Encoder Preset Verification (Linux)
- [ ] **Check presets are applied**
  - [ ] NVENC: Should use `-preset p1`
  - [ ] QSV: Should use `-preset veryfast`
  - [ ] VAAPI: No preset (uses default)
  - [ ] libx264 fallback: Should use `-preset ultrafast`
  - [ ] Check console logs for encoder arguments

### Recording Tests

#### Basic Recording
- [ ] **30-second test recording**
  - [ ] Recording starts successfully
  - [ ] Check for X11/Wayland capture working
  - [ ] Video file created
  - [ ] Events and metadata files created
  - [ ] Video plays in media player

#### Hardware Encoder Performance
- [ ] **Compare encoding CPU usage**
  - [ ] Record 1 min with hardware encoder, note CPU% in System Monitor: _____
  - [ ] Record 1 min with libx264 (override), note CPU%: _____
  - [ ] Hardware should use less CPU (if working)

#### Linux-Specific: Cursor Position
- [ ] **Test cursor tracking**
  - [ ] Move cursor during recording
  - [ ] Check `events.jsonl` for:
    - [ ] `raw_x` and `raw_y` fields present
    - [ ] Coordinates are valid (within screen bounds)
  - [ ] Note: Uses pynput fallback for cursor position

#### Linux-Specific: Frame Timing Fallback
- [ ] **Verify graceful fallback for PTS timing**
  - [ ] Check `events.jsonl` for:
    - [ ] `frame_pts_seconds` may be `null` or `-1` (expected on Linux)
    - [ ] `second_in_video` should still be present
    - [ ] `frame_index` should still be present
  - [ ] No errors about missing frame timing
  - [ ] Recording should still work correctly

### Letterbox Testing

#### Aspect Ratio Handling
- [ ] **Test letterbox with resolution mismatch**
  - [ ] Record with non-matching video resolution
  - [ ] Check `metadata.json` for letterbox parameters
  - [ ] Verify coordinate mapping
  - [ ] Click corners/edges during recording

#### Visual Letterbox Verification (Linux)
- [ ] **Check video output visually**
  - [ ] Open recorded `video.mp4` in media player
  - [ ] Verify black bars visible if aspect ratio mismatch
  - [ ] Screen content is centered, no stretching or distortion
  - [ ] Screenshot any issues

#### Multi-Monitor (if available)
- [ ] **Test with multiple displays**
  - [ ] Check console for desktop dimensions detection method
  - [ ] Verify `metadata.json` has correct total virtual desktop size
  - [ ] Move cursor across displays
  - [ ] Verify coordinates in `events.jsonl`

### Linux-Specific Considerations

#### X11 vs Wayland
- [ ] **Note display server in use:** [X11 / Wayland]
  - [ ] Check with: `echo $XDG_SESSION_TYPE`
  - [ ] Different behavior expected between X11 and Wayland

#### Permissions
- [ ] **Verify recording permissions**
  - [ ] Screen capture permission granted
  - [ ] Input monitoring permission granted
  - [ ] No permission errors in console

---

## 🌐 Cross-Platform Tests

### Dependency Verification

#### All Platforms
- [ ] **Verify py-cpuinfo is installed**
  ```bash
  python -c "import cpuinfo; print(cpuinfo.get_cpu_info().get('brand_raw', 'Unknown'))"
  ```
  - [ ] Should print CPU brand string (e.g., "Intel Core i7-10700K")
  - [ ] No import errors

- [ ] **Test CPU detection fallbacks**
  - [ ] Windows: If py-cpuinfo fails, should use WMI or PROCESSOR_IDENTIFIER
  - [ ] macOS: If py-cpuinfo fails, should use `sysctl -n machdep.cpu.brand_string`
  - [ ] Linux: If py-cpuinfo fails, should use `/proc/cpuinfo` or `lscpu`
  - [ ] Check console for CPU detection method used

---

### First-Frame Detection Speed

#### All Platforms
- [ ] **Verify recording starts quickly**
  - [ ] Press start recording button
  - [ ] Recording should start within ~100ms (improved from 50ms to 1ms sleep)
  - [ ] No noticeable delay between button press and recording indicator
  - [ ] First frame is captured promptly

---

### Metadata Validation

#### All Platforms
- [ ] **Check `metadata.json` structure**
  - [ ] Contains all required fields:
    ```json
    {
      "screen_width": ...,
      "screen_height": ...,
      "video_width": ...,
      "video_height": ...,
      "video_fps": 30,
      "letterbox_scale": ...,
      "letterbox_pad_x": ...,
      "letterbox_pad_y": ...,
      "letterbox_scaled_width": ...,
      "letterbox_scaled_height": ...,
      "scroll_direction": [-1 or 1],
      ...
    }
    ```

### Events.jsonl Validation

#### All Platforms
- [ ] **Check event structure**
  - [ ] All events have `time_stamp_ms`
  - [ ] All events have `frame_index`
  - [ ] All events have `second_in_video`
  - [ ] Mouse events have both scaled (`x`, `y`) and raw (`raw_x`, `raw_y`) coords
  - [ ] Windows: Events have `frame_pts_seconds` (non-null)
  - [ ] macOS/Linux: `frame_pts_seconds` may be null or -1

#### Event Coordinate Validation
- [ ] **Verify coordinate scaling**
  - [ ] Record and click in top-left corner (0, 0)
  - [ ] Record and click in bottom-right corner (max, max)
  - [ ] Check `events.jsonl`:
    - [ ] `raw_x`, `raw_y` = screen coordinates
    - [ ] `x`, `y` = video coordinates (scaled + padded)
  - [ ] With letterbox, verify padding offset is applied

### Video Codec Verification

#### All Platforms
- [ ] **Use ffprobe to check codec**
  ```bash
  ffprobe video.mp4 2>&1 | grep "Video:"
  ```
  - [ ] Windows (NVIDIA): Should show `h264 (Main)` from nvenc
  - [ ] Windows (AMD): Should show `h264 (Main)` from amf
  - [ ] Windows (Intel): Should show `h264 (Main)` from qsv
  - [ ] macOS: Should show `h264 (Main)` from VideoToolbox
  - [ ] Linux (NVIDIA): Should show `h264 (Main)` from nvenc
  - [ ] Linux (Intel/AMD): Should show `h264 (Main)` from vaapi
  - [ ] Software fallback: `h264 (High)` from libx264

---

### video.log Format Compatibility

#### Windows
- [ ] **Check video.log parsing**
  - [ ] Locate `video.log` in recording directory
  - [ ] Verify format is parseable
  - [ ] Code supports both `n:` and `frame_index:` prefixes for compatibility
  ```
  # Example format:
  frame_index: 0 pts_time:0.000000 perf_counter_ms:12345.678
  frame_index: 1 pts_time:0.033333 perf_counter_ms:12378.901
  ```

#### macOS / Linux
- [ ] **video.log may not exist or have different format**
  - [ ] If exists, verify it's parseable
  - [ ] No parsing errors in console

---

## 📋 Regression Testing

### Ensure Existing Features Still Work

#### All Platforms
- [ ] **Natural/reverse scrolling setting**
  - [ ] Toggle setting and verify `metadata.json` has correct `scroll_direction`
  
- [ ] **Task UUID and Slug**
  - [ ] Set task and verify in `metadata.json`

- [ ] **Keyboard events**
  - [ ] Press keys during recording
  - [ ] Verify `events.jsonl` has press/release events with correct key names
  - [ ] **NEW:** Verify keyboard events have cursor position:
    - [ ] `x`, `y` (scaled cursor position at key press/release)
    - [ ] `raw_x`, `raw_y` (screen cursor position)
  - [ ] This is an enhancement - keyboard events now include cursor position

- [ ] **Click events**
  - [ ] Left, right, middle click during recording
  - [ ] Verify button names in `events.jsonl`

- [ ] **Scroll events**
  - [ ] Scroll vertically and horizontally
  - [ ] Verify `dx`, `dy` values in `events.jsonl`

---

## 🐛 Known Issues / Edge Cases to Test

### All Platforms
- [ ] **Very short recordings (<1 second)**
  - [ ] Start recording
  - [ ] Immediately stop (<1 second)
  - [ ] Should handle gracefully (no crash)
  - [ ] Files may be minimal or empty (expected)

- [ ] **Very long recordings (>10 minutes)**
  - [ ] Check for memory leaks
  - [ ] Verify duration accuracy
  - [ ] Check file size is reasonable

- [ ] **Rapid start/stop**
  - [ ] Start and immediately stop recording
  - [ ] Should handle gracefully (no crash)

- [ ] **Recording during high CPU load**
  - [ ] Run stress test in background
  - [ ] Start recording
  - [ ] Check for frame drops or duration mismatch

### Windows-Specific
- [ ] **Desktop Duplication API edge cases**
  - [ ] Switch displays during recording (if multi-monitor)
  - [ ] Change resolution during recording
  - [ ] Should handle or fail gracefully

- [ ] **Media Foundation vs FFmpeg fallback**
  - [ ] Check console for: `"Using Media Foundation encoder"` or `"Falling back to FFmpeg"`
  - [ ] Both paths should work

### macOS-Specific
- [ ] **ScreenCaptureKit permissions**
  - [ ] Revoke and re-grant screen recording permission
  - [ ] App should request permission properly

### Linux-Specific
- [ ] **VAAPI permissions**
  - [ ] Check `/dev/dri/renderD*` permissions
  - [ ] User should have access to render devices

### FFmpeg Not Found (All Platforms)
- [ ] **Test when ffmpeg is unavailable**
  - [ ] Temporarily rename/remove ffmpeg from PATH
  - [ ] Launch app
  - [ ] Check console for: `"ffmpeg not found at: [path]"`
  - [ ] App should show appropriate error or fallback behavior
  - [ ] Restore ffmpeg to PATH after test

### Letterbox Invalid Dimensions (All Platforms)
- [ ] **Test internal edge case handling**
  - [ ] This is difficult to trigger manually
  - [ ] Verify in code that `_compute_letterbox_mapping()` handles:
    - [ ] Zero dimensions (should use 1:1 fallback)
    - [ ] Negative dimensions (should use 1:1 fallback)
  - [ ] Console warning: `"Invalid dimensions for letterbox mapping, using 1:1 fallback"`
  - [ ] App should not crash with unusual screen/video dimensions

---

## 📊 Performance Benchmarks

### Record Baseline Metrics

#### Windows
| Metric | Hardware Encoder | Software (libx264) |
|--------|------------------|--------------------|
| CPU % (idle) | | |
| CPU % (recording) | | |
| RAM usage | | |
| Recording duration | 60s | 60s |
| Output file size | | |
| Encoding time | | |

#### macOS
| Metric | VideoToolbox | Software (libx264) |
|--------|--------------|-------------------|
| CPU % (idle) | | |
| CPU % (recording) | | |
| RAM usage | | |
| Recording duration | 60s | 60s |
| Output file size | | |
| Encoding time | | |

#### Linux
| Metric | Hardware Encoder | Software (libx264) |
|--------|------------------|--------------------|
| CPU % (idle) | | |
| CPU % (recording) | | |
| RAM usage | | |
| Recording duration | 60s | 60s |
| Output file size | | |
| Encoding time | | |

---

## ✅ Final Verification

### Before Merging
- [ ] All critical tests passed on Windows
- [ ] All critical tests passed on macOS  
- [ ] All critical tests passed on Ubuntu
- [ ] No regressions in existing functionality
- [ ] Performance improvements documented
- [ ] Edge cases handled gracefully
- [ ] Console logs are clean (no unexpected errors/warnings)

### Documentation
- [ ] Update README if needed
- [ ] Document new environment variables:
  - `TAGGR_FFMPEG_ENCODER` - Override encoder selection
  - `TAGGR_SKIP_SYSTEM_REQUIREMENTS` - Skip hardware checks
  - `TAGGR_MIN_RAM_GB` - Minimum RAM requirement
- [ ] Document new metadata fields (letterbox_*)
- [ ] Document new event fields (frame_pts_seconds, raw_x, raw_y)

---

## 📝 Test Results Summary

### Windows
- **GPU:** _________________
- **Encoder:** _________________
- **Pass/Fail:** _________________
- **Notes:** 

### macOS
- **GPU:** _________________
- **Encoder:** _________________
- **Pass/Fail:** _________________
- **Notes:** 

### Ubuntu
- **GPU:** _________________
- **Encoder:** _________________
- **Pass/Fail:** _________________
- **Notes:** 

---

## 🔍 Debugging Tips

### If encoder detection fails:
```bash
# Check available encoders manually
ffmpeg -encoders | grep h264
ffmpeg -encoders | grep nvenc
ffmpeg -encoders | grep videotoolbox
ffmpeg -encoders | grep vaapi
ffmpeg -encoders | grep qsv
ffmpeg -encoders | grep amf
```

### If recording fails:
1. Check console for error messages
2. Check logs in recording output directory
3. Verify ffmpeg is accessible: `which ffmpeg` / `where ffmpeg`
4. Test ffmpeg directly with detected encoder

### If coordinates are wrong:
1. Check `metadata.json` letterbox values
2. Verify `screen_width/height` vs `video_width/height`
3. Calculate expected padding manually
4. Compare with actual event coordinates

### If duration mismatch occurs:
1. Check console for PTS warnings
2. Verify `video.log` entries (Windows)
3. Use ffprobe to check actual video duration
4. Look for frame drop warnings

### Check CPU detection:
```bash
# Test py-cpuinfo
python -c "import cpuinfo; print(cpuinfo.get_cpu_info().get('brand_raw', 'Unknown'))"

# macOS fallback
sysctl -n machdep.cpu.brand_string

# Linux fallback
cat /proc/cpuinfo | grep "model name" | head -1
lscpu | grep "Model name"

# Windows fallback
echo %PROCESSOR_IDENTIFIER%
```

### Check GPU vendor:
```bash
# Windows (PowerShell)
Get-WmiObject Win32_VideoController | Select-Object Name

# macOS
system_profiler SPDisplaysDataType | grep "Chipset Model"

# Linux
lspci | grep -i vga
```

### Check VAAPI device (Linux):
```bash
ls -la /dev/dri/renderD*
vainfo  # If vainfo is installed
```

### Inspect video.log:
```bash
# Check first few lines
head -10 video.log

# Count total frames
wc -l video.log

# Check for format consistency
grep -c "frame_index:" video.log
```

### Verify event fields:
```bash
# Check if events have new fields
head -1 events.jsonl | python -m json.tool

# Count events with frame_pts_seconds
grep -c "frame_pts_seconds" events.jsonl

# Check for raw coordinates
grep -c "raw_x" events.jsonl
```

---

**Testing Date:** _________________  
**Tester:** _________________  
**Branch Commit:** _________________

