namespace MAPEngine;

class Program {
   static void Main (string[] args) {
      var builder = WebApplication.CreateBuilder (args);

      builder.Services.AddControllers ();

      // Shared SSE broadcast channel
      builder.Services.AddSingleton<SseChannel> ();

      // Rule engine (singleton so Kafka consumer and HTTP share state)
      builder.Services.AddSingleton<RuleEvaluatorService> ();

      // Actuator REST client — base address from config
      builder.Services.AddHttpClient<ActuatorClient> (c => {
         c.BaseAddress = new Uri (builder.Configuration["ActuatorService:BaseUrl"]!);
      });

      // Kafka background consumer
      builder.Services.AddHostedService<SensorEventConsumer> ();

      var app = builder.Build ();
      app.MapControllers ();
      app.Run ();
   }
}