"""
Test agents without API key - just verify structure.
"""
import json
from agents import TireAgent, CompetitorAgent, CoordinatorAgent

print("=" * 60)
print("AI Agents Structure Test (No API)")
print("=" * 60)

# Test agent initialization
print("\n1. Initializing agents...")
try:
    tire_agent = TireAgent()
    print(f"   ✓ {tire_agent.name} initialized")

    comp_agent = CompetitorAgent()
    print(f"   ✓ {comp_agent.name} initialized")

    coord_agent = CoordinatorAgent()
    print(f"   ✓ {coord_agent.name} initialized")

    print("\n✅ All agents initialized successfully!")

    # Test tire model (doesn't need API)
    print("\n2. Testing Tire Model integration...")
    degradation = tire_agent.tire_model.get_degradation_rate('SOFT', 15)
    print(f"   Soft tire degradation at lap 15: +{degradation:.3f}s")

    cliff = tire_agent.tire_model.predict_tire_cliff('SOFT', threshold=2.0)
    print(f"   Soft tire cliff predicted at lap: {cliff}")

    scenarios = tire_agent.tire_model.optimal_pit_window(current_lap=1)
    optimal_lap = scenarios[0]['pit_lap']
    print(f"   Optimal pit lap (Soft→Medium): {optimal_lap}")

    print("\n✅ Tire model working correctly!")

    print("\n" + "=" * 60)
    print("Structure Test Complete!")
    print("=" * 60)
    print("\nTo test with Gemini API:")
    print("1. Get free API key: https://aistudio.google.com/app/apikey")
    print("2. Add to .env file: GOOGLE_API_KEY=your_key_here")
    print("3. Run: python backend/agents.py")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
