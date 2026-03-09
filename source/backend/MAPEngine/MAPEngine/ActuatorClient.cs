namespace MAPEngine;

using MAPEngine.Model;
using System.Net.Http.Json;

class ActuatorClient {
   readonly HttpClient mHttp;

   public ActuatorClient (HttpClient http) => mHttp = http;

   public async Task SendCommandAsync (ActuatorCommand cmd) {
      var url = $"/api/actuators/{cmd.ActuatorName}";
      var response = await mHttp.PostAsJsonAsync (url, new { state = cmd.State });
      response.EnsureSuccessStatusCode ();
   }
}