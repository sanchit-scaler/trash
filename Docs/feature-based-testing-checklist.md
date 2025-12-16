# Feature-Based Testing Checklist: `feat/hwaccel-sysreq-hybuf-letterbox`

## Overview
Testing checklist organized by feature, with OS-specific tests as subsections.

**Branch:** `feat/hwaccel-sysreq-hybuf-letterbox`  
**Test Machines:** Windows, macOS, Ubuntu  
**Build Mode:** Dev mode with console  
**Already Tested:** ✅ System Requirements Check

---

## 🚀 Feature 1: Hardware Acceleration Detection & Encoder Selection

### Overview
Tests GPU detection and automatic encoder selection based on available hardware.

### 1.1 GPU Vendor Detection

#### 🪟 Windows
- [ ] Launch app and check console log
- [ ] Look for: `"Detected GPU vendor: [NVIDIA|AMD|Intel|Unknown]"`
- [ ] Detection method: WMI or driver path detection
- [ ] Note detected GPU: _________________
- [ ] **Expected vendors:**
  - NVIDIA (GeForce, RTX, GTX, Quadro)
  - AMD (Radeon)
  - Intel (Integrated graphics)

#### 🍎 macOS
- [ ] Launch app and check console log
- [ ] Look for: `"Detected GPU vendor: [Apple|AMD|Intel|NVIDIA]"`
- [ ] Detection method: `system_profiler SPDisplaysDataType` or `sysctl`
- [ ] Note detected GPU: _________________
- [ ] **Expected vendors:**
  - Apple (M1/M2/M3/M4 Silicon)
  - AMD (Intel Macs with discrete GPU)
  - Intel (Intel Macs with integrated GPU)

#### 🐧 Ubuntu/Linux
- [ ] Launch app and check console log
- [ ] Look for: `"Detected GPU vendor: [NVIDIA|AMD|Intel|Unknown]"`
- [ ] Detection method: `lspci` command
- [ ] Note detected GPU: _________________
- [ ] Verify detection with: `lspci | grep -i vga`
- [ ] **Expected vendors:**
  - NVIDIA
  - AMD/ATI
  - Intel

---

### 1.2 Encoder Selection

#### 🪟 Windows
- [ ] Check console for: `"Selected hardware encoder: [codec] ([type])"`
- [ ] Note selected encoder: _________________
- [ ] **Expected by GPU:**
  - **NVIDIA:** `h264_nvenc` or `hevc_nvenc`
    - [ ] Log should say: "NVIDIA GPU detected, using NVENC acceleration"
  - **AMD:** `h264_amf` or `hevc_amf`
    - [ ] Log should say: "AMD GPU detected, using AMF acceleration"
  - **Intel:** `h264_qsv` or `hevc_qsv`
    - [ ] Log should say: "Intel GPU detected, using QSV acceleration"
  - **No GPU/Unknown:** `libx264` (software)
    - [ ] Log should say: "No hardware encoder available, using software encoding"

#### 🍎 macOS
- [ ] Check console for: `"Selected hardware encoder: [codec] (VideoToolbox [H.264|HEVC])"`
- [ ] Note selected encoder: _________________
- [ ] **Expected:**
  - `h264_videotoolbox` or `hevc_videotoolbox`
  - [ ] Reason: "macOS VideoToolbox hardware acceleration"
- [ ] **Fallback:** `libx264` if VideoToolbox unavailable

#### 🐧 Ubuntu/Linux
- [ ] Check console for encoder selection log
- [ ] Note selected encoder: _________________
- [ ] **Expected by GPU:**
  - **NVIDIA:** `h264_nvenc` or `hevc_nvenc`
    - [ ] Requires NVIDIA drivers installed
  - **Intel/AMD:** `h264_vaapi` or `hevc_vaapi`
    - [ ] Look for: `"Found VAAPI device: /dev/dri/renderD128"`
    - [ ] Extra args should include: `-hwaccel vaapi -vaapi_device /dev/dri/renderDXXX`
  - **Intel with QSV:** `h264_qsv` or `hevc_qsv`
  - **Fallback:** `libx264` (software)

---

### 1.3 Encoder Override via Environment Variable

#### 🪟 Windows
- [ ] Set override:
  ```cmd
  set TAGGR_FFMPEG_ENCODER=libx264
  ```
- [ ] Launch app
- [ ] Look for log: `"Using encoder from TAGGR_FFMPEG_ENCODER: libx264"`
- [ ] Start recording
- [ ] Recording completes successfully
- [ ] Remove override and verify hardware encoder is used again

#### 🍎 macOS
- [ ] Set override:
  ```bash
  export TAGGR_FFMPEG_ENCODER=libx264
  ```
- [ ] Launch app
- [ ] Look for log: `"Using encoder from TAGGR_FFMPEG_ENCODER: libx264"`
- [ ] Start recording
- [ ] Recording completes successfully
- [ ] Unset and verify VideoToolbox is used again

#### 🐧 Ubuntu/Linux
- [ ] Set override:
  ```bash
  export TAGGR_FFMPEG_ENCODER=libx264
  ```
- [ ] Launch app
- [ ] Look for log: `"Using encoder from TAGGR_FFMPEG_ENCODER: libx264"`
- [ ] Start recording
- [ ] Recording completes successfully
- [ ] Unset and verify hardware encoder is used again

---

### 1.4 Encoder Performance Comparison

#### 🪟 Windows
- [ ] **Hardware encoder test:**
  - [ ] Remove any encoder override
  - [ ] Start recording for 60 seconds
  - [ ] Open Task Manager → Performance
  - [ ] Note CPU usage: _____%
  - [ ] Note GPU usage (if available): _____%
  - [ ] Recording completes successfully
  
- [ ] **Software encoder test:**
  - [ ] Set `TAGGR_FFMPEG_ENCODER=libx264`
  - [ ] Start recording for 60 seconds
  - [ ] Note CPU usage: _____%
  - [ ] Recording completes successfully
  
- [ ] **Comparison:**
  - [ ] Hardware should use significantly less CPU (30-50% less)
  - [ ] Hardware may show GPU usage increase

#### 🍎 macOS
- [ ] **VideoToolbox test:**
  - [ ] Remove any encoder override
  - [ ] Start recording for 60 seconds
  - [ ] Open Activity Monitor
  - [ ] Note CPU usage: _____%
  - [ ] Recording completes successfully
  
- [ ] **Software encoder test:**
  - [ ] Set `TAGGR_FFMPEG_ENCODER=libx264`
  - [ ] Start recording for 60 seconds
  - [ ] Note CPU usage: _____%
  - [ ] Recording completes successfully
  
- [ ] **Comparison:**
  - [ ] VideoToolbox should be more efficient

#### 🐧 Ubuntu/Linux
- [ ] **Hardware encoder test:**
  - [ ] Remove any encoder override
  - [ ] Start recording for 60 seconds
  - [ ] Open System Monitor
  - [ ] Note CPU usage: _____%
  - [ ] Recording completes successfully
  
- [ ] **Software encoder test:**
  - [ ] Set `TAGGR_FFMPEG_ENCODER=libx264`
  - [ ] Start recording for 60 seconds
  - [ ] Note CPU usage: _____%
  - [ ] Recording completes successfully
  
- [ ] **Comparison:**
  - [ ] Hardware should use less CPU (if working properly)

---

### 1.5 Video Codec Verification

#### 🪟 Windows
- [ ] Use ffprobe to verify codec:
  ```cmd
  ffprobe video.mp4 2>&1 | findstr "Video:"
  ```
- [ ] Expected output based on GPU:
  - NVIDIA: `h264 (Main)` or similar from nvenc
  - AMD: `h264 (Main)` from amf
  - Intel: `h264 (Main)` from qsv
  - Software: `h264 (High)` from libx264

#### 🍎 macOS
- [ ] Use ffprobe to verify codec:
  ```bash
  ffprobe video.mp4 2>&1 | grep "Video:"
  ```
- [ ] Expected: `h264 (Main)` from VideoToolbox or `h264 (High)` from libx264

#### 🐧 Ubuntu/Linux
- [ ] Use ffprobe to verify codec:
  ```bash
  ffprobe video.mp4 2>&1 | grep "Video:"
  ```
- [ ] Expected output based on GPU:
  - NVIDIA: `h264 (Main)` from nvenc
  - Intel/AMD: `h264 (Main)` from vaapi
  - Software: `h264 (High)` from libx264

---

### 1.6 Encoder Preset Verification

#### All Platforms (🪟 🍎 🐧)
- [ ] After recording, check ffmpeg command logs for correct presets:
  - [ ] **NVENC:** Should include `-preset p1`
  - [ ] **QSV:** Should include `-preset veryfast`
  - [ ] **libx264/libx265:** Should include `-preset ultrafast`
  - [ ] **AMF/VAAPI/VideoToolbox:** No preset argument (uses default)
- [ ] Verify in console logs that preset is applied

---

### 1.7 FFmpeg Encoder Query

#### All Platforms (🪟 🍎 🐧)
- [ ] Check console for: `"Available video encoders: [...]"`
- [ ] Verify ffmpeg is queried successfully (no timeout warning)
- [ ] If ffmpeg not found, should see: `"ffmpeg not found at: [path]"`
- [ ] Verify encoder query completes in <10 seconds

---

## 🎯 Feature 2: Letterbox-Aware Coordinate Mapping

### Overview
Tests proper coordinate scaling when video aspect ratio doesn't match screen aspect ratio.

### 2.1 Letterbox Metadata Generation

#### 🪟 Windows
- [ ] Set video resolution to create aspect ratio mismatch:
  - Example: Video 1280x720 (16:9) on 1920x1200 monitor (16:10)
- [ ] Start and stop recording
- [ ] Open `metadata.json`
- [ ] Verify letterbox fields exist:
  ```json
  {
    "screen_width": 1920,
    "screen_height": 1200,
    "video_width": 1280,
    "video_height": 720,
    "letterbox_scale": 0.6,
    "letterbox_pad_x": 0,
    "letterbox_pad_y": 120,
    "letterbox_scaled_width": 1280,
    "letterbox_scaled_height": 720
  }
  ```
- [ ] Note letterbox values: _________________

#### 🍎 macOS
- [ ] Set video resolution to create aspect ratio mismatch
- [ ] Start and stop recording
- [ ] Open `metadata.json`
- [ ] Verify letterbox fields exist
- [ ] Note letterbox values: _________________
- [ ] On Retina displays, verify dimensions use physical pixels

#### 🐧 Ubuntu/Linux
- [ ] Set video resolution to create aspect ratio mismatch
- [ ] Start and stop recording
- [ ] Open `metadata.json`
- [ ] Verify letterbox fields exist
- [ ] Note letterbox values: _________________

---

### 2.2 Coordinate Scaling Validation

#### 🪟 Windows
- [ ] With letterbox setup from 2.1:
- [ ] During recording, click at:
  - [ ] **Top-left corner** (approximately 0, 0)
  - [ ] **Top-right corner** (screen_width, 0)
  - [ ] **Bottom-left corner** (0, screen_height)
  - [ ] **Bottom-right corner** (screen_width, screen_height)
  - [ ] **Center** (screen_width/2, screen_height/2)
- [ ] Stop recording and open `events.jsonl`
- [ ] For each click event, verify:
  - [ ] `raw_x`, `raw_y` = actual screen coordinates
  - [ ] `x`, `y` = scaled coordinates with padding
  - [ ] Formula check: `x = raw_x * letterbox_scale + letterbox_pad_x`
  - [ ] Formula check: `y = raw_y * letterbox_scale + letterbox_pad_y`

#### 🍎 macOS
- [ ] With letterbox setup from 2.1:
- [ ] During recording, click at corners and center
- [ ] Stop recording and open `events.jsonl`
- [ ] Verify coordinate transformation:
  - [ ] `raw_x`, `raw_y` present
  - [ ] `x`, `y` correctly scaled with padding
  - [ ] Coordinates map to visible video area (not black bars)

#### 🐧 Ubuntu/Linux
- [ ] With letterbox setup from 2.1:
- [ ] During recording, click at corners and center
- [ ] Stop recording and open `events.jsonl`
- [ ] Verify coordinate transformation:
  - [ ] `raw_x`, `raw_y` present
  - [ ] `x`, `y` correctly scaled with padding
  - [ ] Coordinates map to visible video area

---

### 2.3 Visual Letterbox Verification

#### 🪟 Windows
- [ ] Open recorded `video.mp4` in VLC/media player
- [ ] With aspect ratio mismatch, verify:
  - [ ] Black bars visible (top/bottom OR left/right)
  - [ ] Screen content is centered
  - [ ] No stretching or distortion of content
- [ ] Screenshot any issues

#### 🍎 macOS
- [ ] Open recorded `video.mp4` in QuickTime/VLC
- [ ] With aspect ratio mismatch, verify:
  - [ ] Black bars visible (top/bottom OR left/right)
  - [ ] Screen content is centered
  - [ ] No stretching or distortion
- [ ] Screenshot any issues

#### 🐧 Ubuntu/Linux
- [ ] Open recorded `video.mp4` in media player
- [ ] With aspect ratio mismatch, verify:
  - [ ] Black bars visible (top/bottom OR left/right)
  - [ ] Screen content is centered
  - [ ] No stretching or distortion
- [ ] Screenshot any issues

---

### 2.4 Letterbox Edge Cases

#### All Platforms (🪟 🍎 🐧)
- [ ] **Same aspect ratio test:**
  - [ ] Set video resolution to match screen aspect ratio (e.g., both 16:9)
  - [ ] Verify `letterbox_pad_x` and `letterbox_pad_y` are both 0 (or minimal)
  - [ ] No black bars in video
  
- [ ] **Extreme aspect ratio mismatch:**
  - [ ] Test with very different ratios (e.g., 4:3 screen, 16:9 video)
  - [ ] Verify letterbox calculation handles correctly
  - [ ] Visual: Black bars should be on correct sides
  
- [ ] **Verify formula matches ffmpeg:**
  - [ ] Check that `letterbox_scale = min(video_w/screen_w, video_h/screen_h)`
  - [ ] Check that `pad_x = (video_w - scaled_w) // 2` (integer division)
  - [ ] Check that `pad_y = (video_h - scaled_h) // 2` (integer division)

---

## 🖥️ Feature 3: Multi-Monitor Virtual Desktop Dimensions

### Overview
Tests proper detection of total virtual desktop size across multiple monitors.

### 3.1 Desktop Dimensions Detection

#### 🪟 Windows
- [ ] **Single monitor test:**
  - [ ] Launch app with one monitor
  - [ ] Look for console log: `"Desktop dimensions via GetSystemMetrics: [W]x[H]"`
  - [ ] Note dimensions: _________________
  - [ ] Should match monitor resolution

- [ ] **Multi-monitor test (if available):**
  - [ ] Connect second monitor (different position: left/right/above/below)
  - [ ] Launch app
  - [ ] Look for console log: `"Desktop dimensions via GetSystemMetrics: [W]x[H]"`
  - [ ] Note dimensions: _________________
  - [ ] Should be total virtual screen size (e.g., 3840x1080 for two 1920x1080 side-by-side)
  - [ ] Open `metadata.json` and verify:
    ```json
    {
      "screen_width": [total width],
      "screen_height": [total height]
    }
    ```

#### 🍎 macOS
- [ ] **Single monitor test:**
  - [ ] Launch app with built-in display only
  - [ ] Check console for desktop dimensions detection method
  - [ ] Note dimensions: _________________

- [ ] **Multi-monitor test (if available):**
  - [ ] Connect external display
  - [ ] Launch app
  - [ ] Look for console log: `"Desktop dimensions via monitor bounding box: [W]x[H]"`
  - [ ] Note dimensions: _________________
  - [ ] Should span both displays
  - [ ] Open `metadata.json` and verify screen dimensions

#### 🐧 Ubuntu/Linux
- [ ] **Single monitor test:**
  - [ ] Launch app with one monitor
  - [ ] Check console for desktop dimensions detection
  - [ ] Note dimensions: _________________

- [ ] **Multi-monitor test (if available):**
  - [ ] Configure multi-monitor setup in display settings
  - [ ] Launch app
  - [ ] Check console for detection method
  - [ ] Note dimensions: _________________
  - [ ] Verify with: `xrandr` (X11) or display settings
  - [ ] Open `metadata.json` and verify screen dimensions

---

### 3.2 Cross-Monitor Coordinate Tracking

#### 🪟 Windows (Multi-monitor required)
- [ ] Start recording
- [ ] Move cursor from primary monitor to secondary monitor
- [ ] Click on each monitor
- [ ] Scroll on each monitor
- [ ] Stop recording
- [ ] Open `events.jsonl` and verify:
  - [ ] `raw_x`, `raw_y` coordinates span full virtual desktop
  - [ ] Negative coordinates if secondary monitor is positioned left/above primary
  - [ ] Coordinates exceed primary monitor size when on secondary

#### 🍎 macOS (Multi-monitor required)
- [ ] Start recording
- [ ] Move cursor across both displays
- [ ] Click on each display
- [ ] Stop recording
- [ ] Open `events.jsonl` and verify:
  - [ ] Coordinates span full virtual desktop
  - [ ] Coordinate system is consistent

#### 🐧 Ubuntu/Linux (Multi-monitor required)
- [ ] Start recording
- [ ] Move cursor across both monitors
- [ ] Click on each monitor
- [ ] Stop recording
- [ ] Open `events.jsonl` and verify:
  - [ ] Coordinates span full virtual desktop
  - [ ] X11 vs Wayland coordinate systems handled correctly

---

### 3.3 Negative Coordinate Handling (Multi-monitor)

#### 🪟 Windows (Multi-monitor required)
- [ ] **Test monitor positioned LEFT of primary:**
  - [ ] Position secondary monitor to the LEFT in Display Settings
  - [ ] Start recording
  - [ ] Move cursor to secondary monitor (left side)
  - [ ] Click and scroll on secondary
  - [ ] Stop recording
  - [ ] Open `events.jsonl`
  - [ ] Verify `raw_x` values are NEGATIVE for actions on secondary monitor
  - [ ] Verify coordinates still scale correctly with letterbox mapping

- [ ] **Test monitor positioned ABOVE primary:**
  - [ ] Position secondary monitor ABOVE in Display Settings
  - [ ] Repeat above test
  - [ ] Verify `raw_y` values are NEGATIVE for actions on secondary monitor

#### 🍎 macOS (Multi-monitor required)
- [ ] Similar test with external display positioned left/above
- [ ] Verify coordinate system handles negative values correctly

#### 🐧 Ubuntu/Linux (Multi-monitor required)
- [ ] Configure monitor position in display settings
- [ ] Verify coordinate handling with negative positions

---

## ⏱️ Feature 4: PTS-Based Event Timing

### Overview
Tests frame PTS (presentation timestamp) synchronization for precise event timing.

### 4.1 Frame Timing Callback

#### 🪟 Windows
- [ ] This feature is **fully supported** on Windows
- [ ] Start recording
- [ ] During recording, check console doesn't show frame timing errors
- [ ] Perform various actions (click, move, scroll, type)
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Verify ALL events have:
  - [ ] `frame_pts_seconds` field (should be a float, not null)
  - [ ] `second_in_video` field matches `frame_pts_seconds`
  - [ ] Values increase monotonically
- [ ] Sample event structure:
  ```json
  {
    "time_stamp_ms": 12345.67,
    "frame_index": 42,
    "frame_pts_seconds": 1.234,
    "second_in_video": 1.234,
    "action": "move",
    "x": 960, "y": 540,
    "raw_x": 1920, "raw_y": 1080
  }
  ```

#### 🍎 macOS
- [ ] This feature is **partially supported** on macOS
- [ ] Start recording
- [ ] Perform various actions
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Check events:
  - [ ] `frame_pts_seconds` may be null or -1 (not fully wired up)
  - [ ] `second_in_video` calculated from timestamp instead
  - [ ] `frame_index` should still be present
  - [ ] Timing should still be reasonably accurate

#### 🐧 Ubuntu/Linux
- [ ] This feature is **partially supported** on Linux
- [ ] Start recording
- [ ] Perform various actions
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Check events:
  - [ ] `frame_pts_seconds` may be null or -1
  - [ ] `second_in_video` calculated from timestamp instead
  - [ ] `frame_index` should still be present
  - [ ] Timing should still be reasonably accurate

---

### 4.2 Duration Accuracy

#### 🪟 Windows
- [ ] Record for exactly 60 seconds (use timer)
- [ ] Stop recording
- [ ] Check console logs for:
  - [ ] `"Capture duration: [X]s"` - should be ~60s
  - [ ] `"encoded duration before scaling: [X]s"` - should be ~60s
  - [ ] Look for warnings: `"Duration mismatch detected"` (difference should be <1s)
- [ ] Use ffprobe to check actual duration:
  ```cmd
  ffprobe video.mp4 2>&1 | findstr "Duration"
  ```
- [ ] Duration should be 60s ±1s

#### 🍎 macOS
- [ ] Record for exactly 60 seconds
- [ ] Stop recording
- [ ] Check console logs for duration information
- [ ] Use ffprobe to check actual duration:
  ```bash
  ffprobe video.mp4 2>&1 | grep "Duration"
  ```
- [ ] Duration should be 60s ±1-2s (less precise than Windows)

#### 🐧 Ubuntu/Linux
- [ ] Record for exactly 60 seconds
- [ ] Stop recording
- [ ] Check console logs for duration information
- [ ] Use ffprobe to check actual duration:
  ```bash
  ffprobe video.mp4 2>&1 | grep "Duration"
  ```
- [ ] Duration should be 60s ±1-2s

---

### 4.3 video.log Format Compatibility

#### 🪟 Windows
- [ ] After recording, locate `video.log` file in recording directory
- [ ] Open `video.log` and verify format:
  ```
  # Frame timing log
  frame_index: 0 pts_time:0.000000 perf_counter_ms:12345.678
  frame_index: 1 pts_time:0.033333 perf_counter_ms:12378.901
  ...
  ```
- [ ] Verify file is parseable (no corrupted lines)
- [ ] Check console doesn't show video.log parsing errors

#### 🍎 macOS / 🐧 Ubuntu/Linux
- [ ] `video.log` may use different format or may not exist
- [ ] If exists, verify it's parseable
- [ ] Code supports both `n:` and `frame_index:` prefixes for compatibility

---

### 4.4 Frame Timing Fallback

#### 🍎 macOS / 🐧 Ubuntu/Linux
- [ ] Verify graceful fallback when `get_current_frame_timing()` returns -1
- [ ] Events should still have valid `second_in_video` (calculated from timestamp)
- [ ] `frame_pts_seconds` should be `null` or not present
- [ ] No errors or warnings about missing frame timing
- [ ] Recording should still work correctly

---

## 🖱️ Feature 5: Cursor Position at Frame Capture Time (Hybrid Buffer)

### Overview
Tests cursor synchronization by capturing cursor position at exact frame capture moment.

### 5.1 Cursor Position Capture

#### 🪟 Windows
- [ ] This is a **Windows-only feature**
- [ ] Check that `windows_screen_recorder.py` has been modified
- [ ] Start recording
- [ ] Move cursor rapidly in circles and figure-8 patterns
- [ ] Stop recording immediately
- [ ] Play back video
- [ ] Verify cursor movement is:
  - [ ] **Smooth** (no jitter)
  - [ ] **Synchronized** with video frame
  - [ ] **Not laggy** (cursor doesn't lag behind actual position)
- [ ] Check console for: `"None-frame count from dxcam: [X]"` (should be low)

#### 🍎 macOS
- [ ] This feature is **not implemented** on macOS
- [ ] Recording should still work normally
- [ ] Cursor tracking uses live position query (existing behavior)
- [ ] No `cursor_pos` in frame payload

#### 🐧 Ubuntu/Linux
- [ ] This feature is **not implemented** on Linux
- [ ] Recording should still work normally
- [ ] Cursor tracking uses live position query (existing behavior)
- [ ] No `cursor_pos` in frame payload

---

### 5.2 Cursor Coordinate Accuracy

#### 🪟 Windows
- [ ] Start recording
- [ ] Slowly move cursor to each screen corner
- [ ] Pause briefly at each corner
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] For events at corners, verify:
  - [ ] `raw_x`, `raw_y` match actual screen coordinates
  - [ ] Coordinates captured at frame time (not delayed)
  - [ ] Check console logs don't show cursor position errors

---

### 5.3 Capture Metrics Logging (Windows Only)

#### 🪟 Windows
- [ ] After recording completes, check console for capture metrics:
  - [ ] `"None-frame count from dxcam: [X]"` 
    - Should be low (<5% of total frames)
    - High count indicates capture issues
  - [ ] `"Frame queue stalled [X] times waiting for encoder"`
    - Should be 0 ideally
    - Non-zero indicates encoder bottleneck
- [ ] Note metrics: None-frames: _____ Queue stalls: _____

#### 🍎 macOS / 🐧 Ubuntu/Linux
- [ ] These metrics are Windows-specific
- [ ] No such logs expected on these platforms

---

### 5.4 Cursor Sprite with Position Override

#### 🪟 Windows
- [ ] Verify cursor is drawn at the captured position (not live position)
- [ ] During fast cursor movement, cursor in video should match frame capture time
- [ ] No "cursor trailing" effect (cursor should not appear behind actual position)

#### 🍎 macOS
- [ ] Start recording
- [ ] Move cursor to corners
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Verify:
  - [ ] `raw_x`, `raw_y` present and reasonable
  - [ ] Uses NSEvent.mouseLocation for position
  - [ ] Coordinates within screen bounds

#### 🐧 Ubuntu/Linux
- [ ] Start recording
- [ ] Move cursor to corners
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Verify:
  - [ ] `raw_x`, `raw_y` present and reasonable
  - [ ] Uses pynput for position
  - [ ] Coordinates within screen bounds

---

## 📄 Feature 6: Enhanced Event Structure

### Overview
Tests new event fields (raw coordinates, PTS, etc.) across all event types.

### 6.1 Mouse Move Events

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording
- [ ] Move mouse around screen
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Find `"action": "move"` events
- [ ] Verify each has:
  - [ ] `time_stamp_ms` (float)
  - [ ] `frame_index` (int)
  - [ ] `frame_pts_seconds` (float or null)
  - [ ] `second_in_video` (float)
  - [ ] `x`, `y` (scaled coordinates)
  - [ ] `raw_x`, `raw_y` (screen coordinates)

---

### 6.2 Mouse Click Events

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording
- [ ] Perform clicks:
  - [ ] Left click
  - [ ] Right click
  - [ ] Middle click (if available)
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Find `"action": "click"` events
- [ ] Verify each has:
  - [ ] `time_stamp_ms`
  - [ ] `frame_index`
  - [ ] `frame_pts_seconds` (float or null)
  - [ ] `second_in_video`
  - [ ] `x`, `y` (scaled)
  - [ ] `raw_x`, `raw_y` (screen)
  - [ ] `button` ("left", "right", "middle")
  - [ ] `pressed` (true or false)

---

### 6.3 Scroll Events

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording
- [ ] Scroll vertically (up and down)
- [ ] Scroll horizontally (if supported)
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Find `"action": "scroll"` events
- [ ] Verify each has:
  - [ ] `time_stamp_ms`
  - [ ] `frame_index`
  - [ ] `frame_pts_seconds` (float or null)
  - [ ] `second_in_video`
  - [ ] `x`, `y` (scaled)
  - [ ] `raw_x`, `raw_y` (screen)
  - [ ] `dx`, `dy` (scroll deltas)

---

### 6.3.1 Windows Trackpad Scroll Events

#### 🪟 Windows Only
- [ ] Use a trackpad (laptop or external) to scroll
- [ ] Start recording
- [ ] Perform two-finger scroll gestures
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Verify trackpad scroll events have:
  - [ ] Same structure as regular scroll events
  - [ ] `frame_pts_seconds` present (Windows has full PTS support)
  - [ ] Correct `dx`, `dy` values for gesture direction
- [ ] Trackpad scroll callback uses same frame timing as mouse scroll

---

### 6.4 Keyboard Events

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording
- [ ] Type some keys and key combinations
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Find `"action": "press"` and `"action": "release"` events
- [ ] **NEW:** Verify keyboard events now have:
  - [ ] `time_stamp_ms`
  - [ ] `frame_index`
  - [ ] `frame_pts_seconds` (float or null)
  - [ ] `second_in_video`
  - [ ] `name` (key name)
  - [ ] **NEW:** `x`, `y` (scaled cursor position at key press/release)
  - [ ] **NEW:** `raw_x`, `raw_y` (screen cursor position)
- [ ] This is a new enhancement - keyboard events now include cursor position

---

## 🔄 Feature 7: Regression Testing

### Overview
Ensures existing functionality still works correctly.

### 7.1 Basic Recording Flow

#### All Platforms (🪟 🍎 🐧)
- [ ] Launch app
- [ ] App starts without crashes
- [ ] UI loads properly
- [ ] Start recording button works
- [ ] Recording indicator shows
- [ ] Stop recording button works
- [ ] Files are generated:
  - [ ] `video.mp4`
  - [ ] `events.jsonl`
  - [ ] `metadata.json`
- [ ] Video plays correctly
- [ ] No corruption in files

---

### 7.2 Natural Scrolling Setting

#### All Platforms (🪟 🍎 🐧)
- [ ] Set natural scrolling ON
- [ ] Start recording
- [ ] Scroll vertically
- [ ] Stop recording
- [ ] Check `metadata.json`:
  - [ ] `"scroll_direction": -1`
  
- [ ] Set natural scrolling OFF
- [ ] Start recording
- [ ] Stop recording
- [ ] Check `metadata.json`:
  - [ ] `"scroll_direction": 1`

---

### 7.3 Task UUID and Slug

#### All Platforms (🪟 🍎 🐧)
- [ ] Set task UUID and slug before recording
- [ ] Start and stop recording
- [ ] Open `metadata.json`
- [ ] Verify presence of:
  - [ ] `"task_uuid": "[uuid]"`
  - [ ] `"task_slug": "[slug]"`

---

### 7.4 All Event Types Captured

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording
- [ ] Perform various actions:
  - [ ] Mouse movements
  - [ ] Left clicks
  - [ ] Right clicks
  - [ ] Scrolling
  - [ ] Key presses
  - [ ] Key releases
- [ ] Stop recording
- [ ] Open `events.jsonl`
- [ ] Verify all event types are captured
- [ ] No missing or duplicate events

---

## 🔧 Feature 8: Windows Recording Improvements

### Overview
Tests Windows-specific recording enhancements including duration validation, large file handling, and improved timeouts.

### 8.1 Duration Validation Warnings

#### 🪟 Windows Only
- [ ] Record for 2+ minutes
- [ ] Stop recording
- [ ] Check console logs for duration validation:
  - [ ] `"Capture duration: [X]s"` - capture PTS duration
  - [ ] `"encoded duration before scaling: [X]s"` - MKV duration before remux
  - [ ] Look for: `"Duration mismatch detected: capture=[X]s vs encoded=[X]s (difference: [X]s)"`
    - This warning should NOT appear for normal recordings
    - If it appears, difference should be <1s
  - [ ] After remux, look for: `"Output duration mismatch: expected ~[X]s, got [X]s"`
    - This warning should NOT appear
- [ ] Final MP4 duration should match capture duration (±1s)

---

### 8.2 Large File Handling

#### 🪟 Windows Only
- [ ] Record for 10+ minutes to create large file (>500MB)
- [ ] Monitor console during recording:
  - [ ] No queue stall warnings
  - [ ] Frame timing continues working
- [ ] After recording:
  - [ ] Remux should complete successfully
  - [ ] No timeout errors (timeout is 1200s / 20 minutes)
  - [ ] Console shows: `"✓ Remux successful! MP4: [X] MB"`
- [ ] Final video:
  - [ ] Plays correctly
  - [ ] Duration is accurate
  - [ ] No corruption

---

### 8.3 Extended Timeouts

#### 🪟 Windows Only
- [ ] **Remux timeout (1200s):**
  - [ ] For very large files, remux should not timeout
  - [ ] Stream copy is fast, but slow disks may need extra time
  
- [ ] **FFmpeg probe timeout (60s for large files):**
  - [ ] Duration detection should work for large files
  - [ ] No timeout warnings during `_get_video_duration_seconds()`

---

### 8.4 First-Frame Detection Speed

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording and measure time to recording indicator
- [ ] **Expected:** Recording should start within 100ms of button press
- [ ] **Improvement:** Sleep reduced from 50ms to 1ms for responsive detection
- [ ] No noticeable delay between button press and recording start

---

## 📦 Feature 9: Dependency Verification

### Overview
Tests that new dependencies are installed and working correctly.

### 9.1 py-cpuinfo Installation

#### All Platforms (🪟 🍎 🐧)
- [ ] Verify py-cpuinfo is installed:
  ```bash
  python -c "import cpuinfo; print(cpuinfo.get_cpu_info().get('brand_raw', 'Unknown'))"
  ```
- [ ] Should print CPU brand string (e.g., "Intel Core i7-10700K")
- [ ] No import errors

#### 🪟 Windows
- [ ] If py-cpuinfo fails, fallback to WMI or PROCESSOR_IDENTIFIER env var
- [ ] Check console for: `"CPU detected via WMI: [brand]"` or similar

#### 🍎 macOS
- [ ] If py-cpuinfo fails, fallback to `sysctl -n machdep.cpu.brand_string`
- [ ] Check console for: `"CPU detected via sysctl: [brand]"`

#### 🐧 Ubuntu/Linux
- [ ] If py-cpuinfo fails, fallback to `/proc/cpuinfo` or `lscpu`
- [ ] Check console for: `"CPU detected via /proc/cpuinfo: [brand]"` or `"CPU detected via lscpu: [brand]"`

---

## 🐛 Edge Cases & Error Handling

### 10.1 Invalid Encoder Override

#### All Platforms (🪟 🍎 🐧)
- [ ] Set invalid encoder:
  - Windows: `set TAGGR_FFMPEG_ENCODER=invalid_codec_name`
  - macOS/Linux: `export TAGGR_FFMPEG_ENCODER=invalid_codec_name`
- [ ] Launch app
- [ ] Look for console warning: `"TAGGR_FFMPEG_ENCODER=invalid_codec_name not available in ffmpeg, ignoring"`
- [ ] App should fall back to detected encoder
- [ ] Recording should still work

---

### 10.2 No GPU / Software Fallback

#### 🪟 Windows
- [ ] Test on VM without GPU acceleration OR disable GPU in Device Manager
- [ ] Launch app
- [ ] Check console: Should detect no hardware encoder
- [ ] Should fall back to `libx264`
- [ ] Recording should complete successfully (just slower)

#### 🍎 macOS
- [ ] If VideoToolbox is unavailable (rare):
- [ ] App should fall back to `libx264`
- [ ] Recording should complete

#### 🐧 Ubuntu/Linux
- [ ] Test on system without NVIDIA/Intel/AMD GPU drivers
- [ ] App should fall back to `libx264`
- [ ] Recording should complete

---

### 10.3 Very Short Recordings

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording
- [ ] Immediately stop (< 1 second)
- [ ] App should handle gracefully
- [ ] No crash or error
- [ ] Files may be minimal or empty (expected)

---

### 10.4 Very Long Recordings

#### All Platforms (🪟 🍎 🐧)
- [ ] Start recording for 10+ minutes
- [ ] Perform various actions throughout
- [ ] Stop recording
- [ ] Check for:
  - [ ] No memory leaks (monitor RAM usage)
  - [ ] Duration accuracy still maintained
  - [ ] File size is reasonable
  - [ ] Video plays correctly
  - [ ] All events captured

---

### 10.5 High CPU Load During Recording

#### All Platforms (🪟 🍎 🐧)
- [ ] Start CPU stress test (e.g., Prime95, stress-ng, or compile large project)
- [ ] Start recording
- [ ] Record for 1-2 minutes
- [ ] Stop recording
- [ ] Check console for warnings:
  - [ ] Frame drops
  - [ ] Duration mismatch
  - [ ] Queue stalls
- [ ] Video should still be usable
- [ ] Hardware encoding should handle better than software

---

### 10.6 Letterbox Invalid Dimensions Edge Case

#### All Platforms (🪟 🍎 🐧)
- [ ] This is an internal edge case - difficult to trigger manually
- [ ] Verify in code that `_compute_letterbox_mapping()` handles:
  - [ ] Zero dimensions (should use 1:1 fallback)
  - [ ] Negative dimensions (should use 1:1 fallback)
- [ ] Console warning: `"Invalid dimensions for letterbox mapping, using 1:1 fallback"`
- [ ] App should not crash with unusual screen/video dimensions

---

### 10.7 FFmpeg Not Found

#### All Platforms (🪟 🍎 🐧)
- [ ] Temporarily rename/remove ffmpeg from PATH
- [ ] Launch app
- [ ] Check console for: `"ffmpeg not found at: [path]"`
- [ ] App should show appropriate error or fallback behavior
- [ ] Restore ffmpeg to PATH after test

---

## 📊 Performance Benchmarks

### Platform Comparison Table

| Test | Windows (HW) | Windows (SW) | macOS (HW) | macOS (SW) | Linux (HW) | Linux (SW) |
|------|--------------|--------------|------------|------------|------------|------------|
| CPU % (idle) | | | | | | |
| CPU % (recording) | | | | | | |
| RAM usage (MB) | | | | | | |
| 60s file size (MB) | | | | | | |
| Encoding quality | | | | | | |
| GPU used | | | | | | |
| Frame drops | | | | | | |

---

## ✅ Final Checklist

### Pre-Merge Verification

#### Feature Completion
- [ ] **Hardware Acceleration:** Tested on all platforms
  - [ ] Encoder presets verified
  - [ ] FFmpeg encoder query working
- [ ] **Letterbox Mapping:** Tested on all platforms
  - [ ] Edge cases handled
  - [ ] Formula matches ffmpeg
- [ ] **Multi-Monitor:** Tested where available
  - [ ] Negative coordinates handled
  - [ ] Bounding box calculation correct
- [ ] **PTS Timing:** Verified Windows full support, macOS/Linux partial
  - [ ] video.log format compatible
  - [ ] Fallback working on macOS/Linux
- [ ] **Hybrid Buffer:** Verified Windows only
  - [ ] Capture metrics logged
  - [ ] Cursor sprite with position override
- [ ] **Enhanced Events:** Verified on all platforms
  - [ ] Windows trackpad scroll tested
  - [ ] Keyboard events have cursor position
- [ ] **Windows Recording Improvements:** Windows only
  - [ ] Duration validation working
  - [ ] Large file handling tested
  - [ ] Extended timeouts sufficient
- [ ] **Dependencies:** Verified on all platforms
  - [ ] py-cpuinfo installed and working
  - [ ] CPU detection fallbacks working

#### Platform Sign-Off
- [ ] **Windows:** All critical tests passed
- [ ] **macOS:** All critical tests passed
- [ ] **Ubuntu/Linux:** All critical tests passed

#### Regression Check
- [ ] No existing features broken
- [ ] Performance improvements documented
- [ ] Edge cases handled gracefully

#### Documentation
- [ ] Environment variables documented
- [ ] Metadata schema updated
- [ ] Event schema updated
- [ ] Platform-specific features noted

---

## 📝 Test Results Summary

### Windows
**Date:** _________________  
**Tester:** _________________  
**GPU:** _________________  
**Encoder:** _________________  
**Encoder Preset:** _________________  

**Capture Metrics:**
- None-frame count: _________________
- Queue stall count: _________________
- Duration mismatch: _________________

**Results:**
- [ ] ✅ Hardware acceleration working
- [ ] ✅ Encoder preset applied correctly
- [ ] ✅ Letterbox mapping correct
- [ ] ✅ PTS timing accurate
- [ ] ✅ Hybrid buffer functioning
- [ ] ✅ Duration validation passing
- [ ] ✅ Large file handling tested
- [ ] ✅ py-cpuinfo working
- [ ] ✅ No regressions

**Issues Found:** _________________

---

### macOS
**Date:** _________________  
**Tester:** _________________  
**GPU:** _________________  
**Encoder:** _________________  
**CPU Detection Method:** _________________  

**Results:**
- [ ] ✅ VideoToolbox working
- [ ] ✅ Letterbox mapping correct
- [ ] ⚠️ PTS timing partial (expected)
- [ ] ⚠️ No hybrid buffer (expected)
- [ ] ✅ py-cpuinfo working (or fallback)
- [ ] ✅ First-frame detection fast
- [ ] ✅ No regressions

**Issues Found:** _________________

---

### Ubuntu/Linux
**Date:** _________________  
**Tester:** _________________  
**GPU:** _________________  
**Encoder:** _________________  
**VAAPI Device:** _________________  
**CPU Detection Method:** _________________  

**Results:**
- [ ] ✅ Hardware acceleration working
- [ ] ✅ VAAPI device detected (if applicable)
- [ ] ✅ Letterbox mapping correct
- [ ] ⚠️ PTS timing partial (expected)
- [ ] ⚠️ No hybrid buffer (expected)
- [ ] ✅ py-cpuinfo working (or fallback)
- [ ] ✅ First-frame detection fast
- [ ] ✅ No regressions

**Issues Found:** _________________

---

## 🔧 Debugging Reference

### Check Available Encoders
```bash
# All platforms
ffmpeg -encoders | grep h264
ffmpeg -encoders | grep hevc

# Check specific encoder availability
ffmpeg -encoders | grep nvenc
ffmpeg -encoders | grep videotoolbox
ffmpeg -encoders | grep vaapi
ffmpeg -encoders | grep qsv
ffmpeg -encoders | grep amf
```

### Check Video Codec
```bash
# All platforms
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,codec_long_name video.mp4
```

### Check Video Duration
```bash
# All platforms  
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video.mp4
```

### Check CPU Info (py-cpuinfo)
```bash
# All platforms
python -c "import cpuinfo; info=cpuinfo.get_cpu_info(); print(f\"Brand: {info.get('brand_raw', 'Unknown')}\")"

# macOS fallback
sysctl -n machdep.cpu.brand_string

# Linux fallback
cat /proc/cpuinfo | grep "model name" | head -1
lscpu | grep "Model name"

# Windows fallback
echo %PROCESSOR_IDENTIFIER%
```

### Check GPU Vendor
```bash
# Windows (PowerShell)
Get-WmiObject Win32_VideoController | Select-Object Name

# macOS
system_profiler SPDisplaysDataType | grep "Chipset Model"

# Linux
lspci | grep -i vga
lspci | grep -i nvidia
lspci | grep -i amd
```

### Check VAAPI Device (Linux)
```bash
ls -la /dev/dri/renderD*
vainfo  # If vainfo is installed
```

### Monitor GPU Usage
- **Windows:** Task Manager → Performance → GPU
- **macOS:** Activity Monitor → GPU History
- **Linux:** `nvidia-smi` (NVIDIA), `radeontop` (AMD), `intel_gpu_top` (Intel)

### Inspect video.log Format
```bash
# Check first few lines of video.log
head -10 video.log

# Count total frames logged
wc -l video.log

# Check for format consistency
grep -c "frame_index:" video.log
grep -c "^n:" video.log
```

### Verify Event Fields
```bash
# Check if events have new fields
head -1 events.jsonl | python -m json.tool

# Count events with frame_pts_seconds
grep -c "frame_pts_seconds" events.jsonl

# Check for raw coordinates
grep -c "raw_x" events.jsonl
```

---

**Branch Commit:** _________________  
**Last Updated:** _________________

