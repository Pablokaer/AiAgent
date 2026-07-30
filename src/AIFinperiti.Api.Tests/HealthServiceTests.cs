using AIFinperiti.Api.Services;
using Xunit;

namespace AIFinperiti.Api.Tests;

public class HealthServiceTests
{
    [Fact]
    public void Status_ReturnsOk()
    {
        var sut = new HealthService();

        Assert.Equal("OK", sut.Status());
    }
}
