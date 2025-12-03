"""Utilities for inferring DLS plugin version from configuration files."""
from __future__ import annotations

import logging
from configparser import ConfigParser
from typing import Optional

logger = logging.getLogger(__name__)


class VersionDetector:
    """Inspect INI contents and attempt to guess DLS plugin version."""

    @staticmethod
    def infer_from_ini(config: ConfigParser) -> Optional[str]:
        try:
            sections = set(config.sections())
            v1_signals = 0
            v2_signals = 0

            if "Keyboard" in sections:
                v1_signals += 2
                kb_keys = set(k.lower() for k in config["Keyboard"].keys())
                v1_kb_expected = {
                    "lightstage",
                    "tadvisor",
                    "sirentoggle",
                    "tone1",
                    "tone2",
                    "tone3",
                    "tone4",
                    "auxtoggle",
                    "manual",
                    "horn",
                    "steadyburn",
                    "interiorlt",
                    "indl",
                    "indr",
                    "hazard",
                    "lockall",
                    "uimodifier",
                    "uikey",
                }
                if kb_keys & v1_kb_expected:
                    v1_signals += 2

            if "UI" in sections:
                v1_signals += 1

            if "Settings" in sections:
                settings_keys = set(config["Settings"].keys())
                v1_settings_keys = {"sirencontrolnondls", "ailightscontrol", "indenabled", "brakelightsenabled"}
                v2_settings_keys = {"audioname", "audioref", "disabledcontrols", "extrapatch", "devmode", "brakelights"}
                if settings_keys & v1_settings_keys:
                    v1_signals += 2
                if settings_keys & v2_settings_keys:
                    v2_signals += 2

            v2_control_sections = {
                "lockall",
                "killall",
                "intlt",
                "indl",
                "indr",
                "hzrd",
                "cycle_stages",
                "reverse_cycle_stages",
                "toggle_stages",
                "toggle_stage3",
                "cycle_ta",
                "reverse_cycle_ta",
                "audio_horn",
                "toggle_siren",
                "cycle_siren",
                "reverse_cycle_siren",
                "audio_siren1_manual",
                "audio_siren1",
                "audio_siren2",
                "audio_siren3",
            }
            v2_control_hits = len({s.lower() for s in sections} & v2_control_sections)
            if v2_control_hits >= 2:
                v2_signals += 3

            if v2_signals > v1_signals and v2_signals >= 3:
                return "v2"
            if v1_signals > v2_signals and v1_signals >= 2:
                return "v1"
            if v2_signals >= 2:
                return "v2"
            if v1_signals >= 2:
                return "v1"
        except Exception:
            logger.debug("Failed to infer DLS version from INI", exc_info=True)
        return None
