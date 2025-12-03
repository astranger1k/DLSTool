"""Data models used across the DLS tool."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DLSVersion(Enum):
    V1 = "v1"
    V2 = "v2"
    UNKNOWN = "unknown"


@dataclass
class SirenItem:
    rotation: Dict[str, Any] = field(default_factory=dict)
    flashiness: Dict[str, Any] = field(default_factory=dict)
    corona: Dict[str, Any] = field(default_factory=dict)
    color: str = "0xFFFFFFFF"
    intensity: float = 1.0
    lightGroup: int = 0
    rotate: bool = False
    scale: bool = True
    scaleFactor: float = 1.0
    flash: bool = True
    light: bool = True
    spotLight: bool = True
    castShadows: bool = False


@dataclass
class SirenSettings:
    timeMultiplier: float = 1.0
    lightFalloffMax: float = 10.0
    lightFalloffExponent: float = 10.0
    lightInnerConeAngle: float = 2.29061
    lightOuterConeAngle: float = 70.0
    lightOffset: float = 0.0
    textureName: str = "VehicleLight_sirenlight"
    sequencerBpm: int = 220
    leftHeadLight: int = 0
    rightHeadLight: int = 0
    leftTailLight: int = 0
    rightTailLight: int = 0
    leftHeadLightMultiples: int = 1
    rightHeadLightMultiples: int = 1
    leftTailLightMultiples: int = 1
    rightTailLightMultiples: int = 1
    useRealLights: bool = True
    sirens: List[SirenItem] = field(default_factory=list)


@dataclass
class DLSv1Data:
    vehicles: str = ""
    stage1_enabled: bool = True
    stage2_enabled: bool = True
    stage3_enabled: bool = True
    custom_stage1_enabled: bool = False
    custom_stage2_enabled: bool = False
    get_stage3_from_carcols: bool = False

    siren_ui: str = ""
    preset_siren_on_leave: str = "none"
    wail_setup_enabled: bool = False
    wail_light_stage: str = ""
    wail_siren_tone: str = ""
    steady_burn_enabled: bool = False
    steady_burn_pattern: str = ""
    steady_burn_sirens: str = ""

    tone1: str = "VEHICLES_HORNS_SIREN_1"
    tone2: str = "VEHICLES_HORNS_SIREN_2"
    tone3: str = "VEHICLES_HORNS_POLICE_WARNING"
    tone4: str = "VEHICLES_HORNS_AMBULANCE_WARNING"
    horn: str = "SIRENS_AIRHORN"
    air_horn_interrupts_siren: bool = False

    traffic_advisory_type: str = "off"
    traffic_advisory_diverge_only: bool = False
    traffic_advisory_auto_enable_stages: str = ""
    traffic_advisory_default_direction: str = ""
    traffic_advisory_auto_disable_stages: str = ""
    traffic_advisory_patterns: Dict[str, str] = field(default_factory=dict)

    stage1: Optional[SirenSettings] = None
    stage2: Optional[SirenSettings] = None
    stage3: Optional[SirenSettings] = None
    custom_stage1: Optional[SirenSettings] = None
    custom_stage2: Optional[SirenSettings] = None


@dataclass
class AudioMode:
    name: str
    soundset: str = ""
    soundbank: str = ""
    sound_name: str = ""
    yield_enabled: bool = False


@dataclass
class LightMode:
    name: str
    yield_enabled: bool = False
    extras: List[Dict[str, Any]] = field(default_factory=list)
    siren_settings: Optional[SirenSettings] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioControlModeEntry:
    names: List[str] = field(default_factory=list)
    toggle: str = ""
    hold: str = ""


@dataclass
class AudioControlGroup:
    name: str = ""
    cycle: str = ""
    rev_cycle: str = ""
    toggle: str = ""
    exclusive: bool = False
    modes: List[AudioControlModeEntry] = field(default_factory=list)


@dataclass
class DLSv2Data:
    vehicles: str = "police"
    audio_modes: List[AudioMode] = field(default_factory=list)
    audio_control_groups: List[AudioControlGroup] = field(default_factory=list)
    light_modes: List[LightMode] = field(default_factory=list)
    pattern_sync: str = ""
    speed_drift: float = 0.0
    default_mode: str = ""
