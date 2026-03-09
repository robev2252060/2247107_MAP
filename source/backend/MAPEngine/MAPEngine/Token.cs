namespace MAPEngine;

abstract class Token {
}

class TNumber (double value) : Token {
   public double Value { get; } = value;
}

// IF/THEN, SET, TO, ON/OFF
class TLiteral (string name) : Token {
   public string Name { get; private set; } = name;
   public override string ToString () => $"var:{Name}";
}

class TIf (string name) : TLiteral {
   public string Name { get; private set; } = name;
   public Predicate<TOperator>? Pred = null;
   public override string ToString () => $"var:{Name}";
}

class TThen (string name) : TLiteral {
   public string Name { get; private set; } = name;
   public Action Action = null;
   public override string ToString () => $"var:{Name}";
}

class TVariable (string name) : Token { }

class TSensor (string name) : TVariable {
   public string Name { get; private set; } = name;
   public override string ToString () => $"var:{Name}";
}

class TActuator (string name) : TVariable {
   public string Name { get; private set; } = name;
   public override string ToString () => $"var:{Name}";
}

class TOperator (Evaluator eval, string op) : Token {
   public string Op { get; private set; } = op;
   public override string ToString () => $"op:{Op}:{Priority}";
   public int Priority => sPriority[Op] + mEval.BasePriority;

   public bool Evaluate (double a, double b) {
      return Op switch {
         "<" => a - b < mEpsilon,
         "<=" => a - b <= mEpsilon,
         "=" => a - b == mEpsilon,
         ">" => a - b > mEpsilon,
         ">=" => a - b >= mEpsilon,
         _ => throw new EvalException ($"Unknown operator: {Op}"),
      };
   }

   readonly double mEpsilon = 10e-6;
   static readonly Dictionary<string, int> sPriority = new () {
      ["<"] = 1, ["<="] = 2, ["=<"] = 2, ["="] = 3, [">="] = 2, ["=>"] = 2, [">"] = 1,
   };
   readonly Evaluator mEval = eval;
}

class TPunctuation (char ch) : Token {
   public char Punct { get; private set; } = ch;
   public override string ToString () => $"punct:{Punct}";
}

class TEnd : Token {
   public override string ToString () => "end";
}

class TError : Token {
   public TError (string message) => Message = message;
   public string Message { get; private set; }
   public override string ToString () => $"error:{Message}";
}