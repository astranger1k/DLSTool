"""Qt dialogs used by the DLS tool UI."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from .models import DLSVersion, DLSv1Data, DLSv2Data


class ConfigEditorDialog(QtWidgets.QDialog):
    """Configuration editor dialog for DLS settings."""

    def __init__(self, data, version: DLSVersion, parent=None):
        super().__init__(parent)
        self.data: DLSv1Data | DLSv2Data = data
        self.version = version
        self.modified = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"DLS Configuration Editor - {self.version.value.upper()}")
        self.setMinimumSize(800, 600)
        layout = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()

        if self.version == DLSVersion.V1:
            tabs.addTab(self.create_v1_stage_settings(), "Stage Settings")
            tabs.addTab(self.create_v1_sound_settings(), "Sound Settings")
            tabs.addTab(self.create_v1_special_modes(), "Special Modes")
            tabs.addTab(self.create_v1_traffic_advisory(), "Traffic Advisory")
        else:
            tabs.addTab(self.create_v2_general_settings(), "General")
            tabs.addTab(self.create_v2_light_modes(), "Light Modes")
            tabs.addTab(self.create_v2_audio_modes(), "Audio Modes")
            tabs.addTab(self.create_v2_sync_settings(), "Sync Settings")

        layout.addWidget(tabs)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        save_btn = QtWidgets.QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    # --- V1 tabs ---------------------------------------------------------
    def create_v1_stage_settings(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        layout.addRow(QtWidgets.QLabel("<b>Light Stage Configuration</b>"))
        layout.addRow(QtWidgets.QLabel("<i>Enable or disable light stages. Stages define different siren patterns.</i>"))
        layout.addRow(QtWidgets.QLabel(""))

        self.stage1_enabled = QtWidgets.QCheckBox()
        self.stage1_enabled.setChecked(self.data.stage1_enabled)
        self.stage1_enabled.setToolTip("Primary siren pattern (usually activated with 'Q')")
        layout.addRow("Stage 1 Enabled:", self.stage1_enabled)

        self.stage2_enabled = QtWidgets.QCheckBox()
        self.stage2_enabled.setChecked(self.data.stage2_enabled)
        self.stage2_enabled.setToolTip("Secondary siren pattern (usually activated with 'R')")
        layout.addRow("Stage 2 Enabled:", self.stage2_enabled)

        self.stage3_enabled = QtWidgets.QCheckBox()
        self.stage3_enabled.setChecked(self.data.stage3_enabled)
        self.stage3_enabled.setToolTip("Tertiary siren pattern (usually activated with 'T')")
        layout.addRow("Stage 3 Enabled:", self.stage3_enabled)

        self.custom_stage1_enabled = QtWidgets.QCheckBox()
        self.custom_stage1_enabled.setChecked(self.data.custom_stage1_enabled)
        self.custom_stage1_enabled.setToolTip("Additional custom pattern 1")
        layout.addRow("Custom Stage 1 Enabled:", self.custom_stage1_enabled)

        self.custom_stage2_enabled = QtWidgets.QCheckBox()
        self.custom_stage2_enabled.setChecked(self.data.custom_stage2_enabled)
        self.custom_stage2_enabled.setToolTip("Additional custom pattern 2")
        layout.addRow("Custom Stage 2 Enabled:", self.custom_stage2_enabled)

        layout.addRow(QtWidgets.QLabel(""))

        self.get_stage3_from_carcols = QtWidgets.QCheckBox()
        self.get_stage3_from_carcols.setChecked(self.data.get_stage3_from_carcols)
        self.get_stage3_from_carcols.setToolTip("Use Stage 3 definition from carcols.meta instead of VCF")
        layout.addRow("Get Stage 3 from Carcols:", self.get_stage3_from_carcols)

        layout.addRow(QtWidgets.QLabel(""))

        if self.data.stage1:
            layout.addRow("Stage 1 Sirens:", QtWidgets.QLabel(f"{len(self.data.stage1.sirens)} items"))
        if self.data.stage2:
            layout.addRow("Stage 2 Sirens:", QtWidgets.QLabel(f"{len(self.data.stage2.sirens)} items"))
        if self.data.stage3:
            layout.addRow("Stage 3 Sirens:", QtWidgets.QLabel(f"{len(self.data.stage3.sirens)} items"))
        if self.data.custom_stage1:
            layout.addRow("Custom Stage 1 Sirens:", QtWidgets.QLabel(f"{len(self.data.custom_stage1.sirens)} items"))
        if self.data.custom_stage2:
            layout.addRow("Custom Stage 2 Sirens:", QtWidgets.QLabel(f"{len(self.data.custom_stage2.sirens)} items"))

        layout.addRow(QtWidgets.QLabel(""))
        layout.addRow(QtWidgets.QLabel("<i>Note: Individual siren patterns, timing, and effects are edited in the XML directly.</i>"))
        return widget

    def create_v1_sound_settings(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        layout.addRow(QtWidgets.QLabel("<b>Siren Sound Configuration</b>"))
        layout.addRow(QtWidgets.QLabel("<i>Configure which sound effects play for each siren tone.</i>"))
        layout.addRow(QtWidgets.QLabel(""))

        sound_options = [
            "VEHICLES_HORNS_SIREN_1",
            "VEHICLES_HORNS_SIREN_2",
            "VEHICLES_HORNS_POLICE_WARNING",
            "VEHICLES_HORNS_AMBULANCE_WARNING",
            "VEHICLES_HORNS_FIRETRUCK_WARNING",
            "SIRENS_AIRHORN",
            "RESIDENT_VEHICLES_HORN",
        ]

        self.tone1 = QtWidgets.QComboBox()
        self.tone1.addItems(sound_options)
        self.tone1.setEditable(True)
        self.tone1.setCurrentText(self.data.tone1)
        self.tone1.setToolTip("Primary siren sound (Wail/Yelp)")
        layout.addRow("Tone 1:", self.tone1)

        self.tone2 = QtWidgets.QComboBox()
        self.tone2.addItems(sound_options)
        self.tone2.setEditable(True)
        self.tone2.setCurrentText(self.data.tone2)
        self.tone2.setToolTip("Secondary siren sound (typically faster)")
        layout.addRow("Tone 2:", self.tone2)

        self.tone3 = QtWidgets.QComboBox()
        self.tone3.addItems(sound_options)
        self.tone3.setEditable(True)
        self.tone3.setCurrentText(self.data.tone3)
        self.tone3.setToolTip("Warning/Alert sound")
        layout.addRow("Tone 3:", self.tone3)

        self.tone4 = QtWidgets.QComboBox()
        self.tone4.addItems(sound_options)
        self.tone4.setEditable(True)
        self.tone4.setCurrentText(self.data.tone4)
        self.tone4.setToolTip("Auxiliary/secondary warning sound")
        layout.addRow("Tone 4:", self.tone4)

        self.horn = QtWidgets.QComboBox()
        self.horn.addItems(sound_options)
        self.horn.setEditable(True)
        self.horn.setCurrentText(self.data.horn)
        self.horn.setToolTip("Airhorn sound")
        layout.addRow("Horn:", self.horn)

        self.air_horn_interrupts_siren = QtWidgets.QCheckBox()
        self.air_horn_interrupts_siren.setChecked(self.data.air_horn_interrupts_siren)
        layout.addRow("Airhorn interrupts siren:", self.air_horn_interrupts_siren)

        layout.addRow(QtWidgets.QLabel(""))
        layout.addRow(QtWidgets.QLabel("<i>Tip: Double-click entries to edit or type custom sound names.</i>"))
        return widget

    def create_v1_special_modes(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        layout.addRow(QtWidgets.QLabel("<b>Special Modes</b>"))
        layout.addRow(QtWidgets.QLabel("Configure wail/steady burn behaviour."))
        layout.addRow(QtWidgets.QLabel(""))

        self.siren_ui = QtWidgets.QLineEdit(self.data.siren_ui)
        self.siren_ui.setPlaceholderText("E.g. default")
        layout.addRow("Siren UI preset:", self.siren_ui)

        self.preset_siren_on_leave = QtWidgets.QComboBox()
        self.preset_siren_on_leave.addItems(["none", "wail", "yelp", "priority"])
        self.preset_siren_on_leave.setCurrentText(self.data.preset_siren_on_leave or "none")
        layout.addRow("Preset on leave vehicle:", self.preset_siren_on_leave)

        self.wail_setup_enabled = QtWidgets.QCheckBox()
        self.wail_setup_enabled.setChecked(self.data.wail_setup_enabled)
        layout.addRow("Wail setup enabled:", self.wail_setup_enabled)

        self.wail_light_stage = QtWidgets.QLineEdit(self.data.wail_light_stage)
        layout.addRow("Wail light stage:", self.wail_light_stage)

        self.wail_siren_tone = QtWidgets.QLineEdit(self.data.wail_siren_tone)
        layout.addRow("Wail siren tone:", self.wail_siren_tone)

        layout.addRow(QtWidgets.QLabel(""))

        self.steady_burn_enabled = QtWidgets.QCheckBox()
        self.steady_burn_enabled.setChecked(self.data.steady_burn_enabled)
        layout.addRow("Steady burn enabled:", self.steady_burn_enabled)

        self.steady_burn_pattern = QtWidgets.QLineEdit(self.data.steady_burn_pattern)
        layout.addRow("Steady burn pattern:", self.steady_burn_pattern)

        self.steady_burn_sirens = QtWidgets.QLineEdit(self.data.steady_burn_sirens)
        layout.addRow("Steady burn sirens:", self.steady_burn_sirens)
        return widget

    def create_v1_traffic_advisory(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        layout.addRow(QtWidgets.QLabel("<b>Traffic Advisory</b>"))
        layout.addRow(QtWidgets.QLabel("Configure patterns for each panel section."))
        layout.addRow(QtWidgets.QLabel(""))

        self.ta_type = QtWidgets.QComboBox()
        self.ta_type.addItems(["off", "default", "custom"])
        self.ta_type.setCurrentText(self.data.traffic_advisory_type or "off")
        layout.addRow("TA Type:", self.ta_type)

        self.ta_diverge_only = QtWidgets.QCheckBox()
        self.ta_diverge_only.setChecked(self.data.traffic_advisory_diverge_only)
        layout.addRow("Diverge only mode:", self.ta_diverge_only)

        self.ta_auto_enable = QtWidgets.QLineEdit(self.data.traffic_advisory_auto_enable_stages)
        layout.addRow("Auto enable stages:", self.ta_auto_enable)

        self.ta_default_dir = QtWidgets.QLineEdit(self.data.traffic_advisory_default_direction)
        layout.addRow("Default direction:", self.ta_default_dir)

        self.ta_auto_disable = QtWidgets.QLineEdit(self.data.traffic_advisory_auto_disable_stages)
        layout.addRow("Auto disable stages:", self.ta_auto_disable)

        layout.addRow(QtWidgets.QLabel(""))

        self.ta_patterns = {}
        for pos in ["L", "EL", "CL", "C", "CR", "ER", "R"]:
            edit = QtWidgets.QLineEdit(self.data.traffic_advisory_patterns.get(pos, ""))
            layout.addRow(f"Pattern {pos}:", edit)
            self.ta_patterns[pos] = edit

        layout.addRow(QtWidgets.QLabel(""))
        layout.addRow(QtWidgets.QLabel("<i>Patterns accept sequences like L/R or custom commands.</i>"))
        return widget

    # --- V2 tabs ---------------------------------------------------------
    def create_v2_general_settings(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        self.vehicles = QtWidgets.QLineEdit(self.data.vehicles)
        layout.addRow("Vehicles tag:", self.vehicles)

        layout.addRow(QtWidgets.QLabel(""))
        layout.addRow(QtWidgets.QLabel("<b>Default Mode</b>"))

        self.default_mode = QtWidgets.QLineEdit(self.data.default_mode)
        layout.addRow("Default mode name:", self.default_mode)

        return widget

    def create_v2_light_modes(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        layout.addWidget(QtWidgets.QLabel("<b>Light Modes (read-only preview)</b>"))
        list_widget = QtWidgets.QListWidget()
        for mode in self.data.light_modes:
            siren_count = len(mode.siren_settings.sirens) if mode.siren_settings else 0
            list_widget.addItem(f"{mode.name} — {siren_count} sirens, extras: {len(mode.extras)}")
        layout.addWidget(list_widget)
        layout.addWidget(
            QtWidgets.QLabel(
                "<i>Detailed light-mode editing not yet supported here. Edit XML directly for full control.</i>"
            )
        )
        return widget

    def create_v2_audio_modes(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        layout.addWidget(QtWidgets.QLabel("<b>Audio Modes (read-only preview)</b>"))
        list_widget = QtWidgets.QListWidget()
        for mode in self.data.audio_modes:
            list_widget.addItem(f"{mode.name} — {mode.sound_name} ({mode.soundset})")
        layout.addWidget(list_widget)
        layout.addWidget(
            QtWidgets.QLabel(
                "<i>Detailed audio-mode editing not yet supported here. Edit XML directly for full control.</i>"
            )
        )
        return widget

    def create_v2_sync_settings(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        self.pattern_sync = QtWidgets.QLineEdit(self.data.pattern_sync)
        layout.addRow("Pattern sync bus:", self.pattern_sync)

        self.speed_drift = QtWidgets.QDoubleSpinBox()
        self.speed_drift.setDecimals(3)
        self.speed_drift.setRange(-10.0, 10.0)
        self.speed_drift.setValue(self.data.speed_drift)
        layout.addRow("Speed drift:", self.speed_drift)
        return widget

    # --- Save ------------------------------------------------------------
    def save_changes(self):
        if self.version == DLSVersion.V1:
            self.data.stage1_enabled = self.stage1_enabled.isChecked()
            self.data.stage2_enabled = self.stage2_enabled.isChecked()
            self.data.stage3_enabled = self.stage3_enabled.isChecked()
            self.data.custom_stage1_enabled = self.custom_stage1_enabled.isChecked()
            self.data.custom_stage2_enabled = self.custom_stage2_enabled.isChecked()
            self.data.get_stage3_from_carcols = self.get_stage3_from_carcols.isChecked()

            self.data.tone1 = self.tone1.currentText()
            self.data.tone2 = self.tone2.currentText()
            self.data.tone3 = self.tone3.currentText()
            self.data.tone4 = self.tone4.currentText()
            self.data.horn = self.horn.currentText()
            self.data.air_horn_interrupts_siren = self.air_horn_interrupts_siren.isChecked()

            self.data.siren_ui = self.siren_ui.text().strip()
            self.data.preset_siren_on_leave = self.preset_siren_on_leave.currentText()
            self.data.wail_setup_enabled = self.wail_setup_enabled.isChecked()
            self.data.wail_light_stage = self.wail_light_stage.text().strip()
            self.data.wail_siren_tone = self.wail_siren_tone.text().strip()
            self.data.steady_burn_enabled = self.steady_burn_enabled.isChecked()
            self.data.steady_burn_pattern = self.steady_burn_pattern.text().strip()
            self.data.steady_burn_sirens = self.steady_burn_sirens.text().strip()

            self.data.traffic_advisory_type = self.ta_type.currentText()
            self.data.traffic_advisory_diverge_only = self.ta_diverge_only.isChecked()
            self.data.traffic_advisory_auto_enable_stages = self.ta_auto_enable.text().strip()
            self.data.traffic_advisory_default_direction = self.ta_default_dir.text().strip()
            self.data.traffic_advisory_auto_disable_stages = self.ta_auto_disable.text().strip()
            for pos, edit in self.ta_patterns.items():
                self.data.traffic_advisory_patterns[pos] = edit.text().strip()
        else:
            self.data.vehicles = self.vehicles.text().strip()
            self.data.default_mode = self.default_mode.text().strip()
            self.data.pattern_sync = self.pattern_sync.text().strip()
            self.data.speed_drift = self.speed_drift.value()

        self.modified = True
        self.accept()


class PluginConfigDialog(QtWidgets.QDialog):
    """Simple INI editor for DLS plugin configuration (DLS.ini)."""

    def __init__(self, config, ini_path: str, parent=None):
        super().__init__(parent)
        self.config = config
        self.ini_path = ini_path
        self.setWindowTitle("DLS Plugin Config Editor (DLS.ini)")
        self.setMinimumSize(700, 500)
        # Build a comment-preserving model of the INI file
        self._ini = CommentPreservingIni.from_file(ini_path)
        self._build_ui()

    def _build_ui(self):
        import configparser

        layout = QtWidgets.QVBoxLayout(self)
        self.table = QtWidgets.QTableWidget()
        rows = []
        for section in self._ini.sections():
            for key in self._ini.keys(section):
                rows.append((section, key, self._ini.get(section, key)))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Section", "Key", "Value", "Comment"])
        self.table.setRowCount(len(rows))
        for i, (sec, key, val) in enumerate(rows):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(sec))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(key))
            item_val = QtWidgets.QTableWidgetItem(val)
            item_val.setFlags(item_val.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item_val)
            comment_text = self._ini.get_comment(sec, key) or ""
            item_comment = QtWidgets.QTableWidgetItem(comment_text)
            item_comment.setToolTip(comment_text)
            item_comment.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(i, 3, item_comment)
        self.table.resizeColumnsToContents()
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked
        )
        layout.addWidget(self.table)

        btns = QtWidgets.QHBoxLayout()
        btns.addStretch()
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self._save_ini)
        btns.addWidget(save_btn)
        cancel_btn = QtWidgets.QPushButton("Close")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def _save_ini(self):
        for row in range(self.table.rowCount()):
            sec = self.table.item(row, 0).text()
            key = self.table.item(row, 1).text()
            val_item = self.table.item(row, 2)
            val = val_item.text() if val_item else ""
            self._ini.set(sec, key, val)
        try:
            self._ini.write(self.ini_path)
            QtWidgets.QMessageBox.information(self, "Saved", f"Updated {self.ini_path}")
            self.accept()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to write INI:\n{exc}")


class CommentPreservingIni:
    """Minimal INI handler that keeps comments and formatting intact."""

    def __init__(self, lines):
        self._lines = lines
        self._index = {}
        self._sections = []
        self._build_index()

    @classmethod
    def from_file(cls, path):
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
        return cls(lines)

    def sections(self):
        return list(self._sections)

    def keys(self, section):
        return [k for (s, k) in self._index.keys() if s == section]

    def get(self, section, key):
        idx = self._index.get((section, key))
        if idx is None:
            return ""
        line = self._lines[idx]
        return self._extract_value(line)

    def set(self, section, key, value):
        idx = self._index.get((section, key))
        if idx is None:
            self._ensure_section(section)
            insert_idx = self._find_section_insert_point(section)
            new_line = f"{key} = {value}\n"
            self._lines.insert(insert_idx, new_line)
            self._build_index()
            return
        line = self._lines[idx]
        pre, comment = self._split_comment(line)
        key_part, eq, rest = self._split_key_value(pre)
        if not eq:
            eq = "="
        new_pre = f"{key_part.strip()} {eq} {value}"
        self._lines[idx] = new_pre + comment

    def write(self, path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.writelines(self._lines)

    def _build_index(self):
        self._index.clear()
        self._sections = []
        current_section = None
        for i, raw in enumerate(self._lines):
            line = raw.strip()
            if not line:
                continue
            if line.startswith(("#", ";", "//")):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                if current_section not in self._sections:
                    self._sections.append(current_section)
                continue
            if "=" in line and current_section:
                key = line.split("=", 1)[0].strip()
                self._index[(current_section, key)] = i

    def _extract_value(self, line):
        s = line.rstrip("\n")
        s = self._strip_inline_comment(s)
        if "=" in s:
            return s.split("=", 1)[1].strip()
        return ""

    def get_comment(self, section, key):
        idx = self._index.get((section, key))
        if idx is None:
            return ""
        line = self._lines[idx].rstrip("\n")
        _, inline_comment = self._split_comment(line)
        comments = []
        if inline_comment.strip():
            comments.append(inline_comment.strip())
        i = idx - 1
        while i >= 0:
            raw_prev = self._lines[i].rstrip("\n")
            prev = raw_prev.strip()
            if not prev:
                break
            if prev.startswith("[") and prev.endswith("]"):
                break
            if prev.startswith("//") or prev.startswith("#") or prev.startswith(";"):
                if prev.startswith("//"):
                    comments.insert(0, prev[2:].strip())
                elif prev.startswith("#"):
                    comments.insert(0, prev[1:].strip())
                else:
                    comments.insert(0, prev[1:].strip())
                i -= 1
                continue
            break
        return "\n".join(comments)

    def _strip_inline_comment(self, s):
        idxs = [i for i in [s.find("//"), s.find("#"), s.find(";")] if i != -1]
        if idxs:
            cut = min(idxs)
            return s[:cut]
        return s

    def _split_comment(self, line):
        s = line
        idxs = [i for i in [s.find("//"), s.find("#"), s.find(";")] if i != -1]
        if idxs:
            cut = min(idxs)
            return s[:cut].rstrip(), s[cut:]
        return s.rstrip("\n"), "\n"

    def _split_key_value(self, pre):
        if "=" in pre:
            key_part, rest = pre.split("=", 1)
            return key_part, "=", rest
        return pre, "", ""

    def _ensure_section(self, section):
        if section not in self._sections:
            self._lines.append(f"\n[{section}]\n")
            self._sections.append(section)

    def _find_section_insert_point(self, section):
        for i, raw in enumerate(self._lines):
            line = raw.strip()
            if line == f"[{section}]":
                return i + 1
        return len(self._lines)


class GTAVRootsDialog(QtWidgets.QDialog):
    """Startup dialog to select or add GTAV installations before opening main window."""

    def __init__(self, roots: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select GTAV Installation")
        self.setMinimumSize(600, 400)
        self._roots = [dict(r) for r in roots]
        self._selected: Optional[Tuple[str, str]] = None
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        info = QtWidgets.QLabel("Choose a GTAV installation or add a new one.")
        layout.addWidget(info)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(container)
        for entry in self._roots:
            btn = self._make_root_button(entry)
            vbox.addWidget(btn)
        vbox.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        actions = QtWidgets.QHBoxLayout()
        add_btn = QtWidgets.QPushButton("Add GTAV Root")
        add_btn.setIcon(QtGui.QIcon(os.path.join("icons", "gtav_logo.png")))
        add_btn.clicked.connect(self._add_root)
        actions.addWidget(add_btn)

        manage_btn = QtWidgets.QPushButton("Add via File Picker")
        manage_btn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton))
        manage_btn.clicked.connect(self._pick_and_add)
        actions.addWidget(manage_btn)

        actions.addStretch()

        close_btn = QtWidgets.QPushButton("Continue")
        close_btn.setIcon(QtGui.QIcon(os.path.join("icons", "rage_plugin_hook_logo.png")))
        close_btn.clicked.connect(self._on_continue)
        actions.addWidget(close_btn)
        layout.addLayout(actions)

    def _make_root_button(self, entry: Dict[str, Any]) -> QtWidgets.QPushButton:
        ver = entry.get("version") or "unknown"
        path = entry.get("path") or ""
        btn = QtWidgets.QPushButton(f"{ver} | {path}")
        btn.setIcon(QtGui.QIcon(os.path.join("icons", "gtav_logo.png")))
        btn.setIconSize(QtCore.QSize(48, 48))
        btn.setMinimumHeight(60)
        btn.setStyleSheet("text-align: left; padding: 8px; font-size: 14px;")
        btn.clicked.connect(lambda: self._select_root(path, ver))
        return btn

    def _select_root(self, path: str, version: str):
        self._selected = (path, version)
        self.accept()

    def _add_root(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select GTAV Root Directory", "")
        if not path:
            return
        self._roots.append({"path": path, "version": "unknown"})
        self._rebuild_buttons()

    def _pick_and_add(self):
        self._add_root()

    def _rebuild_buttons(self):
        scroll = self.findChild(QtWidgets.QScrollArea)
        if not scroll:
            return
        container = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(container)
        for entry in self._roots:
            vbox.addWidget(self._make_root_button(entry))
        vbox.addStretch()
        scroll.setWidget(container)

    def _on_continue(self):
        self.accept()

    def selected_root(self) -> Optional[Tuple[str, str]]:
        return self._selected


__all__ = [
    "ConfigEditorDialog",
    "PluginConfigDialog",
    "CommentPreservingIni",
    "GTAVRootsDialog",
]
