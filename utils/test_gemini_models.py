#!/usr/bin/env python3
"""
TEST GEMINI MODELS
------------------
Test different Gemini models and see their responses
Fun way to verify which models are available and working

Run: python utils/test_gemini_models.py
"""

from google import genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

print("="*70)
print("  🤖 GEMINI MODELS TESTER")
print("="*70)

# Create client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\n❌ GEMINI_API_KEY not found!")
    exit(1)

client = genai.Client(api_key=api_key)

print("\n⏳ Discovering available models...")

try:
    # Models to test (in order of preference)
    # Just test the main ones we know work
    available_test_models = [
        "gemini-2.5-flash",
        "gemini-2.5-pro", 
        "gemini-2.0-flash-exp",
    ]
    
    print(f"✅ Testing {len(available_test_models)} Gemini models\n")
    
    print("="*70)
    print("  🧪 TESTING MODELS")
    print("="*70)
    
    # Test prompt
    test_prompt = "Say 'What's up Tony! I'm ready to help!' in a friendly way"
    
    print(f"\n📝 Test prompt: {test_prompt}\n")
    
    results = []
    
    for i, model_name in enumerate(available_test_models, 1):
        print(f"[{i}/{len(available_test_models)}] Testing: {model_name}")
        print("─"*70)
        
        try:
            start_time = time.time()
            
            response = client.models.generate_content(
                model=model_name,
                contents=test_prompt
            )
            
            elapsed = time.time() - start_time
            
            print(f"✅ Response ({elapsed:.2f}s):")
            print(f"   {response.text}\n")
            
            results.append({
                "model": model_name,
                "status": "✅ Success",
                "time": elapsed,
                "response": response.text[:100]
            })
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
            results.append({
                "model": model_name,
                "status": "❌ Failed",
                "time": 0,
                "response": str(e)[:100]
            })
    
    # Summary
    print("="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    
    print("\n🎯 Model Performance:\n")
    
    for result in results:
        status_icon = "✅" if "Success" in result["status"] else "❌"
        time_str = f"{result['time']:.2f}s" if result['time'] > 0 else "N/A"
        print(f"   {status_icon} {result['model']:<25} {time_str:>8}")
    
    successful = sum(1 for r in results if "Success" in r["status"])
    
    print(f"\n📈 Success rate: {successful}/{len(results)} ({(successful/len(results)*100):.0f}%)")
    
    if successful > 0:
        avg_time = sum(r['time'] for r in results if r['time'] > 0) / successful
        print(f"⚡ Average response time: {avg_time:.2f}s")
        
        fastest = min([r for r in results if r['time'] > 0], key=lambda x: x['time'])
        print(f"🏆 Fastest model: {fastest['model']} ({fastest['time']:.2f}s)")
    
    print("\n💡 Recommended models for your use case:")
    print("   • Speed: gemini-2.5-flash (fast queries)")
    print("   • Quality: gemini-2.5-pro (complex analysis)")
    print("   • Balance: gemini-2.0-flash-exp (good middle ground)")
    
    print("\n" + "="*70)
    print("  ✅ MODEL TESTING COMPLETE!")
    print("="*70)
    
    print("\n🎉 All systems go! Ready to build your chatbot!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check API key is valid")
    print("2. Verify internet connection")
    print("3. Update SDK: poetry add google-genai")
    exit(1)