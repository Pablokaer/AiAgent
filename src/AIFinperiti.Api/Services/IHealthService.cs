namespace AIFinperiti.Api.Services;

/// <summary>Provides the current health status of the API.</summary>
public interface IHealthService
{
    /// <summary>Returns a short status string.</summary>
    string Status();
}
