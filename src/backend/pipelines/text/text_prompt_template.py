from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def build_text_evaluation_prompt(transcript: str, max_chars: int = 20000) -> str:
    
    if not transcript:
        logger.warning("Empty transcript provided to prompt builder")
        transcript = "[No transcript available]"
        
    if len(transcript) > max_chars:
        logger.info(f"Truncating transcript from {len(transcript)} to {max_chars} chars")
        transcript = transcript[:max_chars] + "... [TRUNCATED]"

    prompt = f
    return prompt
