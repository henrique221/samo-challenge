#!/usr/bin/env python3
"""
Quick Test Script - Video Intelligence Prompt Solution
Demonstrates the one-shot prompt approach for video analysis

This script shows how a single prompt can transform an entire video
into structured, searchable knowledge.
"""

import json
import os
from video_analyzer import get_analyzer

def demonstrate_prompt_solution():
    """
    Demonstrates the core innovation: One-shot prompts that analyze
    entire videos in a single API call.
    """
    
    print("=" * 60)
    print("🎬 Video Intelligence: One-Shot Prompt Demonstration")
    print("=" * 60)
    
    # Initialize the analyzer
    analyzer = get_analyzer()
    
    # Check if we have a real API key
    if os.getenv('GEMINI_API_KEY'):
        print("✅ Using Google Gemini 1.5 Flash (Real Analysis)")
    else:
        print("ℹ️  Using Mock Analyzer (Set GEMINI_API_KEY for real analysis)")
    
    print("\n📝 THE ONE-SHOT PROMPTS:")
    print("-" * 40)
    
    # Display the actual prompts used
    for mode, config in analyzer.modes.items():
        if mode != 'custom':
            print(f"\n{config['emoji']} {mode.upper()} Mode:")
            print(f"Description: {config['description']}")
            if 'prompt' in config:
                prompt_preview = config['prompt'][:200] + "..." if len(config['prompt']) > 200 else config['prompt']
                print(f"Prompt: {prompt_preview}")
    
    print("\n" + "=" * 60)
    print("💡 THE MAGIC:")
    print("Each prompt above analyzes ENTIRE videos in ONE API call!")
    print("No loops, no frames extraction, just pure prompt engineering.")
    print("=" * 60)
    
    # Example analysis (using mock data if no API key)
    print("\n🔬 Example Analysis Output:")
    print("-" * 40)
    
    # Simulate or perform actual analysis
    if hasattr(analyzer, 'modes'):
        sample_result = {
            "status": "success",
            "analysis": {
                "summary": "This video demonstrates advanced concepts in machine learning...",
                "key_topics": ["Neural Networks", "Deep Learning", "Transformers"],
                "moments": [
                    {"time": "00:15", "description": "Introduction to ML concepts"},
                    {"time": "03:45", "description": "Deep dive into transformers"},
                    {"time": "07:20", "description": "Practical implementation"}
                ]
            }
        }
        
        print(json.dumps(sample_result, indent=2))
    
    print("\n✨ Transform any video into structured knowledge!")
    print("🚀 Run the web app to see it in action: python app.py")

if __name__ == "__main__":
    demonstrate_prompt_solution()