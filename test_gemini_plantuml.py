"""
Test script for Gemini API PlantUML generation
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from app.ml.uml.plantuml_generator import generate_plantuml


def _load_local_env() -> None:
    # Load root .env first
    root_env = Path(__file__).resolve().parent / ".env"
    if root_env.exists():
        load_dotenv(root_env, override=False)
    # Also check app/ml/uml/.env
    env_path = Path(__file__).resolve().parent / "app" / "ml" / "uml" / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


def test_gemini_plantuml():
    """Test the Gemini API PlantUML generation."""

    # Sample UML data for testing
    test_graph = {
        "actors": ["User", "Administrator"],
        "use_cases": ["Login", "View Reports", "Generate Report", "Manage Users"],
        "relationships": [
            {"actor": "User", "use_case": "Login"},
            {"actor": "User", "use_case": "View Reports"},
            {"actor": "Administrator", "use_case": "Generate Report"},
            {"actor": "Administrator", "use_case": "Manage Users"}
        ],
        "include_edges": [
            {"from_uc": "Generate Report", "to_uc": "View Reports"}
        ],
        "extend_edges": [
            {"from_uc": "Manage Users", "to_uc": "Login"}
        ]
    }

    print("Testing Gemini API PlantUML generation...")
    print("=" * 50)

    try:
        plantuml_code = generate_plantuml(test_graph)
        print("[OK] PlantUML code generated successfully!")
        print("\nGenerated PlantUML Code:")
        print("-" * 30)
        print(plantuml_code.encode('ascii', 'replace').decode('ascii'))
        print("-" * 30)

        # Save to file for testing
        with open('test_plantuml.puml', 'w', encoding='utf-8') as f:
            f.write(plantuml_code)
        print("[SAVED] Saved to test_plantuml.puml")

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        print("Make sure GEMINI_API_KEY environment variable is set.")

if __name__ == "__main__":
    # Load local .env if available
    _load_local_env()

    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("[WARNING] OPENROUTER_API_KEY environment variable not found!")
        print("")
        print("To set up OpenRouter API:")
        print("1. Get your free API key from: https://openrouter.ai/settings/keys")
        print("2. Add to your .env file: OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        print("")
        print("Then run this script again.")
        exit(1)

    test_gemini_plantuml()