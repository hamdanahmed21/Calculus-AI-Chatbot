export const SYMBOL_GROUPS = [
    {
      label: "Calculus",
      symbols: [
        { label: "∂", insert: "\\partial ", title: "Partial derivative" },
        { label: "∫", insert: "\\int ", title: "Integral" },
        { label: "∬", insert: "\\iint ", title: "Double integral" },
        { label: "∭", insert: "\\iiint ", title: "Triple integral" },
        { label: "∮", insert: "\\oint ", title: "Contour integral" },
        { label: "∇", insert: "\\nabla ", title: "Gradient / nabla" },
        { label: "lim", insert: "\\lim_{x \\to a} ", title: "Limit" },
        { label: "∞", insert: "\\infty", title: "Infinity" },
        { label: "d/dx", insert: "\\frac{d}{dx}", title: "Derivative" },
        { label: "∂f/∂x", insert: "\\frac{\\partial f}{\\partial x}", title: "Partial ∂f/∂x" },
        { label: "∑", insert: "\\sum_{i=1}^{n} ", title: "Summation" },
        { label: "∏", insert: "\\prod_{i=1}^{n} ", title: "Product" },
      ],
    },
    {
      label: "Vectors",
      symbols: [
        { label: "⟨⟩", insert: "\\langle x, y \\rangle", title: "Vector" },
        { label: "→v", insert: "\\vec{v}", title: "Vector v" },
        { label: "‖v‖", insert: "\\|\\vec{v}\\|", title: "Magnitude" },
        { label: "·", insert: "\\cdot", title: "Dot product" },
        { label: "×", insert: "\\times", title: "Cross product" },
        { label: "î", insert: "\\hat{i}", title: "Unit i" },
        { label: "ĵ", insert: "\\hat{j}", title: "Unit j" },
        { label: "k̂", insert: "\\hat{k}", title: "Unit k" },
      ],
    },
    {
      label: "Greek",
      symbols: [
        { label: "α", insert: "\\alpha", title: "Alpha" },
        { label: "β", insert: "\\beta", title: "Beta" },
        { label: "γ", insert: "\\gamma", title: "Gamma" },
        { label: "δ", insert: "\\delta", title: "Delta" },
        { label: "ε", insert: "\\epsilon", title: "Epsilon" },
        { label: "λ", insert: "\\lambda", title: "Lambda" },
        { label: "μ", insert: "\\mu", title: "Mu" },
        { label: "π", insert: "\\pi", title: "Pi" },
        { label: "θ", insert: "\\theta", title: "Theta" },
        { label: "φ", insert: "\\phi", title: "Phi" },
        { label: "ρ", insert: "\\rho", title: "Rho" },
        { label: "σ", insert: "\\sigma", title: "Sigma" },
      ],
    },
    {
      label: "Structures",
      symbols: [
        { label: "a/b", insert: "\\frac{a}{b}", title: "Fraction" },
        { label: "√", insert: "\\sqrt{x}", title: "Square root" },
        { label: "ⁿ√", insert: "\\sqrt[n]{x}", title: "nth root" },
        { label: "x²", insert: "x^{2}", title: "Squared" },
        { label: "xⁿ", insert: "x^{n}", title: "Power" },
        { label: "xₙ", insert: "x_{n}", title: "Subscript" },
        { label: "[ ]", insert: "\\left[ x \\right]", title: "Brackets" },
        { label: "( )", insert: "\\left( x \\right)", title: "Parentheses" },
      ],
    },
  ];
  
  function MathSymbolPicker({ activeGroup, onGroupChange, onInsert }) {
    return (
      <div className="cb-symbols-palette">
        <div className="cb-sym-groups">
          {SYMBOL_GROUPS.map((g, i) => (
            <button
              key={g.label}
              type="button"
              className={`cb-sym-group-btn${activeGroup === i ? " active" : ""}`}
              onClick={() => onGroupChange(i)}
            >
              {g.label}
            </button>
          ))}
        </div>
        <div className="cb-sym-grid">
          {SYMBOL_GROUPS[activeGroup].symbols.map((s) => (
            <button
              key={s.label + s.insert}
              type="button"
              className="cb-sym-btn"
              onClick={() => onInsert(s.insert)}
              title={s.title}
              aria-label={s.title}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>
    );
  }
  
  export default MathSymbolPicker;