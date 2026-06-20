function SuggestedQuestions({ suggestions, onSelect, disabled }) {
  if (!suggestions?.length) return null;

  return (
    <div className="cb-suggestions" aria-label="Suggested follow-up questions">
      <span className="cb-suggestions-label">Suggested</span>
      <div className="cb-suggestions-chips">
        {suggestions.slice(0, 3).map((q, i) => (
          <button
            key={`${i}-${q}`}
            type="button"
            className="cb-chip"
            onClick={() => !disabled && onSelect(q)}
            disabled={disabled}
            aria-label={`Ask: ${q}`}
          >
            <span className="cb-chip-icon" aria-hidden="true">↗</span>
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

export default SuggestedQuestions;