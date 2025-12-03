# Quick Start Guide - DLS Tool

## 🚀 Getting Started in 3 Steps

### 1. Install
```bash
# Activate the virtual environment
.\env\Scripts\Activate.ps1

# (If needed) Install dependencies
pip install PySide6
```

### 2. Run
```bash
python dls_tool.py
```

### 3. Convert
1. Click **"Load VCF File"** to load a single file
   - OR -
2. Click **"Browse Folder"** to browse a folder with multiple VCF files
3. Click on any file in the list to load it
4. Click **"Convert V1 → V2"** or **"Convert V2 → V1"**
5. Save the converted file

## 📝 Example Workflow

### Converting a V1 Police Vehicle to V2

1. **Load**: Open `DLSv1/Templates/police.xml`
2. **Analyze**: Review the analysis panel
   - You'll see 3 stages enabled
   - 60 total sirens
   - All audio settings
3. **Convert**: Click **"Convert V1 → V2"**
4. **Save**: Choose output location (e.g., `police_v2.xml`)
5. **Done**: You now have a v2 file with all sirens and audio preserved!

### Converting a V2 File to V1

1. **Load**: Open `DLSv2/Templates/default.xml`
2. **Analyze**: Review the analysis panel
   - You'll see 19 light modes
   - 61 total sirens
3. **Convert**: Click **"Convert V2 → V1"**
   - ⚠️ **Warning**: You'll see a dialog about feature loss
   - Only first 5 modes will be converted
   - Conditions, triggers, extras will be lost
4. **Save**: Choose output location (e.g., `default_v1.xml`)
5. **Review**: The v1 file will have up to 5 stages

### Working with Multiple Files (Folder Browsing)

1. **Browse**: Click **"Browse Folder"**
2. **Select**: Choose a folder containing multiple VCF files
3. **View List**: All XML files appear in the left panel
4. **Load**: Click any file name to load it
5. **Convert**: Convert each file as needed
6. **Repeat**: Quickly switch between files without re-browsing

**Benefits:**
- Compare different vehicle configurations
- Batch convert multiple files
- Organize your VCF library
- Quick access to all files in a folder

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_conversion.py
```

This will:
- Parse both template files
- Convert v1 → v2
- Convert v2 → v1
- Test round-trip conversion
- Generate output files for inspection

## 💡 Tips

### Best Practices
- **Backup**: Always keep a backup of your original files
- **Test First**: Use the templates to test conversions before working with custom files
- **Check Analysis**: Review the analysis panel to understand what's in your file
- **Read Warnings**: Pay attention to warning messages about feature loss

### Understanding the Analysis Panel

**v1 Files Show:**
- ✓ = Stage enabled, ✗ = Stage disabled
- Siren count per stage
- BPM (beats per minute)
- Audio tone settings

**v2 Files Show:**
- Light modes with siren counts
- Audio modes with soundsets
- Extras count per mode
- V2-specific features (pattern sync, speed drift)

## ❓ Common Questions

**Q: Why are some features missing after v2→v1 conversion?**  
A: v1 doesn't support v2 features like conditions, triggers, extras, animations, etc. These are inherent format limitations.

**Q: Can I convert v1→v2→v1 without loss?**  
A: Basic siren and audio settings survive the round-trip. However, v1-specific features like traffic advisory patterns may not.

**Q: How many modes can I convert from v2 to v1?**  
A: Maximum 5 modes (Stage1-3, CustomStage1-2) due to v1 limitations.

**Q: The GUI won't start?**  
A: Make sure you've activated the virtual environment and installed PySide6:
```bash
.\env\Scripts\Activate.ps1
pip install PySide6
python dls_tool.py
```

## 🔍 Troubleshooting

### Issue: "Module not found: PySide6"
**Solution**: Install PySide6 in your virtual environment
```bash
.\env\Scripts\Activate.ps1
pip install PySide6
```

### Issue: "Failed to parse XML"
**Solution**: 
- Verify your file is a valid DLS VCF XML file
- Check for XML syntax errors
- Test with the included templates first

### Issue: "Conversion produces unexpected results"
**Solution**:
- Run the test suite first: `python test_conversion.py`
- Check the console logs for warnings
- Compare with template conversions
- Verify your source file is not corrupted

## 📚 Next Steps

- Read the full [README.md](README.md) for technical details
- Explore the source code to understand the conversion logic
- Check the DLS v1 and v2 source folders for reference
- Experiment with the template files

---

**Need Help?** Check the console output for detailed logs and warnings.
