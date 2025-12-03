"""
Test script for DLS VCF conversion
Tests the conversion between v1 and v2 formats
"""

import sys
import os

# Ensure local package imports work when run directly
sys.path.insert(0, os.path.dirname(__file__))

from dlstool.analyzer import DLSAnalyzer
from dlstool.converters import V1ToV2Converter, V2ToV1Converter
from dlstool.parsers import DLSv1Parser, DLSv2Parser
from dlstool.writers import DLSv1Writer, DLSv2Writer

def test_v1_parsing():
    """Test parsing of DLS v1 file"""
    print("=" * 60)
    print("TEST 1: Parsing DLS v1 Template")
    print("=" * 60)
    
    v1_file = "./DLSv1/Templates/police.xml"
    try:
        v1_data = DLSv1Parser.parse(v1_file)
        print(f"✓ Successfully parsed {v1_file}")
        print(f"  - Stage 1 enabled: {v1_data.stage1_enabled}")
        print(f"  - Stage 2 enabled: {v1_data.stage2_enabled}")
        print(f"  - Stage 3 enabled: {v1_data.stage3_enabled}")
        
        if v1_data.stage1:
            print(f"  - Stage 1 sirens: {len(v1_data.stage1.sirens)}")
        if v1_data.stage2:
            print(f"  - Stage 2 sirens: {len(v1_data.stage2.sirens)}")
        if v1_data.stage3:
            print(f"  - Stage 3 sirens: {len(v1_data.stage3.sirens)}")
        
        print(f"  - Tone1: {v1_data.tone1}")
        print(f"  - Tone2: {v1_data.tone2}")
        
        # Analyze
        analysis = DLSAnalyzer.analyze_v1(v1_data)
        print(f"\n  Analysis: {analysis['total_sirens']} total sirens")
        
        return v1_data
    except Exception as e:
        print(f"✗ Failed to parse: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_v2_parsing():
    """Test parsing of DLS v2 file"""
    print("\n" + "=" * 60)
    print("TEST 2: Parsing DLS v2 Template")
    print("=" * 60)
    
    v2_file = "./DLSv2/Templates/default.xml"
    try:
        v2_data = DLSv2Parser.parse(v2_file)
        print(f"✓ Successfully parsed {v2_file}")
        print(f"  - Vehicles: {v2_data.vehicles}")
        print(f"  - Audio modes: {len(v2_data.audio_modes)}")
        print(f"  - Light modes: {len(v2_data.light_modes)}")
        
        for mode in v2_data.audio_modes[:3]:
            print(f"    - Audio: {mode.name} -> {mode.sound_name}")
        
        for mode in v2_data.light_modes[:3]:
            siren_count = len(mode.siren_settings.sirens) if mode.siren_settings else 0
            print(f"    - Light: {mode.name} -> {siren_count} sirens")
        
        # Analyze
        analysis = DLSAnalyzer.analyze_v2(v2_data)
        print(f"\n  Analysis: {analysis['total_sirens']} total sirens")
        
        return v2_data
    except Exception as e:
        print(f"✗ Failed to parse: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_v1_to_v2_conversion(v1_data):
    """Test conversion from v1 to v2"""
    print("\n" + "=" * 60)
    print("TEST 3: Converting V1 → V2")
    print("=" * 60)
    
    try:
        v2_data = V1ToV2Converter.convert(v1_data)
        print(f"✓ Successfully converted v1 to v2")
        print(f"  - Audio modes created: {len(v2_data.audio_modes)}")
        print(f"  - Light modes created: {len(v2_data.light_modes)}")
        
        # Write to file
        output_file = "./test_v1_to_v2_output.xml"
        DLSv2Writer.write(v2_data, output_file)
        print(f"✓ Saved converted file to {output_file}")
        
        return v2_data
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_v2_to_v1_conversion(v2_data):
    """Test conversion from v2 to v1"""
    print("\n" + "=" * 60)
    print("TEST 4: Converting V2 → V1")
    print("=" * 60)
    
    try:
        v1_data = V2ToV1Converter.convert(v2_data)
        print(f"✓ Successfully converted v2 to v1")
        print(f"  - Stage 1 enabled: {v1_data.stage1_enabled}")
        print(f"  - Stage 2 enabled: {v1_data.stage2_enabled}")
        print(f"  - Stage 3 enabled: {v1_data.stage3_enabled}")
        
        # Write to file
        output_file = "./test_v2_to_v1_output.xml"
        DLSv1Writer.write(v1_data, output_file)
        print(f"✓ Saved converted file to {output_file}")
        
        return v1_data
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_round_trip():
    """Test round-trip conversion v1 -> v2 -> v1"""
    print("\n" + "=" * 60)
    print("TEST 5: Round-trip Conversion (V1 → V2 → V1)")
    print("=" * 60)
    
    try:
        # Parse original v1
        v1_original = DLSv1Parser.parse("./DLSv1/Templates/police.xml")
        print("✓ Parsed original v1")
        
        # Convert to v2
        v2_converted = V1ToV2Converter.convert(v1_original)
        print("✓ Converted v1 → v2")
        
        # Convert back to v1
        v1_roundtrip = V2ToV1Converter.convert(v2_converted)
        print("✓ Converted v2 → v1")
        
        # Compare
        print("\nComparison:")
        print(f"  - Original v1 stage1 enabled: {v1_original.stage1_enabled}")
        print(f"  - Round-trip v1 stage1 enabled: {v1_roundtrip.stage1_enabled}")
        
        if v1_original.stage1 and v1_roundtrip.stage1:
            orig_sirens = len(v1_original.stage1.sirens)
            rt_sirens = len(v1_roundtrip.stage1.sirens)
            print(f"  - Original v1 stage1 sirens: {orig_sirens}")
            print(f"  - Round-trip v1 stage1 sirens: {rt_sirens}")
            
            if orig_sirens == rt_sirens:
                print("  ✓ Siren counts match!")
            else:
                print("  ⚠ Siren counts differ")
        
        print("\n✓ Round-trip test complete")
        
    except Exception as e:
        print(f"✗ Round-trip test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DLS VCF Conversion Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Parse v1
    v1_data = test_v1_parsing()
    
    # Test 2: Parse v2
    v2_data = test_v2_parsing()
    
    if v1_data:
        # Test 3: Convert v1 to v2
        v2_converted = test_v1_to_v2_conversion(v1_data)
    
    if v2_data:
        # Test 4: Convert v2 to v1
        v1_converted = test_v2_to_v1_conversion(v2_data)
    
    # Test 5: Round-trip
    test_round_trip()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - test_v1_to_v2_output.xml")
    print("  - test_v2_to_v1_output.xml")
    print("\nYou can inspect these files to verify the conversions.")


if __name__ == "__main__":
    main()
