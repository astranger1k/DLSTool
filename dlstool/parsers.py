"""Parsers for DLS v1 and v2 XML files."""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Optional

from .models import (
    AudioControlGroup,
    AudioControlModeEntry,
    AudioMode,
    DLSv1Data,
    DLSv2Data,
    LightMode,
    SirenItem,
    SirenSettings,
)

logger = logging.getLogger(__name__)


class DLSv1Parser:
    """Parser for DLS v1 XML files."""

    @staticmethod
    def parse(xml_path: str) -> DLSv1Data:
        logger.info("Parsing DLS v1 file: %s", xml_path)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        data = DLSv1Data()

        models_text = root.findtext("Models", "")
        data.vehicles = models_text.strip() if models_text else ""

        stage_settings = root.find("StageSettings")
        if stage_settings is not None:
            data.stage1_enabled = stage_settings.findtext("Stage1Enabled", "true").lower() == "true"
            data.stage2_enabled = stage_settings.findtext("Stage2Enabled", "true").lower() == "true"
            data.stage3_enabled = stage_settings.findtext("Stage3Enabled", "true").lower() == "true"
            data.custom_stage1_enabled = stage_settings.findtext("CustomStage1Enabled", "false").lower() == "true"
            data.custom_stage2_enabled = stage_settings.findtext("CustomStage2Enabled", "false").lower() == "true"
            data.get_stage3_from_carcols = (
                stage_settings.findtext("GetStage3FromCarcols", "false").lower() == "true"
            )

        special_modes = root.find("SpecialModes")
        if special_modes is not None:
            data.siren_ui = special_modes.findtext("SirenUI", "")
            data.preset_siren_on_leave = special_modes.findtext("PresetSirenOnLeaveVehicle", "none")

            wail_setup = special_modes.find("WailSetup")
            if wail_setup is not None:
                data.wail_setup_enabled = wail_setup.findtext("WailSetupEnabled", "false").lower() == "true"
                data.wail_light_stage = wail_setup.findtext("WailLightStage", "")
                data.wail_siren_tone = wail_setup.findtext("WailSirenTone", "")

            steady_burn = special_modes.find("SteadyBurn")
            if steady_burn is not None:
                data.steady_burn_enabled = steady_burn.findtext("SteadyBurnEnabled", "false").lower() == "true"
                data.steady_burn_pattern = steady_burn.findtext("Pattern", "")
                data.steady_burn_sirens = steady_burn.findtext("Sirens", "")

        sound_settings = root.find("SoundSettings")
        if sound_settings is not None:
            data.tone1 = sound_settings.findtext("Tone1", "VEHICLES_HORNS_SIREN_1")
            data.tone2 = sound_settings.findtext("Tone2", "VEHICLES_HORNS_SIREN_2")
            data.tone3 = sound_settings.findtext("Tone3", "VEHICLES_HORNS_POLICE_WARNING")
            data.tone4 = sound_settings.findtext("Tone4", "VEHICLES_HORNS_AMBULANCE_WARNING")
            data.horn = sound_settings.findtext("Horn", "SIRENS_AIRHORN")
            data.air_horn_interrupts_siren = (
                sound_settings.findtext("AirHornInterruptsSiren", "false").lower() == "true"
            )

        traffic_advisory = root.find("TrafficAdvisory")
        if traffic_advisory is not None:
            data.traffic_advisory_type = traffic_advisory.findtext("Type", "off")
            data.traffic_advisory_diverge_only = traffic_advisory.findtext("DivergeOnly", "false").lower() == "true"
            data.traffic_advisory_auto_enable_stages = traffic_advisory.findtext("AutoEnableStages", "")
            data.traffic_advisory_default_direction = traffic_advisory.findtext("DefaultEnabledDirection", "")
            data.traffic_advisory_auto_disable_stages = traffic_advisory.findtext("AutoDisableStages", "")
            for pos in ["L", "EL", "CL", "C", "CR", "ER", "R"]:
                pattern = traffic_advisory.findtext(pos, "")
                if pattern:
                    data.traffic_advisory_patterns[pos] = pattern

        sirens = root.find("Sirens")
        if sirens is not None:
            data.stage1 = DLSv1Parser._parse_siren_settings(sirens.find("Stage1"))
            data.stage2 = DLSv1Parser._parse_siren_settings(sirens.find("Stage2"))
            data.stage3 = DLSv1Parser._parse_siren_settings(sirens.find("Stage3"))
            data.custom_stage1 = DLSv1Parser._parse_siren_settings(sirens.find("CustomStage1"))
            data.custom_stage2 = DLSv1Parser._parse_siren_settings(sirens.find("CustomStage2"))

        logger.info("DLS v1 parsing complete")
        return data

    @staticmethod
    def _parse_siren_settings(element: Optional[ET.Element]) -> Optional[SirenSettings]:
        if element is None:
            return None

        settings = SirenSettings()
        settings.timeMultiplier = float(DLSv1Parser._get_value(element, "timeMultiplier", "1"))
        settings.lightFalloffMax = float(DLSv1Parser._get_value(element, "lightFalloffMax", "10"))
        settings.lightFalloffExponent = float(DLSv1Parser._get_value(element, "lightFalloffExponent", "10"))
        settings.lightInnerConeAngle = float(DLSv1Parser._get_value(element, "lightInnerConeAngle", "2.29061"))
        settings.lightOuterConeAngle = float(DLSv1Parser._get_value(element, "lightOuterConeAngle", "70"))
        settings.lightOffset = float(DLSv1Parser._get_value(element, "lightOffset", "0"))
        settings.textureName = element.findtext("textureName", "VehicleLight_sirenlight")
        settings.sequencerBpm = int(DLSv1Parser._get_value(element, "sequencerBpm", "220"))

        settings.leftHeadLight = int(DLSv1Parser._get_value(element, "leftHeadLight/sequencer", "0"))
        settings.rightHeadLight = int(DLSv1Parser._get_value(element, "rightHeadLight/sequencer", "0"))
        settings.leftTailLight = int(DLSv1Parser._get_value(element, "leftTailLight/sequencer", "0"))
        settings.rightTailLight = int(DLSv1Parser._get_value(element, "rightTailLight/sequencer", "0"))

        settings.leftHeadLightMultiples = int(DLSv1Parser._get_value(element, "leftHeadLightMultiples", "1"))
        settings.rightHeadLightMultiples = int(DLSv1Parser._get_value(element, "rightHeadLightMultiples", "1"))
        settings.leftTailLightMultiples = int(DLSv1Parser._get_value(element, "leftTailLightMultiples", "1"))
        settings.rightTailLightMultiples = int(DLSv1Parser._get_value(element, "rightTailLightMultiples", "1"))
        settings.useRealLights = DLSv1Parser._get_value(element, "useRealLights", "true").lower() == "true"

        sirens_element = element.find("sirens")
        if sirens_element is not None:
            for item in sirens_element.findall("Item"):
                siren = DLSv1Parser._parse_siren_item(item)
                settings.sirens.append(siren)

        return settings

    @staticmethod
    def _parse_siren_item(element: ET.Element) -> SirenItem:
        siren = SirenItem()
        rotation = element.find("rotation")
        if rotation is not None:
            siren.rotation = {
                "delta": float(DLSv1Parser._get_value(rotation, "delta", "0")),
                "start": float(DLSv1Parser._get_value(rotation, "start", "0")),
                "speed": float(DLSv1Parser._get_value(rotation, "speed", "0")),
                "sequencer": int(DLSv1Parser._get_value(rotation, "sequencer", "0")),
                "multiples": int(DLSv1Parser._get_value(rotation, "multiples", "1")),
                "direction": DLSv1Parser._get_value(rotation, "direction", "false").lower() == "true",
                "syncToBpm": DLSv1Parser._get_value(rotation, "syncToBpm", "true").lower() == "true",
            }

        flashiness = element.find("flashiness")
        if flashiness is not None:
            siren.flashiness = {
                "delta": float(DLSv1Parser._get_value(flashiness, "delta", "0")),
                "start": float(DLSv1Parser._get_value(flashiness, "start", "0")),
                "speed": float(DLSv1Parser._get_value(flashiness, "speed", "0")),
                "sequencer": int(DLSv1Parser._get_value(flashiness, "sequencer", "0")),
                "multiples": int(DLSv1Parser._get_value(flashiness, "multiples", "1")),
                "direction": DLSv1Parser._get_value(flashiness, "direction", "false").lower() == "true",
                "syncToBpm": DLSv1Parser._get_value(flashiness, "syncToBpm", "true").lower() == "true",
            }

        corona = element.find("corona")
        if corona is not None:
            siren.corona = {
                "intensity": float(DLSv1Parser._get_value(corona, "intensity", "50")),
                "size": float(DLSv1Parser._get_value(corona, "size", "1")),
                "pull": float(DLSv1Parser._get_value(corona, "pull", "0")),
                "faceCamera": DLSv1Parser._get_value(corona, "faceCamera", "false").lower() == "true",
            }

        siren.color = DLSv1Parser._get_value(element, "color", "0xFFFFFFFF")
        siren.intensity = float(DLSv1Parser._get_value(element, "intensity", "1"))
        siren.lightGroup = int(DLSv1Parser._get_value(element, "lightGroup", "0"))
        siren.rotate = DLSv1Parser._get_value(element, "rotate", "false").lower() == "true"
        siren.scale = DLSv1Parser._get_value(element, "scale", "true").lower() == "true"
        siren.scaleFactor = float(DLSv1Parser._get_value(element, "scaleFactor", "1"))
        siren.flash = DLSv1Parser._get_value(element, "flash", "true").lower() == "true"
        siren.light = DLSv1Parser._get_value(element, "light", "true").lower() == "true"
        siren.spotLight = DLSv1Parser._get_value(element, "spotLight", "true").lower() == "true"
        siren.castShadows = DLSv1Parser._get_value(element, "castShadows", "false").lower() == "true"
        return siren

    @staticmethod
    def _get_value(element: ET.Element, path: str, default: str) -> str:
        parts = path.split("/")
        current = element
        for part in parts:
            current = current.find(part)
            if current is None:
                return default
        value = current.get("value")
        if value is not None:
            return value
        text = current.text
        if text is not None:
            return text.strip()
        return default


class DLSv2Parser:
    """Parser for DLS v2 XML files."""

    @staticmethod
    def parse(xml_path: str) -> DLSv2Data:
        logger.info("Parsing DLS v2 file: %s", xml_path)
        tree = ET.parse(xml_path)
        root = tree.getroot()
        data = DLSv2Data()
        data.vehicles = root.get("vehicles", "police")

        audio = root.find("Audio")
        if audio is not None:
            audio_modes = audio.find("AudioModes")
            if audio_modes is not None:
                for mode_elem in audio_modes.findall("AudioMode"):
                    mode = AudioMode(name=mode_elem.get("name", ""))
                    sound = mode_elem.find("Sound")
                    if sound is not None:
                        mode.soundset = sound.get("soundset", "")
                        mode.soundbank = sound.get("soundbank", "")
                        mode.sound_name = sound.text.strip() if sound.text else ""
                    yield_elem = mode_elem.find("Yield")
                    if yield_elem is not None:
                        mode.yield_enabled = yield_elem.get("enabled", "false").lower() == "true"
                    data.audio_modes.append(mode)

            acg_root = audio.find("AudioControlGroups")
            if acg_root is not None:
                for group_elem in acg_root.findall("AudioControlGroup"):
                    group = AudioControlGroup(
                        name=group_elem.get("name", ""),
                        cycle=group_elem.get("cycle", ""),
                        rev_cycle=group_elem.get("rev_cycle", ""),
                        toggle=group_elem.get("toggle", ""),
                        exclusive=group_elem.get("exclusive", "false").lower() == "true",
                    )
                    gmodes = group_elem.find("AudioModes")
                    if gmodes is not None:
                        for entry in gmodes.findall("AudioMode"):
                            names_text = (entry.text or "").strip()
                            names = [n.strip() for n in names_text.split(",") if n.strip()] if names_text else []
                            ac_entry = AudioControlModeEntry(
                                names=names,
                                toggle=entry.get("toggle", ""),
                                hold=entry.get("hold", ""),
                            )
                            group.modes.append(ac_entry)
                    data.audio_control_groups.append(group)

        modes = root.find("Modes")
        if modes is not None:
            for mode_elem in modes.findall("Mode"):
                mode = LightMode(name=mode_elem.get("name", ""))
                yield_elem = mode_elem.find("Yield")
                if yield_elem is not None:
                    mode.yield_enabled = yield_elem.get("enabled", "false").lower() == "true"
                extras = mode_elem.find("Extras")
                if extras is not None:
                    for extra in extras.findall("Extra"):
                        mode.extras.append(
                            {
                                "id": int(extra.get("ID", "0")),
                                "enabled": extra.get("Enabled", "false").lower() == "true",
                            }
                        )
                siren_settings_elem = mode_elem.find("SirenSettings")
                if siren_settings_elem is not None:
                    mode.siren_settings = DLSv1Parser._parse_siren_settings(siren_settings_elem)
                data.light_modes.append(mode)

        data.pattern_sync = root.findtext("PatternSync", "")
        speed_drift = root.find("SpeedDrift")
        if speed_drift is not None:
            data.speed_drift = float(speed_drift.text or "0")
        data.default_mode = root.findtext("DefaultMode", "")

        logger.info("DLS v2 parsing complete")
        return data
