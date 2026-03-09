namespace MAPEngine;

class Tokenizer (Evaluator eval, string text) {
   readonly Evaluator mEval = eval;  // The evaluator that owns this
   readonly string mText = text;     // The input text we're parsing through
   int mN = 0;                    // Position within the text

   public Token Next () {
      while (mN < mText.Length) {
         char ch = char.ToLower (mText[mN++]);
         switch (ch) {
            case ' ' or '\t': continue;
            case (>= '0' and <= '9') or '.': return GetNumber ();
            case '(' or ')': return new TPunctuation (ch);
            case '<' or '>' or '=': return GetOperator ();
            case >= 'a' and <= 'z': return GetIdentifier ();
            default: return new TError ($"Unknown symbol: {ch}");
         }
      }
      return new TEnd ();
   }

   Token GetOperator () {
      int start = mN - 1;
      while (mN < mText.Length) {
         char ch = char.ToLower (mText[mN++]);
         if (ch is '>' or '=' or '<') continue;
         mN--; break;
      }
      string sub = mText[start..mN];
      if (mOps.Contains (sub)) return new TOperator (mEval, sub);
      else return new TError ($"Unknown operator: {sub}");
   }
   readonly string[] mOps = { "=", "<", ">", "<=", ">=", "=<", "=>" };


   // returns actuator/sensor name OR one of the literal tokens
   Token GetIdentifier () {
      int start = mN - 1;
      while (mN < mText.Length) {
         char ch = char.ToLower (mText[mN++]);
         if (ch is '_' or (>= 'a' and <= 'z')) continue;
         mN--; break;
      }
      string sub = mText[start..mN];
      if (mFuncs.Contains (sub))
         return (sub.ToLower ()) switch {
            "if" => new TIf (sub),
            "then" => new TThen (sub),
            _ => TLiteral (sub)
         };
      else return new TVariable (sub);
   }
   readonly string[] mFuncs = { "IF", "THEN", "SET", "ON", "OFF", "TO" };

   Token GetNumber () {
      int start = mN - 1;
      while (mN < mText.Length) {
         char ch = mText[mN++];
         if (ch is (>= '0' and <= '9') or '.') continue;
         mN--; break;
      }
      // Now, mN points to the first character of mText that is not part of the number
      string sub = mText[start..mN];
      if (double.TryParse (sub, out double f)) return new TNumber (f);
      return new TError ($"Invalid number: {sub}");
   }
}
