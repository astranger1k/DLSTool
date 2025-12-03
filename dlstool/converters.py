"""Format conversion helpers between DLS v1 and v2."""
import logging

from .models import AudioMode, DLSv1Data, DLSv2Data, LightMode

logger = logging.getLogger(__name__)


class V1ToV2Converter:
    """Convert parsed DLS v1 structures into v2 structures."""

    @staticmethod
    def convert(v1_data: DLSv1Data) -> DLSv2Data:
        logger.info("Converting DLS v1 to v2...")
        v2_data = DLSv2Data()

        audio_map = [
            ("Siren1", v1_data.tone1, "slow"),
            ("Siren2", v1_data.tone2, "fast"),
            ("Siren3", v1_data.tone3, "warning"),
            ("Siren4", v1_data.tone4, "warning"),
            ("Siren_Horn", v1_data.horn, "horn"),
        ]

        for name, sound_full, sound_short in audio_map:
            if sound_full:
                mode = AudioMode(name=name, soundset="policevehsirens", sound_name=sound_short)
                v2_data.audio_modes.append(mode)

        stage_map = [
            ("Stage 1", v1_data.stage1, v1_data.stage1_enabled),
            ("Stage 2", v1_data.stage2, v1_data.stage2_enabled),
            ("Stage 3", v1_data.stage3, v1_data.stage3_enabled),
            ("Custom Stage 1", v1_data.custom_stage1, v1_data.custom_stage1_enabled),
            ("Custom Stage 2", v1_data.custom_stage2, v1_data.custom_stage2_enabled),
        ]

        for name, settings, enabled in stage_map:
            if enabled and settings is not None:
                mode = LightMode(name=name, yield_enabled=False, siren_settings=settings)
                v2_data.light_modes.append(mode)

        logger.info("Converted %s light modes and %s audio modes", len(v2_data.light_modes), len(v2_data.audio_modes))
        logger.warning("v2-specific features (conditions, triggers, extras, animations) are not populated from v1")
        return v2_data


class V2ToV1Converter:
    """Convert parsed DLS v2 structures into v1 structures."""

    @staticmethod
    def convert(v2_data: DLSv2Data) -> DLSv1Data:
        logger.info("Converting DLS v2 to v1...")
        v1_data = DLSv1Data()

        sound_map = {
            "slow": "VEHICLES_HORNS_SIREN_1",
            "fast": "VEHICLES_HORNS_SIREN_2",
            "warning": "VEHICLES_HORNS_POLICE_WARNING",
            "horn": "SIRENS_AIRHORN",
        }

        for i, mode in enumerate(v2_data.audio_modes):
            sound_name = sound_map.get(mode.sound_name.lower(), f"VEHICLES_HORNS_{mode.sound_name.upper()}")
            if i == 0 or "siren1" in mode.name.lower():
                v1_data.tone1 = sound_name
            elif i == 1 or "siren2" in mode.name.lower():
                v1_data.tone2 = sound_name
            elif i == 2 or "siren3" in mode.name.lower():
                v1_data.tone3 = sound_name
            elif "siren4" in mode.name.lower():
                v1_data.tone4 = sound_name
            elif "horn" in mode.name.lower():
                v1_data.horn = sound_name

        stages_assigned = 0
        for i, mode in enumerate(v2_data.light_modes):
            if stages_assigned >= 5:
                logger.warning("Skipping mode '%s' - v1 supports max 5 stages", mode.name)
                break
            if i == 0:
                v1_data.stage1 = mode.siren_settings
                v1_data.stage1_enabled = True
            elif i == 1:
                v1_data.stage2 = mode.siren_settings
                v1_data.stage2_enabled = True
            elif i == 2:
                v1_data.stage3 = mode.siren_settings
                v1_data.stage3_enabled = True
            elif i == 3:
                v1_data.custom_stage1 = mode.siren_settings
                v1_data.custom_stage1_enabled = True
            elif i == 4:
                v1_data.custom_stage2 = mode.siren_settings
                v1_data.custom_stage2_enabled = True
            stages_assigned += 1

        logger.info("Converted %s light modes to v1 stages", stages_assigned)
        logger.warning("v2 features (conditions, triggers, extras, animations, paints, modkits) are lost in conversion")
        return v1_data
