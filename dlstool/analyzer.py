"""Utility helpers for summarising parsed DLS data."""
from typing import Any, Dict

from .models import DLSv1Data, DLSv2Data


class DLSAnalyzer:
    """Produce quick summaries of parsed VCF structures."""

    @staticmethod
    def analyze_v1(data: DLSv1Data) -> Dict[str, Any]:
        analysis: Dict[str, Any] = {
            "version": "DLS v1",
            "stages": {},
            "audio": {},
            "special_features": {},
            "traffic_advisory": {},
            "total_sirens": 0,
        }

        stages = {
            "Stage 1": (data.stage1, data.stage1_enabled),
            "Stage 2": (data.stage2, data.stage2_enabled),
            "Stage 3": (data.stage3, data.stage3_enabled),
            "Custom Stage 1": (data.custom_stage1, data.custom_stage1_enabled),
            "Custom Stage 2": (data.custom_stage2, data.custom_stage2_enabled),
        }

        stage_xml_tags = {
            "Stage 1": "Stage1",
            "Stage 2": "Stage2",
            "Stage 3": "Stage3",
            "Custom Stage 1": "CustomStage1",
            "Custom Stage 2": "CustomStage2",
        }

        for name, (settings, enabled) in stages.items():
            if enabled and settings:
                siren_count = len(settings.sirens)
                analysis["stages"][name] = {
                    "enabled": True,
                    "siren_count": siren_count,
                    "bpm": settings.sequencerBpm,
                    "texture": settings.textureName,
                    "xml_marker": stage_xml_tags.get(name, name.replace(" ", "")),
                }
                analysis["total_sirens"] += siren_count
            else:
                analysis["stages"][name] = {
                    "enabled": False,
                    "xml_marker": stage_xml_tags.get(name, name.replace(" ", "")),
                }

        analysis["audio"] = {
            "tone1": data.tone1,
            "tone2": data.tone2,
            "tone3": data.tone3,
            "tone4": data.tone4,
            "horn": data.horn,
            "air_horn_interrupts": data.air_horn_interrupts_siren,
        }

        analysis["special_features"] = {
            "custom_ui": bool(data.siren_ui),
            "wail_setup": data.wail_setup_enabled,
            "steady_burn": data.steady_burn_enabled,
            "preset_on_leave": data.preset_siren_on_leave != "none",
        }

        analysis["traffic_advisory"] = {
            "enabled": data.traffic_advisory_type != "off",
            "type": data.traffic_advisory_type,
            "patterns": len(data.traffic_advisory_patterns),
        }

        return analysis

    @staticmethod
    def analyze_v2(data: DLSv2Data) -> Dict[str, Any]:
        analysis: Dict[str, Any] = {
            "version": "DLS v2",
            "vehicles": data.vehicles,
            "light_modes": {},
            "audio_modes": {},
            "total_sirens": 0,
            "features": {},
        }

        for mode in data.light_modes:
            mode_info = {
                "yield_enabled": mode.yield_enabled,
                "extras_count": len(mode.extras),
                "has_siren_settings": mode.siren_settings is not None,
            }
            if mode.siren_settings:
                mode_info["siren_count"] = len(mode.siren_settings.sirens)
                mode_info["bpm"] = mode.siren_settings.sequencerBpm
                analysis["total_sirens"] += len(mode.siren_settings.sirens)
            mode_info["xml_marker"] = mode.name
            analysis["light_modes"][mode.name] = mode_info

        for mode in data.audio_modes:
            analysis["audio_modes"][mode.name] = {
                "soundset": mode.soundset,
                "sound": mode.sound_name,
                "yield_enabled": mode.yield_enabled,
                "xml_marker": mode.name,
            }

        analysis["features"] = {
            "pattern_sync": bool(data.pattern_sync),
            "speed_drift": data.speed_drift != 0,
            "default_mode": bool(data.default_mode),
            "audio_control_groups": len(data.audio_control_groups),
        }

        if data.audio_control_groups:
            acg_summary: Dict[str, Any] = {}
            for group in data.audio_control_groups:
                acg_summary[group.name or "(unnamed)"] = {
                    "exclusive": group.exclusive,
                    "modes": sum(len(entry.names) if entry.names else 0 for entry in group.modes),
                    "entries": len(group.modes),
                    "cycle": bool(group.cycle),
                    "toggle": bool(group.toggle),
                }
            analysis["audio_control_groups"] = acg_summary

        return analysis
