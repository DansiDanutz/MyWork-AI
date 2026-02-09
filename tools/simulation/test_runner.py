#!/usr/bin/env python3
"""Quick test runner for user journey simulation."""

import sys
from pathlib import Path

# Add the tools directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from user_journey import UserJourneySimulator
    print("✅ UserJourneySimulator imported successfully")
    
    simulator = UserJourneySimulator()
    print("✅ Simulator instance created")
    
    # Test just the first stage
    print("🧪 Testing Stage 1...")
    grade = simulator.stage_1_signup_onboarding()
    print(f"✅ Stage 1 completed with grade: {grade}")
    
    print("🎉 Basic test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()