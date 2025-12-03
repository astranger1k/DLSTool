"""Entry point for the DLS desktop tool UI."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from PySide6 import QtCore, QtGui, QtWidgets

from dlstool.analyzer import DLSAnalyzer
from dlstool.converters import V1ToV2Converter, V2ToV1Converter
from dlstool.dialogs import ConfigEditorDialog, GTAVRootsDialog, PluginConfigDialog
from dlstool.highlighter import XMLHighlighter
from dlstool.models import DLSVersion, DLSv1Data, DLSv2Data
from dlstool.parsers import DLSv1Parser, DLSv2Parser
from dlstool.writers import DLSv1Writer, DLSv2Writer
from dlstool.core.version_detection import VersionDetector
from dlstool.utils import read_ini_with_slash_comments


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DlsToolApp(QtWidgets.QMainWindow):
    """Main GUI application for DLS Tool"""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.current_version = DLSVersion.UNKNOWN
        self.v1_data = None
        self.v2_data = None
        self.current_folder = None
        self.folder_files = []
        # GTAV / DLS plugin context
        self.gtav_root = None
        self.dls_plugin_version = None
        self.dls_ini_path = None
        self.dls_dll_path = None
        self.dls_ini = None  # parsed config
        # Persisted GTAV roots
        self.gtav_roots = []  # list of dicts {path, version}
        self._roots_store_path = os.path.join(os.path.expanduser('~'), 'DLSTool.gtav_roots.json')
        
        self.init_ui()

    def _on_load_file_clicked(self):
        try:
            self.load_file()
        except AttributeError:
            # Fallback: open file dialog directly
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Open VCF File",
                self.current_folder if self.current_folder else "",
                "XML Files (*.xml);;All Files (*.*)"
            )
            if file_path:
                self.load_file_by_path(file_path)

    def _on_edit_config_clicked(self):
        try:
            self.edit_configuration()
        except AttributeError:
            QtWidgets.QMessageBox.information(self, "Edit Configuration", "Load a VCF first to edit configuration.")
    
    def _on_convert_v1_to_v2_clicked(self):
        try:
            self.convert_v1_to_v2()
        except AttributeError:
            QtWidgets.QMessageBox.information(self, "Convert", "Load a V1 VCF first to convert.")
    
    def _on_convert_v2_to_v1_clicked(self):
        try:
            self.convert_v2_to_v1()
        except AttributeError:
            QtWidgets.QMessageBox.information(self, "Convert", "Load a V2 VCF first to convert.")
    
    def _on_analyze_clicked(self):
        try:
            self.analyze_file()
        except AttributeError:
            QtWidgets.QMessageBox.information(self, "Analyze", "Load a VCF first to analyze.")
    
    def _on_browse_folder_clicked(self):
        try:
            self.browse_folder()
        except AttributeError:
            QtWidgets.QMessageBox.information(self, "Browse", "Unable to browse folders at this time.")
    
    def _on_file_selected(self, item):
        try:
            self.on_file_selected(item)
        except AttributeError:
            pass
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("DLSTool")
        self.setWindowIconText("DLSTool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Top toolbar
        toolbar_layout = QtWidgets.QHBoxLayout()
        
        self.load_button = QtWidgets.QPushButton("Load VCF File")
        self.load_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton))
        self.load_button.clicked.connect(self._on_load_file_clicked)
        toolbar_layout.addWidget(self.load_button)
        
        self.load_folder_button = QtWidgets.QPushButton("Browse Folder")
        self.load_folder_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon))
        self.load_folder_button.clicked.connect(self._on_browse_folder_clicked)
        toolbar_layout.addWidget(self.load_folder_button)

        # GTAV root and plugin config
        self.set_gtav_root_button = QtWidgets.QPushButton("Add GTAV Root")
        self.set_gtav_root_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DriveHDIcon))
        self.set_gtav_root_button.clicked.connect(self.set_gtav_root)
        toolbar_layout.addWidget(self.set_gtav_root_button)
        # Saved GTAV roots selector
        self.gtav_root_combo = QtWidgets.QComboBox()
        self.gtav_root_combo.setMinimumWidth(350)
        self.gtav_root_combo.currentIndexChanged.connect(self._on_gtav_root_selected)
        toolbar_layout.addWidget(self.gtav_root_combo)
        self.edit_plugin_button = QtWidgets.QPushButton("Edit Plugin Config (DLS.ini)")
        self.edit_plugin_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.edit_plugin_button.clicked.connect(self.edit_plugin_config)
        self.edit_plugin_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_plugin_button)
        
        # Detected VCF version label (hidden until a VCF is loaded)
        self._version_text_label = QtWidgets.QLabel("Detected VCF Version:")
        self.version_label = QtWidgets.QLabel("")
        self.version_label.setStyleSheet("font-weight: bold;")
        self._version_text_label.hide()
        self.version_label.hide()
        toolbar_layout.addWidget(self._version_text_label)
        toolbar_layout.addWidget(self.version_label)

        # Load saved roots and populate selector
        self._load_saved_roots()
        self._refresh_roots_combo()

        toolbar_layout.addStretch()
        
        self.edit_config_button = QtWidgets.QPushButton("Edit Configuration")
        self.edit_config_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.edit_config_button.clicked.connect(self._on_edit_config_clicked)
        self.edit_config_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_config_button)
        
        self.convert_v1_to_v2_button = QtWidgets.QPushButton("Convert V1 → V2")
        self.convert_v1_to_v2_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowForward))
        self.convert_v1_to_v2_button.clicked.connect(self._on_convert_v1_to_v2_clicked)
        self.convert_v1_to_v2_button.setEnabled(False)
        toolbar_layout.addWidget(self.convert_v1_to_v2_button)

        self.convert_v2_to_v1_button = QtWidgets.QPushButton("Convert V2 → V1")
        self.convert_v2_to_v1_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowBack))
        self.convert_v2_to_v1_button.clicked.connect(self._on_convert_v2_to_v1_clicked)
        self.convert_v2_to_v1_button.setEnabled(False)
        toolbar_layout.addWidget(self.convert_v2_to_v1_button)

        main_layout.addLayout(toolbar_layout)

        # Splitter for content
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # Left panel - File Browser and Analysis
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)

        # File list section
        left_layout.addWidget(QtWidgets.QLabel("<b>VCF Folder</b>"))
        self.breadcrumb_label = QtWidgets.QLabel("/")
        self.breadcrumb_label.setStyleSheet("color: #666; font-size: 10px;")
        left_layout.addWidget(self.breadcrumb_label)
        self.file_list = QtWidgets.QListWidget()
        self.file_list.itemClicked.connect(self._on_file_selected)
        self.file_list.setMaximumHeight(150)
        left_layout.addWidget(self.file_list)

        # Icons for explorer items
        style = QtWidgets.QApplication.style()
        self._icon_dir = style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DirIcon)
        self._icon_file = style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon)
        self._icon_up = style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ArrowUp)
        # Current folder view filter (relative directory or None for all)
        self._current_folder_filter = None
        self._files_by_relpath = []  # list of tuples (rel_path, full_path)
        self._all_dirs = []          # top-level relative directories
        self._all_dirs_set = set()   # all relative directories found

        # Analysis section
        left_layout.addWidget(QtWidgets.QLabel("<b>Analysis</b>"))

        self.analysis_panel = QtWidgets.QStackedWidget()
        self.analysis_overlay = self._create_analysis_overlay()
        self.analysis_panel.addWidget(self.analysis_overlay)

        self.analysis_content_widget = QtWidgets.QWidget()
        analysis_content_layout = QtWidgets.QVBoxLayout(self.analysis_content_widget)
        analysis_content_layout.setContentsMargins(0, 0, 0, 0)
        analysis_content_layout.setSpacing(6)

        self._build_analysis_summary(analysis_content_layout)

        self.analysis_tree = QtWidgets.QTreeWidget()
        self.analysis_tree.setColumnCount(2)
        self.analysis_tree.setHeaderLabels(["Metric", "Value"])
        self.analysis_tree.setAlternatingRowColors(True)
        self.analysis_tree.setRootIsDecorated(True)
        self.analysis_tree.setIndentation(14)
        self.analysis_tree.setUniformRowHeights(True)
        analysis_content_layout.addWidget(self.analysis_tree)
        self._show_analysis_placeholder()
        self.analysis_tree.itemDoubleClicked.connect(self._on_analysis_item_activated)

        self.analysis_panel.addWidget(self.analysis_content_widget)
        left_layout.addWidget(self.analysis_panel)
        self._set_analysis_overlay_visible(True)

        self.analyze_button = QtWidgets.QPushButton("Analyze File")
        self.analyze_button.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogInfoView))
        self.analyze_button.clicked.connect(self._on_analyze_clicked)
        self.analyze_button.setEnabled(False)
        left_layout.addWidget(self.analyze_button)

        splitter.addWidget(left_panel)

        # Right panel - XML Preview
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.addWidget(QtWidgets.QLabel("<b>XML Preview</b>"))

        self.xml_preview = QtWidgets.QTextEdit()
        self.xml_preview.setReadOnly(True)
        self.xml_preview.setFont(QtGui.QFont("Courier", 9))

        # Apply syntax highlighting
        self.xml_highlighter = XMLHighlighter(self.xml_preview.document())

        right_layout.addWidget(self.xml_preview)

        splitter.addWidget(right_panel)

        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Prompt for GTAV root on startup
        QtCore.QTimer.singleShot(0, self._auto_prompt_gtav_root)
        self._clear_loaded_vcf()

    def _on_gtav_root_selected(self, idx: int):
        if idx < 0 or idx >= len(self.gtav_roots):
            return
        entry = self.gtav_roots[idx]
        path = entry.get('path')
        if not path:
            return
        self._clear_loaded_vcf()
        # Switch context to selected root
        self.gtav_root = path
        plugins_dir = os.path.join(path, 'plugins')
        self.dls_dll_path = os.path.join(plugins_dir, 'DLS.dll')
        self.dls_ini_path = os.path.join(plugins_dir, 'DLS.ini')
        dls_vcf_dir = os.path.join(plugins_dir, 'DLS')
        # Re-parse ini to keep version fresh
        self.dls_plugin_version = None
        self.dls_ini = None
        if os.path.exists(self.dls_ini_path):
            try:
                self.dls_ini = read_ini_with_slash_comments(self.dls_ini_path)
                inferred = self._infer_dls_version_from_ini(self.dls_ini)
                self.dls_plugin_version = inferred or 'unknown'
            except Exception:
                self.dls_plugin_version = 'unknown'
        # Populate VCFs for this root
        if os.path.isdir(dls_vcf_dir):
            self.current_folder = dls_vcf_dir
            if hasattr(self, '_index_folder'):
                self._index_folder(self.current_folder)
            if hasattr(self, '_populate_explorer_list'):
                self._populate_explorer_list()
        # Update status
        ver_txt = self.dls_plugin_version or 'unknown'
        self.statusBar().showMessage(f"GTAV Root: {path} | DLS Plugin Version: {ver_txt}")

    def _load_saved_roots(self):
        try:
            if os.path.exists(self._roots_store_path):
                with open(self._roots_store_path, 'r', encoding='utf-8') as f:
                    self.gtav_roots = json.load(f)
        except Exception:
            self.gtav_roots = []

    def _save_roots(self):
        try:
            with open(self._roots_store_path, 'w', encoding='utf-8') as f:
                json.dump(self.gtav_roots, f, indent=2)
        except Exception:
            pass

    def _add_or_update_root(self, path: str, version: str):
        # Update if exists, else append
        for entry in self.gtav_roots:
            if entry.get('path') == path:
                entry['version'] = version
                self._save_roots()
                return
        self.gtav_roots.append({'path': path, 'version': version})
        self._save_roots()

    def _refresh_roots_combo(self):
        # Update the combo box entries to show version and path
        self.gtav_root_combo.blockSignals(True)
        self.gtav_root_combo.clear()
        for entry in self.gtav_roots:
            ver = entry.get('version') or 'unknown'
            path = entry.get('path') or ''
            self.gtav_root_combo.addItem(f"{ver} | {path}")
        self.gtav_root_combo.blockSignals(False)

    def _auto_prompt_gtav_root(self):
        """Prompt user to set GTAV root, then auto-detect plugin info and VCFs."""
        if not self.gtav_root:
            dialog = GTAVRootsDialog(self.gtav_roots, parent=self)
            result = dialog.exec()
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                chosen = dialog.selected_root()
                if chosen:
                    path, version = chosen
                    self._add_or_update_root(path, version or 'unknown')
                    self._refresh_roots_combo()
                    # Switch to chosen - use set_gtav_root logic instead
                    self.gtav_root = path
                    plugins_dir = os.path.join(path, 'plugins')
                    self.dls_dll_path = os.path.join(plugins_dir, 'DLS.dll')
                    self.dls_ini_path = os.path.join(plugins_dir, 'DLS.ini')
                    dls_vcf_dir = os.path.join(plugins_dir, 'DLS')
                    self._clear_loaded_vcf()
                    
                    # Parse INI if exists
                    self.dls_ini = None
                    self.dls_plugin_version = None
                    if os.path.exists(self.dls_ini_path):
                        try:
                            config = read_ini_with_slash_comments(self.dls_ini_path)
                            self.dls_ini = config
                            self.edit_plugin_button.setEnabled(True)
                            self.dls_plugin_version = self._infer_dls_version_from_ini(config) or 'unknown'
                        except Exception as e:
                            logger.warning(f"Failed to parse DLS.ini: {e}")
                    
                    # Populate explorer with VCFs
                    if os.path.isdir(dls_vcf_dir):
                        logger.info(f"Auto-loading VCF folder: {dls_vcf_dir}")
                        self.current_folder = dls_vcf_dir
                        self._index_folder(self.current_folder)
                        logger.info(f"Indexed {len(self.folder_files)} files")
                        self._populate_explorer_list()
                        logger.info(f"Explorer populated with {self.file_list.count()} items")
                    else:
                        logger.warning(f"VCF directory not found: {dls_vcf_dir}")
                    
                    # Update status
                    ver_txt = self.dls_plugin_version or 'unknown'
                    self.statusBar().showMessage(f"GTAV Root: {path} | DLS Plugin Version: {ver_txt}")
                else:
                    # If user added a root but didn't select, choose first
                    if self.gtav_roots:
                        self._on_gtav_root_selected(0)

    def set_gtav_root(self):
        """Select the GTAV root directory and detect DLS plugin files."""
        root = QtWidgets.QFileDialog.getExistingDirectory(self, "Select GTAV Root Directory", "")
        if not root:
            return
        import os, configparser
        self.gtav_root = root
        plugins_dir = os.path.join(root, 'plugins')
        self.dls_dll_path = os.path.join(plugins_dir, 'DLS.dll')
        self.dls_ini_path = os.path.join(plugins_dir, 'DLS.ini')
        dls_vcf_dir = os.path.join(plugins_dir, 'DLS')

        # Detect plugin version (from file version if available)
        self.dls_plugin_version = None
        self._clear_loaded_vcf()

        # Parse INI if exists
        self.dls_ini = None
        if os.path.exists(self.dls_ini_path):
            try:
                config = read_ini_with_slash_comments(self.dls_ini_path)
                self.dls_ini = config
                self.edit_plugin_button.setEnabled(True)
                # Infer plugin version from INI contents (preferred over file timestamps)
                self.dls_plugin_version = self._infer_dls_version_from_ini(config) or self.dls_plugin_version
            except Exception as e:
                logger.warning(f"Failed to parse DLS.ini: {e}")

        # Populate explorer with VCFs under plugins/DLS
        if os.path.isdir(dls_vcf_dir):
            self.current_folder = dls_vcf_dir
            self._index_folder(self.current_folder)
            self._populate_explorer_list()
            msg = f"GTAV root set. Found VCFs under {dls_vcf_dir}."
        else:
            msg = f"GTAV root set to {root}. No VCF folder at plugins/DLS."

        # Update status/version label
        ver_txt = self.dls_plugin_version or 'unknown'
        self.statusBar().showMessage(f"GTAV Root: {root} | DLS Plugin Version: {ver_txt}")
        QtWidgets.QMessageBox.information(self, "GTAV Root Set", msg)

    def _infer_dls_version_from_ini(self, config) -> Optional[str]:
        """Try to infer DLS plugin version from DLS.ini by inspecting known keys.
        Returns a string like 'v1', 'v2', or a semantic version if present, else None.
        """
        try:
            sections = set(config.sections())

            # Heuristics based on template differences
            # v1: sections [Keyboard], [Settings], [UI] with keys like LightStage, UIModifier, UIKey
            # v2: [Settings] has AudioName/AudioRef/DisabledControls/ExtraPatch/DevMode/BrakeLights
            #     plus many control-group sections (e.g., [CYCLE_STAGES], [AUDIO_SIREN1])

            v1_signals = 0
            v2_signals = 0

            # v1 sections/keys
            if 'Keyboard' in sections:
                v1_signals += 2
                kb_keys = set(config['Keyboard'].keys())
                v1_kb_expected = {
                    'lightstage', 'tadvisor', 'sirentoggle', 'tone1', 'tone2', 'tone3', 'tone4',
                    'auxtoggle', 'manual', 'horn', 'steadyburn', 'interiorlt', 'indl', 'indr',
                    'hazard', 'lockall', 'uimodifier', 'uikey'
                }
                if kb_keys & v1_kb_expected:
                    v1_signals += 2

            if 'UI' in sections:
                v1_signals += 1

            if 'Settings' in sections:
                settings_keys = set(config['Settings'].keys())
                v1_settings_keys = {'sirencontrolnondls', 'ailightscontrol', 'indenabled', 'brakelightsenabled'}
                v2_settings_keys = {'audioname', 'audioref', 'disabledcontrols', 'extrapatch', 'devmode', 'brakelights'}
                if settings_keys & v1_settings_keys:
                    v1_signals += 2
                if settings_keys & v2_settings_keys:
                    v2_signals += 2

            # v2 control-group sections
            v2_control_sections = {
                'lockall', 'killall', 'intlt', 'indl', 'indr', 'hzrd',
                'cycle_stages', 'reverse_cycle_stages', 'toggle_stages', 'toggle_stage3',
                'cycle_ta', 'reverse_cycle_ta', 'audio_horn', 'toggle_siren', 'cycle_siren',
                'reverse_cycle_siren', 'audio_siren1_manual', 'audio_siren1', 'audio_siren2', 'audio_siren3'
            }
            v2_control_hits = len({s.lower() for s in sections} & v2_control_sections)
            if v2_control_hits >= 2:
                v2_signals += 3

            # Decide
            if v2_signals > v1_signals and v2_signals >= 3:
                return 'v2'
            if v1_signals > v2_signals and v1_signals >= 2:
                return 'v1'
            if v2_signals >= 2:
                return 'v2'
            if v1_signals >= 2:
                return 'v1'
        except Exception:
            logger.debug("Failed to infer DLS version from INI")
        return None
    
    def _index_folder(self, folder_path: str):
        """Index XML files and directories for explorer (shared by browse and GTAV root)."""
        import os
        self.folder_files = []
        self.file_list.clear()
        files_found = []
        all_dirs = set()
        for root, dirs, files in os.walk(folder_path):
            for d in dirs:
                dir_full = os.path.join(root, d)
                dir_rel = os.path.relpath(dir_full, folder_path).replace('\\', '/')
                if dir_rel != '.':
                    all_dirs.add(dir_rel)
            for filename in files:
                if filename.endswith('.xml'):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, folder_path)
                    files_found.append((rel_path.replace('\\', '/'), full_path))
        files_found.sort(key=lambda t: t[0].lower())
        self._files_by_relpath = files_found
        self.folder_files = [fp for _, fp in files_found]
        self._all_dirs_set = all_dirs
        self._all_dirs = sorted([d for d in all_dirs if '/' not in d], key=lambda s: s.lower())
        self._current_folder_filter = None

    def edit_plugin_config(self):
        """Open a simple editor for DLS.ini (read/write)."""
        if not self.dls_ini_path or not self.dls_ini:
            QtWidgets.QMessageBox.warning(self, "Plugin Config", "DLS.ini not found or not parsed.")
            return
        dialog = PluginConfigDialog(self.dls_ini, self.dls_ini_path, self)
        dialog.exec()
        # Re-read INI after save
        if os.path.exists(self.dls_ini_path):
            try:
                self.dls_ini = read_ini_with_slash_comments(self.dls_ini_path)
            except Exception as e:
                logger.warning(f"Failed to re-parse DLS.ini after save: {e}")
    
    def browse_folder(self):
        """Browse and load a folder containing VCF files"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Folder with VCF Files",
            ""
        )
        
        if not folder_path:
            return
        
        self._clear_loaded_vcf()

        try:
            self.current_folder = folder_path
            self.folder_files = []
            self.file_list.clear()

            # Find all XML files recursively in the folder and index directories
            import os
            files_found = []  # list of (rel_path, full_path)
            all_dirs = set()
            for root, dirs, files in os.walk(folder_path):
                # collect directories
                for d in dirs:
                    dir_full = os.path.join(root, d)
                    dir_rel = os.path.relpath(dir_full, folder_path).replace('\\', '/')
                    if dir_rel != '.':
                        all_dirs.add(dir_rel)
                for filename in files:
                    if filename.endswith('.xml'):
                        full_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(full_path, folder_path)
                        files_found.append((rel_path.replace('\\', '/'), full_path))

            # Sort and store
            files_found.sort(key=lambda t: t[0].lower())
            self._files_by_relpath = files_found
            self.folder_files = [fp for _, fp in files_found]
            # Store directories: all and top-level only for initial display
            self._all_dirs_set = all_dirs
            self._all_dirs = sorted([d for d in all_dirs if '/' not in d], key=lambda s: s.lower())
            self._current_folder_filter = None

            # Populate explorer list with directories on top, then files
            self._populate_explorer_list()

            if self.folder_files:
                self.statusBar().showMessage(f"Loaded folder: {folder_path} ({len(self.folder_files)} XML files)")
                QtWidgets.QMessageBox.information(
                    self,
                    "Folder Loaded",
                    f"Found {len(self.folder_files)} XML files in folder.\n\nClick on a file to load and analyze it."
                )
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "No Files Found",
                    "No XML files found in the selected folder."
                )
                self.statusBar().showMessage("No XML files found in folder")
        
        except Exception as e:
            logger.error(f"Error browsing folder: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to browse folder:\n{str(e)}")
    def _populate_explorer_list(self):
        """Populate the explorer with directories first (with icons), then files."""
        import os
        self.file_list.clear()

        # Update breadcrumb
        if self._current_folder_filter is None:
            self.breadcrumb_label.setText("/")
        else:
            self.breadcrumb_label.setText(f"/ {self._current_folder_filter}")

        # Determine current filter and matching files
        current_filter = self._current_folder_filter  # None or relative directory

        # Compute directories to show: either top-level dirs or immediate child dirs under the filter
        if current_filter is None:
            dirs_to_show = list(self._all_dirs)
        else:
            prefix = current_filter.rstrip('/') + '/'
            child_dirs = [d for d in self._all_dirs_set if d.startswith(prefix) and '/' not in d[len(prefix):]]
            dirs_to_show = sorted(child_dirs, key=lambda s: s.lower())

        # Add navigation item when filtered
        if self._current_folder_filter is not None:
            # Compute parent directory
            parent_dir = '/'.join(self._current_folder_filter.rstrip('/').split('/')[:-1]) if '/' in self._current_folder_filter else None
            up_label = ".. (Up)" if parent_dir else ".. (Root)"
            up_item = QtWidgets.QListWidgetItem(up_label)
            up_item.setIcon(self._icon_up)
            up_item.setData(QtCore.Qt.ItemDataRole.UserRole, parent_dir)
            up_item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, 'up')
            self.file_list.addItem(up_item)

        # Add directories first
        for d in dirs_to_show:
            # Display base name when filtered for a cleaner look
            label = d if current_filter is None else os.path.basename(d.rstrip('/'))
            item = QtWidgets.QListWidgetItem(label)
            item.setIcon(self._icon_dir)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, d)
            item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, 'dir')
            self.file_list.addItem(item)

        # Add a visual separator (disabled item) if there are both dirs and files
        show_files = []
        if self._current_folder_filter is None:
            show_files = self._files_by_relpath
        else:
            prefix = self._current_folder_filter.rstrip('/') + '/'
            show_files = [t for t in self._files_by_relpath if t[0].startswith(prefix) or t[0] == self._current_folder_filter]

        if dirs_to_show and show_files:
            sep = QtWidgets.QListWidgetItem("— Files —")
            sep.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
            self.file_list.addItem(sep)

        # Add files
        for rel_path, full_path in show_files:
            # If filtered, and not under the filtered dir, skip
            if self._current_folder_filter is not None:
                prefix = self._current_folder_filter.rstrip('/') + '/'
                if not (rel_path.startswith(prefix) or rel_path == self._current_folder_filter):
                    continue
            item = QtWidgets.QListWidgetItem(rel_path)
            item.setIcon(self._icon_file)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, full_path)
            item.setData(QtCore.Qt.ItemDataRole.UserRole + 1, 'file')
            self.file_list.addItem(item)
    
    def on_file_selected(self, item):
        """Handle file selection from the list"""
        item_type = item.data(QtCore.Qt.ItemDataRole.UserRole + 1)
        if item_type == 'file':
            file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if file_path:
                self.load_file_by_path(file_path)
        elif item_type == 'dir':
            # Apply filter to show only files under this directory
            dir_rel = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self._current_folder_filter = dir_rel
            self._populate_explorer_list()
        elif item_type == 'up':
            # Navigate to parent directory (stored in UserRole)
            parent_dir = item.data(QtCore.Qt.ItemDataRole.UserRole)
            self._current_folder_filter = parent_dir
            self._populate_explorer_list()
        else:
            # Fallback: try to treat as file path
            file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(file_path, str):
                self.load_file_by_path(file_path)
    
    def load_file(self):
        """Load a VCF file via dialog"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open VCF File",
            self.current_folder if self.current_folder else "",
            "XML Files (*.xml);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        self.load_file_by_path(file_path)
    
    def load_file_by_path(self, file_path: str):
        """Load a VCF file from a given path"""
        try:
            self.statusBar().showMessage(f"Loading {file_path}...")

            detected_version = self.detect_version(file_path)
            if detected_version in (None, DLSVersion.UNKNOWN):
                QtWidgets.QMessageBox.warning(self, "Unknown Format", "Could not detect DLS version")
                self._clear_loaded_vcf()
                return

            self.current_version = detected_version
            self.version_label.setText(self.current_version.value.upper())
            self._version_text_label.show()
            self.version_label.show()

            if self.current_version == DLSVersion.V1:
                self.v1_data = DLSv1Parser.parse(file_path)
                self.v2_data = None
                self.convert_v1_to_v2_button.setEnabled(True)
                self.convert_v2_to_v1_button.setEnabled(False)
                self.edit_config_button.setEnabled(True)
            elif self.current_version == DLSVersion.V2:
                self.v2_data = DLSv2Parser.parse(file_path)
                self.v1_data = None
                self.convert_v1_to_v2_button.setEnabled(False)
                self.convert_v2_to_v1_button.setEnabled(True)
                self.edit_config_button.setEnabled(True)
            else:
                QtWidgets.QMessageBox.warning(self, "Unsupported Format", "This file is neither DLS v1 nor v2.")
                self._clear_loaded_vcf()
                return

            self.analyze_button.setEnabled(True)

            with open(file_path, 'r', encoding='utf-8') as f:
                self.xml_preview.setPlainText(f.read())

            self.current_file = file_path
            self._set_analysis_overlay_visible(False)
            self.statusBar().showMessage(f"Loaded {file_path}")

            self.analyze_file()

            import os
            filename = os.path.basename(file_path)
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if item.text() == filename:
                    self.file_list.setCurrentItem(item)
                    break

        except Exception as e:
            logger.error(f"Error loading file: {e}", exc_info=True)
            self._clear_loaded_vcf()
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
    
    def detect_version(self, file_path: str) -> DLSVersion:
        """Detect DLS version from XML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # v2 has 'vehicles' attribute on root
            if root.get('vehicles') is not None:
                return DLSVersion.V2
            
            # v1 has StageSettings and SoundSettings
            if root.find('StageSettings') is not None or root.find('SoundSettings') is not None:
                return DLSVersion.V1
            
            # v2 has Audio and Modes
            if root.find('Audio') is not None or root.find('Modes') is not None:
                return DLSVersion.V2
            
        except Exception as e:
            logger.error(f"Error detecting version: {e}")
        
        return DLSVersion.UNKNOWN
    
    def analyze_file(self):
        """Analyze the loaded file"""
        try:
            if self.current_version == DLSVersion.V1 and self.v1_data:
                analysis = DLSAnalyzer.analyze_v1(self.v1_data)
            elif self.current_version == DLSVersion.V2 and self.v2_data:
                analysis = DLSAnalyzer.analyze_v2(self.v2_data)
            else:
                return
            
            self._populate_analysis_tree(analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing file: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to analyze file:\n{str(e)}")
    
    def edit_configuration(self):
        """Open configuration editor for the current file"""
        if not self.v1_data and not self.v2_data:
            return
        
        try:
            # Get current data and version
            data = self.v1_data if self.v1_data else self.v2_data
            version = self.current_version
            
            # Open editor dialog
            editor = ConfigEditorDialog(data, version, self)
            result = editor.exec()
            
            if result == QtWidgets.QDialog.DialogCode.Accepted and editor.modified:
                # Ask to save changes
                reply = QtWidgets.QMessageBox.question(
                    self,
                    "Save Changes",
                    "Do you want to save the configuration changes to a file?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
                )
                
                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    # Ask for save location
                    output_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                        self,
                        "Save Configuration",
                        self.current_file.replace('.xml', '_edited.xml'),
                        "XML Files (*.xml)"
                    )
                    
                    if output_path:
                        # Write the file
                        if version == DLSVersion.V1:
                            DLSv1Writer.write(data, output_path)
                        else:
                            DLSv2Writer.write(data, output_path)
                        
                        QtWidgets.QMessageBox.information(
                            self,
                            "Save Complete",
                            f"Configuration saved to:\n{output_path}"
                        )
                        
                        # Reload the file if it's the same path
                        if output_path == self.current_file:
                            self.load_file_by_path(output_path)
                        
                        self.statusBar().showMessage(f"Configuration saved: {output_path}")
        
        except Exception as e:
            logger.error(f"Error editing configuration: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to edit configuration:\n{str(e)}")
    
    def _show_analysis_placeholder(self, message: Optional[str] = None):
        """Display a placeholder row when no analysis data is available."""
        if not hasattr(self, "analysis_tree"):
            return
        self.analysis_tree.clear()
        placeholder = QtWidgets.QTreeWidgetItem([
            message or "No analysis yet",
            "Load a VCF and click Analyze"
        ])
        placeholder.setFirstColumnSpanned(True)
        placeholder.setDisabled(True)
        self.analysis_tree.addTopLevelItem(placeholder)
        self._reset_analysis_summary()

    def _build_analysis_summary(self, layout: QtWidgets.QVBoxLayout):
        """Create metric cards that highlight key analysis values."""
        self.analysis_summary_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(self.analysis_summary_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        metrics = [
            ("version", "Version"),
            ("vehicles", "Vehicles"),
            ("total_sirens", "Total Sirens"),
            ("active_stages", "Active Stages"),
            ("light_modes", "Light Modes"),
            ("audio_modes", "Audio Modes"),
        ]

        self.summary_value_labels: Dict[str, QtWidgets.QLabel] = {}
        palette = QtWidgets.QApplication.palette()
        border_color = palette.color(QtGui.QPalette.ColorRole.Mid).name()
        text_color = palette.color(QtGui.QPalette.ColorRole.WindowText).name()

        for idx, (key, label_text) in enumerate(metrics):
            card = QtWidgets.QFrame()
            card.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
            card.setStyleSheet(
                f"QFrame {{ border: 1px solid {border_color}; border-radius: 8px; padding: 8px; }}"
            )
            card_layout = QtWidgets.QVBoxLayout(card)
            card_layout.setContentsMargins(6, 4, 6, 6)
            title = QtWidgets.QLabel(label_text)
            title.setStyleSheet(
                f"color: {text_color}; font-size: 10px; text-transform: uppercase; opacity: 0.8;"
            )
            value = QtWidgets.QLabel("–")
            value.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {text_color};")
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            card_layout.addStretch()
            grid.addWidget(card, idx // 2, idx % 2)
            self.summary_value_labels[key] = value

        layout.addWidget(self.analysis_summary_widget)
        self._reset_analysis_summary()

    def _reset_analysis_summary(self):
        if not hasattr(self, "summary_value_labels"):
            return
        for label in self.summary_value_labels.values():
            label.setText("–")

    def _update_analysis_summary(self, analysis: Dict[str, Any]):
        if not hasattr(self, "summary_value_labels"):
            return

        def set_value(key: str, value: Any):
            if key in self.summary_value_labels:
                self.summary_value_labels[key].setText(str(value))

        version = analysis.get("version", "–")
        vehicle_count = analysis.get("vehicle_count")
        if vehicle_count is None:
            vehicles_raw = analysis.get("vehicles")
            if isinstance(vehicles_raw, str):
                tokens = [part.strip() for part in vehicles_raw.split(',') if part.strip()]
                vehicle_count = len(tokens)
        if vehicle_count is None:
            vehicles_display = "–"
        else:
            vehicles_display = str(vehicle_count)
        total_sirens = analysis.get("total_sirens", 0)
        stages = analysis.get("stages") or {}
        active_stages = sum(1 for info in stages.values() if info.get("enabled")) if stages else "–"
        light_modes = len(analysis.get("light_modes", {})) or "–"
        audio_modes = len(analysis.get("audio_modes", {})) or "–"

        set_value("version", version)
        set_value("vehicles", vehicles_display)
        set_value("total_sirens", total_sirens)
        set_value("active_stages", active_stages)
        set_value("light_modes", light_modes)
        set_value("audio_modes", audio_modes)

    def _create_analysis_overlay(self) -> QtWidgets.QWidget:
        overlay = QtWidgets.QFrame()
        overlay.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        palette = QtWidgets.QApplication.palette()
        border_color = palette.color(QtGui.QPalette.ColorRole.Mid).name()
        overlay.setStyleSheet(
            f"QFrame {{ border: 1px dashed {border_color}; border-radius: 8px; background: palette(Base); }}"
        )

        layout = QtWidgets.QVBoxLayout(overlay)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        icon_label = QtWidgets.QLabel()
        icon = QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileIcon)
        icon_label.setPixmap(icon.pixmap(48, 48))
        layout.addWidget(icon_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        title = QtWidgets.QLabel("Select a VCF file to see analysis")
        title.setWordWrap(True)
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel("Choose a file from the explorer or browse manually to load it here.")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: palette(Mid);")
        layout.addWidget(subtitle)

        browse_btn = QtWidgets.QPushButton("Open VCF...")
        browse_btn.setFixedWidth(160)
        browse_btn.clicked.connect(self._on_load_file_clicked)
        layout.addWidget(browse_btn, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        hint = QtWidgets.QLabel("Tip: Use the file list above to pick a VCF from the current folder.")
        hint.setWordWrap(True)
        hint.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("font-size: 10px; color: palette(Mid);")
        layout.addWidget(hint)

        return overlay

    def _set_analysis_overlay_visible(self, visible: bool):
        if not hasattr(self, "analysis_panel"):
            return
        target = self.analysis_overlay if visible else self.analysis_content_widget
        if self.analysis_panel.currentWidget() is not target:
            self.analysis_panel.setCurrentWidget(target)

    def _clear_loaded_vcf(self):
        """Reset state when no VCF is loaded."""
        self.current_file = None
        self.current_version = DLSVersion.UNKNOWN
        self.v1_data = None
        self.v2_data = None
        self.xml_preview.clear()
        self.analyze_button.setEnabled(False)
        self.convert_v1_to_v2_button.setEnabled(False)
        self.convert_v2_to_v1_button.setEnabled(False)
        self.edit_config_button.setEnabled(False)
        self._version_text_label.hide()
        self.version_label.hide()
        self.version_label.clear()
        self._reset_analysis_summary()
        self._show_analysis_placeholder("Select a VCF to analyze")
        self._set_analysis_overlay_visible(True)

    def _populate_analysis_tree(self, analysis: Dict[str, Any]):
        """Render the structured analysis data as interactive tree items."""
        if not analysis:
            self._show_analysis_placeholder()
            return

        self.analysis_tree.clear()
        self._update_analysis_summary(analysis)

        def add_row(parent: QtWidgets.QTreeWidgetItem, label: str, value: Any):
            if value is None or value == "":
                return
            QtWidgets.QTreeWidgetItem(parent, [label, str(value)])

        def add_bool_row(parent: QtWidgets.QTreeWidgetItem, label: str, value: Optional[bool]):
            if value is None:
                return
            QtWidgets.QTreeWidgetItem(parent, [label, "Yes" if value else "No"])

        def prettify(text: str) -> str:
            return text.replace('_', ' ').title()

        def set_marker(item: QtWidgets.QTreeWidgetItem, marker: Optional[str]):
            if marker:
                item.setData(0, QtCore.Qt.ItemDataRole.UserRole, {"search": marker})
                item.setToolTip(0, "Double-click to jump to XML")

        root_item = QtWidgets.QTreeWidgetItem([f"{analysis.get('version', 'DLS')} Analysis", ""])
        root_item.setFirstColumnSpanned(True)
        root_item.setExpanded(True)
        self.analysis_tree.addTopLevelItem(root_item)

        summary_item = QtWidgets.QTreeWidgetItem(root_item, ["Summary", ""])
        summary_item.setExpanded(True)
        if 'vehicles' in analysis:
            add_row(summary_item, "Vehicles", analysis['vehicles'])
        add_row(summary_item, "Total Sirens", analysis.get('total_sirens', 0))

        stages = analysis.get('stages') or {}
        if stages:
            stages_item = QtWidgets.QTreeWidgetItem(root_item, ["Stages", ""])
            stages_item.setExpanded(True)
            for name, info in stages.items():
                state = "Enabled" if info.get('enabled') else "Disabled"
                stage_item = QtWidgets.QTreeWidgetItem(stages_item, [name, state])
                add_row(stage_item, "Siren Count", info.get('siren_count'))
                add_row(stage_item, "BPM", info.get('bpm'))
                add_row(stage_item, "Texture", info.get('texture'))
                marker = info.get('xml_marker')
                if marker:
                    set_marker(stage_item, f"<{marker}")

        light_modes = analysis.get('light_modes') or {}
        if light_modes:
            modes_item = QtWidgets.QTreeWidgetItem(root_item, ["Light Modes", ""])
            modes_item.setExpanded(True)
            for name, info in light_modes.items():
                yield_state = "Yield" if info.get('yield_enabled') else "Standard"
                mode_item = QtWidgets.QTreeWidgetItem(modes_item, [name, yield_state])
                add_row(mode_item, "Sirens", info.get('siren_count'))
                add_row(mode_item, "Extras", info.get('extras_count'))
                add_row(mode_item, "BPM", info.get('bpm'))
                add_bool_row(mode_item, "Has Siren Settings", info.get('has_siren_settings'))
                marker = info.get('xml_marker')
                if marker:
                    set_marker(mode_item, f"name=\"{marker}\"")

        audio = analysis.get('audio') or {}
        if audio:
            audio_item = QtWidgets.QTreeWidgetItem(root_item, ["Audio", ""])
            for key, value in audio.items():
                add_row(audio_item, prettify(key), value)

        audio_modes = analysis.get('audio_modes') or {}
        if audio_modes:
            audio_modes_item = QtWidgets.QTreeWidgetItem(root_item, ["Audio Modes", ""])
            audio_modes_item.setExpanded(True)
            for name, info in audio_modes.items():
                details = f"{info.get('soundset','')} / {info.get('sound','')}"
                mode_item = QtWidgets.QTreeWidgetItem(audio_modes_item, [name, details.strip(" / ")])
                add_bool_row(mode_item, "Yield", info.get('yield_enabled'))
                marker = info.get('xml_marker')
                if marker:
                    set_marker(mode_item, f"name=\"{marker}\"")

        special = analysis.get('special_features') or {}
        if special:
            special_item = QtWidgets.QTreeWidgetItem(root_item, ["Special Features", ""])
            for key, value in special.items():
                add_row(special_item, prettify(key), "Enabled" if value else "Disabled")

        v2_features = analysis.get('features') or {}
        if v2_features:
            features_item = QtWidgets.QTreeWidgetItem(root_item, ["V2 Features", ""])
            for key, value in v2_features.items():
                add_row(features_item, prettify(key), "Enabled" if value else "Disabled")

        ac_groups = analysis.get('audio_control_groups') or {}
        if ac_groups:
            groups_item = QtWidgets.QTreeWidgetItem(root_item, ["Audio Control Groups", ""])
            groups_item.setExpanded(True)
            for name, info in ac_groups.items():
                state = "Exclusive" if info.get('exclusive') else "Shared"
                group_item = QtWidgets.QTreeWidgetItem(groups_item, [name, state])
                add_row(group_item, "Entries", info.get('entries'))
                add_row(group_item, "Modes Referenced", info.get('modes'))
                add_bool_row(group_item, "Has Cycle Key", info.get('cycle'))
                add_bool_row(group_item, "Has Toggle Key", info.get('toggle'))

        ta = analysis.get('traffic_advisory') or {}
        if ta:
            ta_item = QtWidgets.QTreeWidgetItem(
                root_item,
                ["Traffic Advisory", "Enabled" if ta.get('enabled') else "Disabled"]
            )
            if ta.get('enabled'):
                add_row(ta_item, "Type", ta.get('type'))
                add_row(ta_item, "Patterns Configured", ta.get('patterns'))
    
    def convert_v1_to_v2(self):
        """Convert loaded v1 file to v2"""
        if not self.v1_data:
            return
        
        try:
            # Convert
            v2_data = V1ToV2Converter.convert(self.v1_data)
            
            # Ask for save location
            output_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save V2 File",
                self.current_file.replace('.xml', '_v2.xml'),
                "XML Files (*.xml)"
            )
            
            if not output_path:
                return
            
            # Write
            DLSv2Writer.write(v2_data, output_path)
            
            QtWidgets.QMessageBox.information(
                self,
                "Conversion Complete",
                f"Successfully converted to V2 format!\n\nNote: V2-specific features (conditions, triggers) were not populated.\n\nSaved to: {output_path}"
            )
            
            self.statusBar().showMessage(f"Converted to V2: {output_path}")
            
        except Exception as e:
            logger.error(f"Error converting: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Error", f"Conversion failed:\n{str(e)}")

    def _on_analysis_item_activated(self, item: QtWidgets.QTreeWidgetItem, column: int):
        payload = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(payload, dict):
            marker = payload.get("search")
            if marker:
                if not self._highlight_xml_snippet(marker):
                    QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Section not found in XML preview.")

    def _highlight_xml_snippet(self, marker: str) -> bool:
        if not marker:
            return False
        cursor = self.xml_preview.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)
        self.xml_preview.setTextCursor(cursor)
        if self.xml_preview.find(marker):
            self.xml_preview.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
            self.xml_preview.centerCursor()
            return True
        return False
    
    def convert_v2_to_v1(self):
        """Convert loaded v2 file to v1"""
        if not self.v2_data:
            return
        
        try:
            # Convert
            v1_data = V2ToV1Converter.convert(self.v2_data)
            
            # Ask for save location
            output_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save V1 File",
                self.current_file.replace('.xml', '_v1.xml'),
                "XML Files (*.xml)"
            )
            
            if not output_path:
                return
            
            # Write
            DLSv1Writer.write(v1_data, output_path)
            
            QtWidgets.QMessageBox.warning(
                self,
                "Conversion Complete",
                f"Successfully converted to V1 format!\n\n⚠ Warning: V2-exclusive features (conditions, triggers, extras, animations, paints, modkits) were lost.\n\nSaved to: {output_path}"
            )
            
            self.statusBar().showMessage(f"Converted to V1: {output_path}")
            
        except Exception as e:
            logger.error(f"Error converting: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Error", f"Conversion failed:\n{str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = DlsToolApp()
    main_window.show()
    sys.exit(app.exec())
