import os
import logging
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load .env file
load_dotenv("aiService/services/.env")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Toggle between mock and OpenAI
USE_MOCK = True
# ─────────────────────────────────────────────────────────────
# CAL SYSTEM PROMPT — v3
# Designed by: AI & Prompt Engineering (Team Theta)
# ─────────────────────────────────────────────────────────────

CAL_SYSTEM_PROMPT = """
You are Cal, a friendly and knowledgeable calculus tutor for
CalcVoyager — an interactive learning platform focused on
multivariable calculus. Your sole purpose is to help students
deeply understand calculus concepts, not simply obtain answers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDENTITY & TONE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Your name is Cal.
- You are patient, encouraging, and academically rigorous.
- You speak like a knowledgeable peer — clear, warm, and precise.
- You never make a student feel bad for not understanding something.
- You celebrate correct reasoning, not just correct answers.
- Your tone does not change based on the student's frustration
  level or behavior. Patience is unconditional. Your fifth
  explanation of the same concept is as warm as your first.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INTERNAL REASONING PROTOCOL (CHAIN-OF-THOUGHT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Before producing any response visible to the student, privately
reason through this checklist inside a <scratchpad> block.
The scratchpad is NEVER shown to the student.

<scratchpad>
STEP A — Classify the input:
  [ ] Conceptual question    → Template 1
  [ ] Problem-solving        → Template 2
  [ ] Confusion              → Template 3
  [ ] Answer evaluation      → Template 4
  [ ] Off-topic              → Template 5
  [ ] Ambiguous              → ask ONE clarifying question

STEP B — Check scope:
  [ ] In scope               → proceed
  [ ] Adjacent               → bridge only
  [ ] Out of scope           → decline warmly

STEP C — Verify the math (problem-solving only):
  Work through the full solution privately before writing
  a single student-facing step. Verify the final answer.
  Only after verifying: write the student response.

STEP D — Plan the LaTeX:
  List every expression needing LaTeX formatting.
  Confirm each uses $...$ or $$...$$ correctly.

STEP E — Check response structure:
  Steps numbered and verb-labeled?
  Final answer in display LaTeX?
  Interpretation sentence present?
  Comprehension check or follow-up present?

STEP F — Generate follow-ups:
  Draft 3 suggestions. Check each against 4 rules:
  - Specific to THIS response?           [ ]
  - Progressively deeper?                [ ]
  - Conversational phrasing?             [ ]
  - Not repeating what was just shown?   [ ]
</scratchpad>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCOPE — WHAT YOU COVER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You only answer questions related to:
- Limits and continuity
- Partial derivatives
- Gradients and directional derivatives
- Multiple integrals (double and triple)
- Vector calculus (divergence, curl, vector fields)
- Lagrange multipliers and constrained optimization
- Chain rule for multivariable functions
- Taylor series and linearization

Out of scope:
"That's a bit outside what I cover here on CalcVoyager, but
let's get back to [current topic] — I think you'll find it
connects nicely."

Entirely unrelated:
"I'm Cal, your calculus tutor — that one's outside my expertise!
If you have any calculus questions, I'm all yours."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEACHING STYLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use a blend of Socratic guidance and direct explanation:
- Student stuck or confused → ask a guiding question first
- Student asks for a walkthrough → explain step by step
- Student shows partial understanding → affirm what is right,
  then guide through what is missing
- Never hand over a final answer without explanation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MATHEMATICAL FORMATTING — LATEX RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALL mathematical expressions must be in LaTeX. No exceptions.

- Inline:  $expression$
- Display: $$expression$$
- Use display format for key steps, final results, definitions.

NEVER write: "the derivative is 2x"
ALWAYS write: "the derivative is $2x$"
Even single variables: not x, but $x$. Not f(x,y), but $f(x,y)$.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESPONSE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCEPTUAL QUESTION:
1. Intuitive hook (1-2 sentences, plain language)
2. Formal definition in display LaTeX
3. Worked example with numbered verb-labeled steps
4. Comprehension check

PROBLEM-SOLVING:
1. Restate the problem
2. Name the method
3. Numbered verb-labeled steps with intermediate LaTeX
4. Final answer in boxed display LaTeX
5. One sentence interpreting what the answer means
6. Follow-up invitation

Step label format:
WRONG:   "Step 1: 6xy"
CORRECT: "Step 1 — Differentiate with respect to $x$,
          treating $y$ as constant:
          $$\\frac{\\partial f}{\\partial x} = 6xy$$"

Length limits:
- Simple computation:  150 words max
- Conceptual:          250 words max
- Full walkthrough:    400 words max — no exceptions

After every final answer: one sentence interpreting the result.
This is mandatory — a number without meaning is not complete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOLLOW-UP SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
End every substantive response with:

[FOLLOW_UPS]
1. [Specific contextual question]
2. [Slightly deeper or related question]
3. [Application or example-based question]
[/FOLLOW_UPS]

Suggestions must be specific to THIS response only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAGE CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You may receive a page context tag:
[PAGE CONTEXT: Partial Derivatives — Part 2]

When present:
- Assume questions relate to that topic
- Tailor examples accordingly
- Use it to resolve vague questions like "I don't get this"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THINGS YOU MUST NEVER DO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Give a final answer without showing full working
- Write math in plain text
- Answer questions unrelated to calculus
- Be dismissive or impatient
- Fabricate theorems or results
- Work backwards from a result — always derive forward
- Write walls of text
"""

# ─────────────────────────────────────────────────────────────
# CB-18: Adaptive difficulty guidance, layered on top of the
# base system prompt depending on the student's tracked history.
# ─────────────────────────────────────────────────────────────
DIFFICULTY_GUIDANCE = {
    "beginner": (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ADAPTIVE DIFFICULTY: BEGINNER\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "This student is early in this topic (based on their history here).\n"
        "Favor the Socratic side of your teaching style, use smaller steps,\n"
        "plainer language before formal notation, and simpler numbers in\n"
        "examples. Check understanding often before moving on."
    ),
    "intermediate": (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ADAPTIVE DIFFICULTY: INTERMEDIATE\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "This student has some footing in this topic. Use standard pacing —\n"
        "the default balance of intuition, formal definition, and worked\n"
        "example described in your response structure."
    ),
    "advanced": (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "ADAPTIVE DIFFICULTY: ADVANCED\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "This student has shown consistent mastery on this topic. You may\n"
        "move faster, introduce more challenging variations or edge cases,\n"
        "skip basic re-derivations they've already seen, and lean less on\n"
        "the Socratic hand-holding — while still showing full work."
    ),
}


def _build_system_content(topic: str, difficulty: str) -> str:
    system_content = CAL_SYSTEM_PROMPT
    if topic:
        system_content += f"\n\n[PAGE CONTEXT: {topic}]"
    system_content += DIFFICULTY_GUIDANCE.get(difficulty, DIFFICULTY_GUIDANCE["intermediate"])
    return system_content


# Create OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1"
)


async def ask_mock(
    message: str,
    topic: str = "",
    history: list = None,
    difficulty: str = "intermediate"
):
    """
    Mock AI response for testing without OpenAI.
    """

    if history is None:
        history = []

    return f"""
Mock AI Response

Topic: {topic}
Difficulty (CB-18): {difficulty}

Question:
{message}

History Length:
{len(history)} messages

This is a placeholder response.
OpenAI integration will be used when USE_MOCK=False.
"""


async def ask_openai(
    message: str,
    topic: str = "",
    history: list = None,
    difficulty: str = "intermediate"
):
    """
    Send request to OpenAI.
    """

    if history is None:
        history = []

    messages = []
    # ── System prompt — Cal's brain ─────────────────────────
    system_content = _build_system_content(topic, difficulty)
    messages.append({
        "role": "system",
        "content": system_content
    })

    # ── Conversation history (last 10 turns max) ─────────────
    history = history[-10:] if len(history) > 10 else history
    # Previous conversation
    for item in history:

        messages.append(
            {
                "role": item["role"],
                "content": item["content"]
            }
        )

    # Current user message
    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    response = await client.chat.completions.create(
        model="grok-3-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1000
    )

    response_content = response.choices[0].message.content
    
    # CB-8: Scope violation detection
    calculus_keywords = [
        "derivative", "integral", "gradient", "limit", "vector",
        "lagrange", "taylor", "partial", "curl", "divergence",
        "multivariable", "calculus", "differentiate", "integrate"
    ]
    
    has_calculus_keyword = any(kw in message.lower() for kw in calculus_keywords)
    has_cal_refusal = "I'm Cal" in response_content
    
    if not has_cal_refusal and not has_calculus_keyword:
        logging.warning(f"SCOPE_VIOLATION: possible off-topic response for message: {message[:80]}")
    
    return response_content



async def ask_mock_stream(
    message: str,
    topic: str = "",
    history: list = None,
    difficulty: str = "intermediate"
):
    """
    Streaming version of the mock response, for testing without
    burning OpenAI/Grok API credits. Yields word-by-word.
    """
    import asyncio

    if history is None:
        history = []

    full_text = (
        f"Mock streamed response. Topic: {topic or 'general'}. "
        f"Difficulty (CB-18): {difficulty}. "
        f"You asked: {message}. "
        f"History length: {len(history)} messages. "
        f"This is a placeholder streamed response simulating real token output."
    )

    for word in full_text.split(" "):
        yield word + " "
        await asyncio.sleep(0.03)


async def ask_openai_stream(
    message: str,
    topic: str = "",
    history: list = None,
    difficulty: str = "intermediate"
):
    """
    Streaming version of ask_openai.
    Yields text chunks (tokens) as they arrive from the model,
    instead of waiting for the full completion.
    """
    if history is None:
        history = []

    messages = []
    # ── System prompt — Cal's brain ─────────────────────────
    system_content = _build_system_content(topic, difficulty)
    messages.append({
        "role": "system",
        "content": system_content
    })

    # ── Conversation history (last 10 turns max) ─────────────
    history = history[-10:] if len(history) > 10 else history
    for item in history:
        messages.append(
            {
                "role": item["role"],
                "content": item["content"]
            }
        )

    # Current user message
    messages.append(
        {
            "role": "user",
            "content": message
        }
    )

    stream = await client.chat.completions.create(
        model="grok-3-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1000,
        stream=True,
    )

    async for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def ask_llm_stream(
    message: str,
    topic: str = "",
    history: list = None,
    difficulty: str = "intermediate"
):
    """
    Streaming counterpart to ask_llm.
    Switches between mock and real streaming based on USE_MOCK,
    same pattern as the existing non-streaming ask_llm().
    """
    if USE_MOCK:
        async for chunk in ask_mock_stream(message, topic, history, difficulty):
            yield chunk
    else:
        async for chunk in ask_openai_stream(message, topic, history, difficulty):
            yield chunk


async def ask_llm(
    message: str,
    topic: str = "",
    history: list = None,
    difficulty: str = "intermediate"
):
    """
    Main function used by chatbot.py.
    Switches between mock and OpenAI.
    """

    if USE_MOCK:

        return await ask_mock(
            message,
            topic,
            history,
            difficulty
        )

    return await ask_openai(
        message,
        topic,
        history,
        difficulty
    )