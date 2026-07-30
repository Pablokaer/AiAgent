namespace AIFinperiti.Api.Services;

/// <summary>Default <see cref="IHealthService"/> implementation.</summary>
public sealed class HealthService : IHealthService
{
    /// <inheritdoc />
    public string Status() => "OK";
}
