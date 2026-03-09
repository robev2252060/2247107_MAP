using MAPEngine.Http;
using MAPEngine.Model;
using System.Text.Json;

namespace MAPEngine;

class RuleEvaluatorService {
   readonly ActuatorClient mActuator;
   readonly SseChannel mSse;
   readonly ILogger<RuleEvaluatorService> mLog;
   readonly Evaluator mEval;

   public RuleEvaluatorService (ActuatorClient actuator,
                                SseChannel sse,
                                ILogger<RuleEvaluatorService> log) {
      mActuator = actuator;
      mSse = sse;
      mLog = log;
      mEval = new Evaluator ();
   }

   public void OnSensorEvent (SensorEvent ev) {
      // 1. Update in-memory state so your Evaluator can read it
      mEval.SetVariable (ev.SensorName, ev.Value);

      // 2. Evaluate all loaded rules — returns actuator commands
      var triggered = mEval.EvaluateRules (ev.SensorName);

      foreach (var cmd in triggered) {
         // 3. Call actuator microservice via REST
         _ = mActuator.SendCommandAsync (cmd)
             .ContinueWith (t => mLog.LogError (t.Exception, "Actuator call failed"),
                           TaskContinuationOptions.OnlyOnFaulted);

         // 4. Broadcast to SSE subscribers (dashboard, other services)
         var json = JsonSerializer.Serialize (cmd);
         mSse.Writer.TryWrite (json);
      }
   }
}