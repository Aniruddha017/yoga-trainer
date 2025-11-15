# Processing Your Yoga Pose Images

## Current Structure
Your images are organized in folders like:
```
data/reference_poses/images/
├── Tree_Pose_or_Vrksasana__front/
│   └── [your image.jpg]
├── Tree_Pose_or_Vrksasana__side/
│   └── [your image.jpg]
├── Warrior_I_Pose_or_Virabhadrasana_I__front/
│   └── [your image.jpg]
└── Warrior_I_Pose_or_Virabhadrasana_I__side/
    └── [your image.jpg]
```

## Steps to Process Images

### 1. Add Your Images
Make sure each folder (ending with `_front` or `_side`) contains at least one image file:
- Supported formats: `.jpg`, `.jpeg`, `.png`
- Image should show the full yoga pose clearly
- Good lighting and plain background recommended

### 2. Run the Processing Script

**Option A: Using Python directly**
```powershell
cd "d:\yoga_webapp\new yoga app"
.\myenv\Scripts\activate
python scripts/process_reference_images.py
```

**Option B: If activation doesn't work**
```powershell
cd "d:\yoga_webapp\new yoga app"
.\myenv\Scripts\python.exe scripts/process_reference_images.py
```

### 3. What the Script Does

The script will:
1. ✅ Scan all folders in `data/reference_poses/images/`
2. ✅ Find images in each `_front` and `_side` folder
3. ✅ Use MediaPipe to detect 33 body landmarks
4. ✅ Extract keypoint coordinates
5. ✅ Save JSON files to `data/reference_poses/keypoints/`
6. ✅ Create separate entries for front and side views

### 4. Expected Output

For each pose image, you'll get:
- ✅ `Warrior_I_Pose_or_Virabhadrasana_I__front.json` - Front view keypoints
- ✅ `Warrior_I_Pose_or_Virabhadrasana_I__side.json` - Side view keypoints

Each JSON contains:
```json
{
  "pose_id": "Warrior_I_Pose_or_Virabhadrasana_I__front",
  "base_pose_name": "Warrior_I_Pose_or_Virabhadrasana_I_",
  "name": "Warrior I Pose or Virabhadrasana I",
  "difficulty": "intermediate",
  "view_angle": "front",
  "keypoints": [...],
  "reference_image": "data/reference_poses/images/...",
  "description": "..."
}
```

### 5. Using in the Application

After processing:
1. Start the server: `python -m uvicorn app.main:app --reload`
2. Open: http://localhost:8000
3. Select a pose from the dropdown
4. Choose view (Front or Side)
5. The app will show which views are available for each pose

### Troubleshooting

**No images found:**
- Make sure images are inside the `_front` or `_side` folders
- Check file extensions (`.jpg`, `.jpeg`, `.png`)

**Low confidence detection:**
- Ensure full body is visible in the image
- Use images with good lighting
- Plain background works best

**Pose not detected:**
- Person should be clearly visible
- Try a different image with better quality
- Check that the pose is clearly distinguishable

### Manual Editing

You can manually edit the generated JSON files to:
- Change difficulty level (`beginner`, `intermediate`, `advanced`)
- Update pose description
- Modify pose name

### View Selection in Frontend

The updated frontend now:
- Groups poses by base name
- Shows available views (Front & Side, Front only, or Side only)
- Allows switching between views
- Displays appropriate reference image for each view
- Compares user pose against selected view

## Ready to Process!

Run the script and it will process all your yoga pose images automatically! 🧘‍♀️
