using AIFinperiti.Api.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<IHealthService, HealthService>();

var app = builder.Build();

app.MapGet("/health", (IHealthService health) => Results.Ok(health.Status()));

app.Run();

/// <summary>Exposes the entry point to the test host.</summary>
public partial class Program { }
