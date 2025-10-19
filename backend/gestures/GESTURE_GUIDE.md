# 🎮 How to Perform Each Gesture

Complete guide for triggering gestures with your Mac's built-in camera.

**Total Gestures: 5**
- Swipe Left/Right (navigation)
- Thumbs Up (confirm)
- Point (details)
- Closed Fist (emergency)

---

## ⚙️ Setup Position

**Before you start:**
- Sit **2-3 feet** from your laptop
- Camera should be at **eye level or slightly above**
- Your hand should be at **chest to shoulder height**
- Make sure there's **good lighting** (face a window/lamp)
- Keep **simple background** behind your hand

---

## 1. ← → Swipe Left/Right - "Navigate Scenarios"

**Use OPEN HAND for swiping** (all fingers extended naturally)

This prevents false detection and makes swipes smooth!

---

### Swipe Left ← - "Previous Scenario"

**How to do it:**

### **METHOD 1: Full Hand (Easiest)**
1. Start with open hand on the **RIGHT side** of camera view
2. **Smoothly move** your hand to the **LEFT** across the frame
3. Move about 6-12 inches (15-30cm)
4. Takes about 0.5 seconds

### **METHOD 2: Closed Fist**
1. Make a fist on the **RIGHT side**
2. Move it **LEFT** across camera
3. Faster detection

**Tips:**
- ✅ Move in a **smooth line** (left to right)
- ✅ Speed: **Medium pace** (not too fast, not too slow)
- ✅ Start clearly on one side, end clearly on other side
- ✅ Small hand wobbles are OK (we allow 70% consistency)
- ❌ Don't move too slow or stop in the middle
- ❌ Don't zigzag back and forth

**What triggers it:**
- Hand moves LEFT (decreasing X coordinate)
- Minimum 10% of frame width
- At least 70% of movements go leftward
- Confidence: 80%+

**On laptop:** 
- Start hand toward right edge of your screen
- Swipe toward the left edge (toward your left shoulder)

---

### Swipe Right → - "Next Scenario"

**How to do it:**

### **METHOD 1: Full Hand (Easiest)**
1. Start with open hand on the **LEFT side** of camera view
2. **Smoothly move** your hand to the **RIGHT** across the frame
3. Move about 6-12 inches (15-30cm)
4. Takes about 0.5 seconds

### **METHOD 2: Closed Fist**
1. Make a fist on the **LEFT side**
2. Move it **RIGHT** across camera
3. Faster detection

**Tips:**
- ✅ Move in a **smooth line** (left to right)
- ✅ Speed: **Medium pace**
- ✅ Start clearly on one side, end clearly on other side
- ✅ Small hand wobbles are OK
- ❌ Don't move too slow or stop in the middle
- ❌ Don't zigzag back and forth

**What triggers it:**
- Hand moves RIGHT (increasing X coordinate)
- Minimum 10% of frame width
- At least 70% of movements go rightward
- Confidence: 80%+

**On laptop:**
- Start hand toward left edge of your screen
- Swipe toward the right edge (toward your right shoulder)

---

## 2. 👍 Thumbs Up - "Lock In Strategy"

**How to do it:**
1. Make a fist with all fingers curled
2. Stick your thumb straight UP (not sideways)
3. Hold steady for 0.5 seconds

**Tips:**
- ✅ Thumb must point UP (toward ceiling)
- ✅ Other 4 fingers should be closed
- ❌ Don't point thumb sideways - it won't detect

**What triggers it:**
- Thumb extended upward
- Other fingers curled
- Confidence: 95%

---

## 3. ☝️ Point - "Show Details"

**How to do it:**
1. Extend **ONLY your index finger** (pointing finger)
2. Curl your other 3 fingers and thumb into your palm
3. Point forward toward camera
4. Hold steady

**Tips:**
- ✅ ONLY index finger extended
- ✅ Middle, ring, pinky fingers must be curled
- ✅ Thumb can be curled or tucked
- ❌ Don't extend multiple fingers (becomes different gesture)

**What triggers it:**
- Index finger extended
- Other fingers curled
- Confidence: 95%

---

## 4. ✊ Closed Fist - "Emergency Mode"

**How to do it:**
1. Close all your fingers into a **tight fist**
2. Hold at chest level
3. Hold steady for 0.5 seconds
4. **Don't pump it up** - just hold still

**Tips:**
- ✅ All fingers curled in
- ✅ Thumb wrapped around or tucked
- ✅ Hold STATIC (don't move up/down)
- ❌ Don't raise it up (that was the old fist pump)

**What triggers it:**
- At least 3 fingers curled
- Static position (no motion)
- Confidence: 95%

---

## 🎯 Pro Tips for Success

### General Tips
1. **Hold gestures for 0.5-1 second** - Don't flash them too quickly
2. **Wait between gestures** - There's a 0.8 second cooldown
3. **Green is good** - When you see green box with gesture name, it detected!
4. **Practice makes perfect** - Try each gesture a few times

### For Swipes Specifically
- **Think "waving goodbye"** but smoother
- **Don't rush** - medium speed works best
- **Cross the whole frame** - start on one edge, end on the other
- **Keep your hand at same height** while swiping
- **Your hand can wobble a bit** - small jitters are OK now

### Troubleshooting
**If swipes aren't working:**
1. ✓ Check you're moving **at least 4-6 inches** across frame
2. ✓ Move at **medium speed** (not too fast or slow)
3. ✓ Start from **edge** of camera view
4. ✓ Keep movement **generally smooth**
5. ✓ Wait for cooldown between attempts

**If static gestures aren't working:**
1. ✓ Hold the pose for **at least 0.5 seconds**
2. ✓ Make sure **lighting is good**
3. ✓ Check your **hand is in center** of frame
4. ✓ Ensure fingers are **clearly visible**

---

## 📊 Detection Thresholds

| Gesture | Type | Threshold | Cooldown |
|---------|------|-----------|----------|
| Swipe Left/Right | Motion | 80% | 0.8s |
| Thumbs Up | Static | 95% | 0.8s |
| Point | Static | 95% | 0.8s |
| Closed Fist | Static | 95% | 0.8s |

**Note:** Open Palm is NOT detected as a gesture - use it freely for swiping!

---

## 🎬 Testing Your Gestures

Run the demo to practice:
```bash
cd backend
python gestures/gesture_demo.py
```

**What you'll see:**
- Your webcam feed with hand landmarks (colorful dots and lines)
- FPS counter (should be ~30)
- Gesture instructions on the left
- **GREEN BOX** when gesture is detected (bottom left)
- Detection count statistics (bottom right)

**Practice routine:**
1. Try each gesture 3-5 times
2. Watch the detection count increase
3. Get comfortable with the movements
4. Experiment with speed and position

---

## 🏁 Racing Dashboard Context

**In your actual racing app, you'll use these like:**

1. **Swipe Left/Right (with open hand)** - Browse through 3-5 strategy scenarios
2. **Thumbs Up** - "Execute this pit stop strategy NOW"
3. **Point** - "Tell me more about tire wear / fuel / gap"
4. **Closed Fist** - "Emergency! Show me fastest option only"

The gestures are designed to be **quick and deliberate** - perfect for high-pressure race situations! 🏎️💨

