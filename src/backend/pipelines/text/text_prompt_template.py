from src.backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def build_text_evaluation_prompt(transcript: str, max_chars: int = 20000) -> str:
    
    if not transcript:
        logger.warning("Empty transcript provided to prompt builder")
        transcript = "[No transcript available]"
        
    if len(transcript) > max_chars:
        logger.info(f"Truncating transcript from {len(transcript)} to {max_chars} chars")
        transcript = transcript[:max_chars] + "... [TRUNCATED]"

    prompt = f"""You are an expert educational content evaluator. Analyze the following teaching transcript and provide scores and feedback.

IMPORTANT: This transcript is from an Indian educational video and will be in HINDI or ENGLISH (or a mix of both - "Hinglish"). The teacher may be teaching mathematics, science, or other subjects. Evaluate the teaching quality based on the content, regardless of the language used.

TRANSCRIPT:
---
{transcript}
---

Evaluate the teaching quality and return ONLY a valid JSON object (no markdown, no explanation) with these exact keys:

{{
    "clarity_score": <float 0-10>,
    "structure_score": <float 0-10>,
    "technical_correctness_score": <float 0-10>,
    "explanation_quality_score": <float 0-10>,
    "summary": "<2-3 sentence summary of teaching quality in English>"
}}

SCORING GUIDELINES:
- clarity_score: How clear and understandable is the explanation?
- structure_score: Is content well-organized with logical flow?
- technical_correctness_score: Is the information accurate?
- explanation_quality_score: Are concepts explained effectively?

If the transcript is very short, has unclear content, or is in a language you can understand, still provide your best assessment.
If you cannot evaluate at all, return scores of 5.0 (neutral) with an appropriate summary.

Return ONLY the JSON object, nothing else."""

    return prompt

