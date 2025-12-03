"""
Debug script to check v2 to v1 conversion siren loss
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dls_tool import DLSv2Parser, V2ToV1Converter, DLSv1Writer

# Parse v2 template
print("Loading v2 template...")
v2_data = DLSv2Parser.parse("./DLSv2/Templates/default.xml")

print(f"\nv2 Data parsed:")
print(f"  - Light modes: {len(v2_data.light_modes)}")

for i, mode in enumerate(v2_data.light_modes[:5]):
    if mode.siren_settings:
        print(f"  - Mode {i+1} '{mode.name}': {len(mode.siren_settings.sirens)} sirens")
        print(f"    - siren_settings object: {mode.siren_settings}")
    else:
        print(f"  - Mode {i+1} '{mode.name}': NO siren_settings")

# Convert to v1
print("\n" + "="*60)
print("Converting to v1...")
v1_data = V2ToV1Converter.convert(v2_data)

print(f"\nv1 Data after conversion:")
print(f"  - stage1: {v1_data.stage1}")
print(f"  - stage2: {v1_data.stage2}")
print(f"  - stage3: {v1_data.stage3}")

if v1_data.stage1:
    print(f"  - Stage 1 sirens: {len(v1_data.stage1.sirens)}")
    print(f"    - stage1 object type: {type(v1_data.stage1)}")
else:
    print(f"  - Stage 1: NONE")

if v1_data.stage2:
    print(f"  - Stage 2 sirens: {len(v1_data.stage2.sirens)}")
else:
    print(f"  - Stage 2: NONE")

if v1_data.stage3:
    print(f"  - Stage 3 sirens: {len(v1_data.stage3.sirens)}")
else:
    print(f"  - Stage 3: NONE")

# Write to file
print("\n" + "="*60)
print("Writing v1 file...")
DLSv1Writer.write(v1_data, "debug_v2_to_v1_output.xml")
print("Written to debug_v2_to_v1_output.xml")
