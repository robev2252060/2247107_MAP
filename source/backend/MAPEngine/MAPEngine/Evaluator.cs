namespace MAPEngine;

class EvalException : Exception {
   public EvalException (string message) : base (message) { }
}

record Rule (string SensorName, TOperator Op, double Threshold, string ActuatorName, string ActuatorState);

class Evaluator {
   // Parses and storse a rule string like:
   // "IF greenhouse_temperature > 28 THEN set cooling_fan to ON"
   public void LoadRule (string text) {
      List<Token> tokens = [];
      var tokenizer = new Tokenizer (this, text);
      for (; ; ) {
         Token token = tokenizer.Next ();
         if (token is TEnd) break;
         if (token is TError err) throw new EvalException (err.Message);
         tokens.Add (token);
      }

      // Expected sequence:
      // [0] IF  (TLiteral)
      // [1] <sensor_name>  (TSensor)
      // [2] <operator>     (TOperator)
      // [3] <threshold>    (TNumber)
      // [4] THEN           (TLiteral)
      // [5] SET            (TLiteral)
      // [6] <actuator>     (TActuator)
      // [7] TO             (TLiteral)
      // [8] ON | OFF       (TLiteral)

      if (tokens.Count < 9)
         throw new EvalException ("Incomplete rule: expected IF <sensor> <op> <value> THEN SET <actuator> TO ON|OFF");

      if (tokens[0] is not TLiteral { Name: "IF" })
         throw new EvalException ("Rule must start with IF");
      if (tokens[4] is not TLiteral { Name: "THEN" })
         throw new EvalException ("Expected THEN after condition");
      if (tokens[5] is not TLiteral { Name: "SET" })
         throw new EvalException ("Expected SET after THEN");
      if (tokens[7] is not TLiteral { Name: "TO" })
         throw new EvalException ("Expected TO after actuator name");

      if (tokens[1] is not TSensor sensor)
         throw new EvalException ("Expected sensor name after IF");
      if (tokens[2] is not TOperator op)
         throw new EvalException ("Expected operator after sensor name");
      if (tokens[3] is not TNumber threshold)
         throw new EvalException ("Expected numeric threshold after operator");
      if (tokens[6] is not TActuator actuator)
         throw new EvalException ("Expected actuator name after SET");
      if (tokens[8] is not TLiteral stateToken || stateToken.Name is not ("ON" or "OFF"))
         throw new EvalException ("Expected ON or OFF after TO");

      mRules.Add (new Rule (sensor.Name, op, threshold.Value, actuator.Name, stateToken.Name));
   }

   // Called by RuleEvaluatorService whenever a sensor value is updated.
   // Returns all actuator commands triggered by rules on that sensor.
   public IEnumerable<ActuatorCommand> EvaluateRules (string changedSensor) {
      var commands = new List<ActuatorCommand> ();

      foreach (var rule in mRules) {
         // Only evaluate rules that watch the sensor that just changed
         if (rule.SensorName != changedSensor) continue;

         if (!mVars.TryGetValue (rule.SensorName, out double currentValue)) continue;

         if (rule.Op.Evaluate (currentValue, rule.Threshold))
            commands.Add (new ActuatorCommand (rule.ActuatorName, rule.ActuatorState));
      }

      return commands;
   }

   public void SetVariable (string sensorName, double value) =>
       mVars[sensorName] = value;

   public double GetVariable (string name) {
      if (mVars.TryGetValue (name, out double value)) return value;
      throw new EvalException ($"Unknown variable: {name}");
   }

   // For loading persisted rules on startup
   public void LoadRules (IEnumerable<string> ruleTexts) {
      foreach (var text in ruleTexts)
         LoadRule (text);
   }

   public void ClearRules () => mRules.Clear ();

   readonly Dictionary<string, double> mVars = new ();
   readonly List<Rule> mRules = [];
}