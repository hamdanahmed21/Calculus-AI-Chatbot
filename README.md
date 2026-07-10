## 📌 Summary
This PR implements CB-16 (Symbolic Math Verification) and CB-17 (Practice Mode) for the Cal chatbot.

## 🧠 CB-16: Symbolic Math Verifier
- Added `/services/math_verifier.py` using **SymPy**.
- Automatically extracts Cal's `\boxed{}` answer and compares it to SymPy's independent solution.
- Logs `WRONG_ANSWER` warnings for incorrect answers.
- Gracefully falls back to the old answer-key method for unparseable problems.

## 🎓 CB-17: Practice Mode
- Added `/chat/practice/generate` endpoint to create a problem + hidden solution using LLM (mock).
- Added `/chat/practice/attempt` endpoint to verify student answers using CB-16 verifier.
- Added CLI practice tool (`practice_cli.py`) for interactive testing.
- Practice attempts tracked in database (`practice_attempts` table).

## 📂 Files Changed
- Added: `services/math_verifier.py`
- Added: `routes/practice.py`
- Added: `routes/chat.py` (hooked verifier)
- Added: `models.py` (PracticeAttempt table)
- Added: `practice_cli.py` (CLI testing)

## ✅ Closes
Closes CB-16 and CB-17