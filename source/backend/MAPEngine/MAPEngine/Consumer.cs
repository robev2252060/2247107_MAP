using Confluent.Kafka;
using MAPEngine.Model;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;
using System.Threading.Channels;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;
using System.Threading.Channels;

namespace MAPEngine;

class SensorEventConsumer : BackgroundService {
   readonly IConsumer<string, string> mConsumer;
   readonly RuleEvaluatorService mEngine;
   readonly ILogger<SensorEventConsumer> mLog;

   public SensorEventConsumer (IConfiguration cfg,
                               RuleEvaluatorService engine,
                               ILogger<SensorEventConsumer> log) {
      mEngine = engine;
      mLog = log;
      var config = new ConsumerConfig {
         BootstrapServers = cfg["Kafka:BootstrapServers"],
         GroupId = cfg["Kafka:GroupId"] ?? "map-engine",
         AutoOffsetReset = AutoOffsetReset.Latest,
      };
      mConsumer = new ConsumerBuilder<string, string> (config).Build ();
   }

   protected override async Task ExecuteAsync (CancellationToken ct) {
      mConsumer.Subscribe ("sensor.events");   // topic from your ingestion service
      await Task.Run (() => {
         while (!ct.IsCancellationRequested) {
            var result = mConsumer.Consume (ct);
            try {
               var ev = JsonSerializer.Deserialize<SensorEvent> (result.Message.Value);
               if (ev is not null)
                  mEngine.OnSensorEvent (ev);
            } catch (Exception ex) {
               mLog.LogError (ex, "Failed to process Kafka message");
            }
         }
      }, ct);
   }

   public override void Dispose () { mConsumer.Close (); base.Dispose (); }
}

// Singleton channel — engine writes, SSE controller reads
class SseChannel {
   readonly Channel<string> mCh = Channel.CreateUnbounded<string> ();
   public ChannelWriter<string> Writer => mCh.Writer;
   public ChannelReader<string> Reader => mCh.Reader;
}

[ApiController]
[Route ("api/events")]
class SseController : ControllerBase {
   readonly SseChannel mChannel;
   public SseController (SseChannel ch) => mChannel = ch;

   [HttpGet ("stream")]
   public async Task Stream (CancellationToken ct) {
      Response.Headers.Append ("Content-Type", "text/event-stream");
      Response.Headers.Append ("Cache-Control", "no-cache");
      Response.Headers.Append ("X-Accel-Buffering", "no");

      await foreach (var msg in mChannel.Reader.ReadAllAsync (ct)) {
         await Response.WriteAsync ($"data: {msg}\n\n", ct);
         await Response.Body.FlushAsync (ct);
      }
   }
}