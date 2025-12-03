# DLS Tool

A comprehensive tool for converting and analyzing **Dynamic Lighting System (DLS)** Vehicle Configuration Files (VCF) for GTA 5. Supports both DLS v1 and v2 formats with bidirectional conversion and detailed analysis capabilities.

## 🚨 Features

### Core Functionality
- ✅ **Bidirectional Conversion**: Convert between DLS v1 ↔ v2 formats
- ✅ **Intelligent Parsing**: Fully parses both v1 and v2 XML structures
- ✅ **Deep Analysis**: Analyze VCF files with detailed statistics
- ✅ **Data Preservation**: Maintains siren configurations, audio settings, and more
- ✅ **Loss Detection**: Warns about features lost during v2→v1 conversion

### GUI Features
- 📁 File browser for easy VCF loading
- 📂 **Folder browsing** - Load and browse entire folders of VCF files
- 🔍 Real-time XML preview
- 📊 Analysis panel showing:
  - Total siren count
  - Stage/mode configurations
  - Audio settings
  - Special features (traffic advisory, wail setup, etc.)
- 💾 Save converted files with proper XML formatting
- ⚠️ Warning dialogs for feature loss

## ⚠️ Important Notes

### V1 → V2 Conversion
When converting from v1 to v2:
- ✅ All stages (Stage1-3, CustomStage1-2) are preserved as modes
- ✅ All siren configurations are maintained
- ✅ Audio settings (Tone1-4, Horn) are converted to audio modes
- ⚠️ V2-specific features (conditions, triggers, extras) will be **empty** (you'll need to add them manually)

### V2 → V1 Conversion
When converting from v2 to v1:
- ✅ Up to 5 light modes are converted to v1 stages
- ✅ Audio modes are mapped to v1 sound settings
- ✅ Basic siren configurations are preserved
- ❌ **LOST**: Conditions, triggers, extras, modkits, animations, paints (v1 doesn't support these)
- ⚠️ Modes beyond the first 5 are skipped

## 📋 Installation

### Prerequisites
- Python 3.8 or higher
- PySide6 (for GUI)

### Setup

1. **Clone or download this repository**

2. **Create and activate a virtual environment** (recommended):
   ```bash
   # Windows (Powershell)
   python -m venv env
   .\env\Scripts\Activate.ps1
   
   # Linux/Mac
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or manually:
   ```bash
   pip install PySide6 pandas numpy
   ```

## 🚀 Usage

### Graphical Interface (Recommended)

1. **Activate virtual environment**:
   ```bash
   .\env\Scripts\Activate.ps1  # Windows
   ```

2. **Launch the GUI**:
   ```bash
   python dls_tool.py
   ```

3. **Using the GUI**:
   
   **Single File Mode:**
   - Click **"Load VCF File"** to open a single v1 or v2 XML file
   - The tool automatically detects the version
   - View analysis in the left panel
   - Preview XML in the right panel
   - Click **"Convert V1 → V2"** or **"Convert V2 → V1"** to convert
   - Choose where to save the converted file
   
   **Folder Browsing Mode:**
   - Click **"Browse Folder"** to open a folder containing VCF files
   - All XML files in the folder will be listed
   - Click any file in the list to load and analyze it
   - Convert individual files as needed
   - Great for working with multiple vehicle configurations

### Testing the Converter

Run the included test suite to verify functionality:
```bash
python test_conversion.py
```

This will run automated tests on the template files and generate:
- `test_v1_to_v2_output.xml` - v1 police.xml converted to v2
- `test_v2_to_v1_output.xml` - v2 default.xml converted to v1

## 📁 Project Structure

```
DLSTool/
├── dls_tool.py              # Main application (GUI + conversion logic)
├── test_conversion.py       # Test suite for conversions
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── DLSv1/                  # DLS v1 source code (reference)
│   ├── Templates/
│   │   └── police.xml      # v1 template file
│   └── DLS/
│       └── ...             # v1 source code
└── DLSv2/                  # DLS v2 source code (reference)
    ├── Templates/
    │   └── default.xml     # v2 template file
    └── DLSv2/
        └── ...             # v2 source code
```

## 🔧 Technical Details

### Data Structures

#### DLS v1 Format
- **StageSettings**: Enable/disable stages (Stage1-3, CustomStage1-2)
- **SpecialModes**: Siren UI, wail setup, steady burn
- **SoundSettings**: Tone1-4, Horn, air horn behavior
- **TrafficAdvisory**: Traffic advisor patterns (L, EL, CL, C, CR, ER, R)
- **Sirens**: Stage1-3, CustomStage1-2 configurations

#### DLS v2 Format
- **Audio**: AudioModes (with sounds) and AudioControlGroups
- **Modes**: Light modes with conditions, triggers, extras
- **SirenSettings**: Per-mode siren configurations
- **Advanced Features**: Animations, paints, modkits, conditions

### Conversion Mappings

#### V1 → V2
| v1 Element | v2 Element | Notes |
|------------|------------|-------|
| Stage1-3 | Light Modes (named "Stage 1-3") | Direct mapping |
| CustomStage1-2 | Light Modes (named "Custom Stage 1-2") | Direct mapping |
| Tone1-4, Horn | AudioModes | Mapped to slow/fast/warning/horn |
| Sirens | SirenSettings | Fully preserved |
| TrafficAdvisory | *(not converted)* | No direct v2 equivalent |

#### V2 → V1
| v2 Element | v1 Element | Notes |
|------------|------------|-------|
| First 5 Light Modes | Stage1-3, CustomStage1-2 | Max 5 stages |
| AudioModes | Tone1-4, Horn | Best-effort mapping |
| SirenSettings | Sirens | Fully preserved |
| Conditions/Triggers | *(lost)* | v1 doesn't support |
| Extras/Animations | *(lost)* | v1 doesn't support |

## 📊 Analysis Output

When you analyze a file, you'll see:

### v1 Analysis
- **Stages**: Enabled/disabled status, siren count, BPM, texture
- **Audio Settings**: All tone configurations
- **Special Features**: Custom UI, wail setup, steady burn status
- **Traffic Advisory**: Type and pattern count

### v2 Analysis
- **Light Modes**: Mode name, siren count, extras count
- **Audio Modes**: Sound settings (soundset/sound name)
- **V2 Features**: Pattern sync, speed drift, default mode

## 🐛 Known Limitations

1. **v2 Conditions**: Not parsed from v1 (v1 doesn't have them)
2. **Traffic Advisory**: v1 traffic advisory patterns not converted to v2 (no direct equivalent)
3. **V2 to V1 Extras**: Vehicle extras are lost (v1 doesn't support)
4. **Mode Limit**: v2→v1 conversion limited to 5 modes (v1 limitation)

## 🤝 Contributing

Contributions are welcome! The source code is well-documented. Key areas:

- **Parsers**: `DLSv1Parser`, `DLSv2Parser` - XML parsing logic
- **Converters**: `V1ToV2Converter`, `V2ToV1Converter` - Conversion logic
- **Writers**: `DLSv1Writer`, `DLSv2Writer` - XML generation
- **Analyzer**: `DLSAnalyzer` - Analysis logic
- **GUI**: `DlsToolApp` - PySide6 interface

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[TheMaybeast](https://github.com/TheMaybeast/)** for creating [DLS V1](https://github.com/TheMaybeast/DLS) and [DLS V2](https://github.com/TheMaybeast/DLSV2)
- Templates included from official DLS distributions

## 📞 Support

For issues, questions, or feature requests:
1. Check the analysis output for warnings
2. Review the console logs (shows detailed conversion steps)
3. Verify your XML files are valid DLS VCF files
4. Test with the included templates first

---

**Happy Converting! 🚗💡**
