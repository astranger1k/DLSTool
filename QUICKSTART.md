# Quick Start Guide – DLS Tool

The DLS Tool lets you inspect and convert GTA V Dynamic Lighting System (DLS) vehicle configuration files (VCF). This guide focuses on the fastest path from repository clone to converting your first file, regardless of operating system.

> [!NOTE]
> A packaged release is planned. Until then you run the tool directly from source.

## 1. Requirements

- Python 3.10 or newer (3.12 recommended)
- Git (optional; you can also download a ZIP from GitHub)
- Basic familiarity with your OS terminal or PowerShell

## 2. Get the Source

```bash
git clone https://github.com/astranger1k/DLSTool.git
cd DLSTool
```

Alternatively download the repository ZIP from GitHub, extract it, and open the folder in your terminal or VS Code.

## 3. Create a Virtual Environment (recommended)

| Platform | Command |
| --- | --- |
| Windows | `python -m venv env` |
| macOS / Linux | `python3 -m venv env` |

Activate it:

| Platform | Command |
| --- | --- |
| Windows PowerShell | `./env/Scripts/Activate.ps1` |
| Windows cmd | `env\Scripts\activate.bat` |
| macOS / Linux | `source env/bin/activate` |

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

PySide6 is the only external dependency today. If installation fails, upgrade pip first (`python -m pip install --upgrade pip`).

## 5. Launch the UI

```bash
python dls_tool.py
```

The main window opens with three primary regions:

1. **Explorer** – browse folders or individual VCFs.
2. **Analysis Panel** – immediate summary (version, vehicles, siren counts, light/audio modes).
3. **XML Preview** – syntax highlighted view with click-to-jump from the analysis tree.

## 6. Basic Workflow

1. **Load files**
   - *Single file*: click **Load VCF File**.
   - *Folder*: click **Browse Folder** to index every XML underneath.
2. **Inspect**
   - Summary cards show version, vehicle count, sirens, etc.
   - Tree view lists stages/light/audio modes and lets you jump to XML markers.
3. **Convert**
   - Use **Convert V1 → V2** or **Convert V2 → V1**.
   - Review the warning dialog for feature loss (v2→v1 truncates after five modes and strips extras/conditions).
4. **Save**
   - Choose an output path; the tool never overwrites the source automatically.

### Folder browsing perks

- Quickly compare multiple vehicles without re-opening dialogs.
- Filter by subdirectories using the breadcrumbs.
- Conversion buttons stay enabled for the currently selected file.

## 7. Example Conversions

| Scenario | Steps |
| --- | --- |
| **Template v1 → v2** | Load `DLSv1/Templates/police.xml`, review the analysis (3 stages, ~60 sirens), click **Convert V1 → V2**, save as `police_v2.xml`. |
| **Template v2 → v1** | Load `DLSv2/Templates/default.xml`, note the 19 light modes, click **Convert V2 → V1**, acknowledge the feature-loss warning, save as `default_v1.xml`. The result keeps the first five modes only. |

## 8. Testing the Tooling

```bash
python test_conversion.py
```

The script parses both templates, runs v1→v2 and v2→v1 conversions, performs a round-trip accuracy check, and emits sample output files (`test_v1_to_v2_output.xml`, `test_v2_to_v1_output.xml`). Use this whenever you pull new changes or tweak conversion logic.

## 9. Best Practices & Tips

- **Backup everything** before editing or converting live VCFs.
- **Start with templates** to verify your environment before touching production files.
- **Watch the console** for warnings about unsupported features or parsing issues.
- **Review the analysis overlay**; it highlights missing data such as absent vehicles lists or disabled stages.

### Understanding the analysis panel

- **v1 files** list stage enablement, siren counts, BPM, audio tones, and traffic advisory data.
- **v2 files** summarize light modes (sirens + extras), audio modes, vehicle count, and whether pattern sync / audio control groups exist.

## 10. FAQ

**Why do some features disappear after v2→v1 conversion?**  
The v1 schema lacks conditions, triggers, extras, animations, and more. The tool warns you before conversion and logs what was dropped.

**Can I convert v1→v2→v1 without losing anything?**  
Core siren/audio data survives, but v1-only metadata (e.g., traffic advisory patterns) may diverge after round-tripping.

**The GUI will not start. What now?**  
Ensure the virtual environment is active and PySide6 installed. On Windows PowerShell:

```bash
./env/Scripts/Activate.ps1
pip install PySide6
python dls_tool.py
```

**How many v2 modes can I keep when going to v1?**  
Five (Stage1–Stage3, CustomStage1–CustomStage2). Extra modes are skipped with a warning.

## 11. Troubleshooting

| Issue | Fix |
| --- | --- |
| `ModuleNotFoundError: PySide6` | Activate the venv, reinstall requirements. |
| "Failed to parse XML" | Validate the XML, ensure it's a DLS VCF, try opening one of the provided templates. |
| "Conversion produces unexpected results" | Run `python test_conversion.py`, check logs for warnings, compare with template output. |

## 12. Where to go next

- Read [README.md](README.md) for deeper technical context.
- Inspect `DLSv1/` and `DLSv2/` sample projects for schema references.
- Explore the `dlstool/` package to understand parsers, analyzers, and converters.
- Share bugs or ideas via GitHub issues.

---

Questions? The console log is verbose—start there, then open an issue if you need more help.
