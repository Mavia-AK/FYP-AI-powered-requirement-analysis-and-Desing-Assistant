from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path('app/ml/uml/.env').resolve()
print('exists', env_path.exists(), env_path)
print('content', env_path.read_text().strip() if env_path.exists() else '<missing>')
load_dotenv(env_path, override=False)
print('env', os.getenv('GEMINI_API_KEY'))
