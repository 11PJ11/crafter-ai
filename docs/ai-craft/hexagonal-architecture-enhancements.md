# Hexagonal Architecture & Environment Strategy Enhancements

## Enhanced Sub-Agents

### 1. Acceptance Designer Agent - Enhanced
**Key Additions:**
- **User Choice Consultation**: Mandatory question about local environment preference
- **Hexagonal Architecture Integration**: Tests through ports, not adapters
- **Vertical Slice Validation**: Complete business capability testing
- **Environment-Adaptive Strategy**: In-memory locally (~100ms) vs real components (~2-5s)
- **Integration Test Strategy**: Separate adapter testing requirements

### 2. Test-First Developer Agent - Enhanced  
**Key Additions:**
- **Hexagonal Architecture Patterns**: Clear ports/adapters separation with examples
- **Vertical Slices Development**: Business capability-focused implementation
- **Open Source Framework Requirements**: FREE testing frameworks only (NUnit, xUnit, NSubstitute)
- **Mocking Minimization**: Use real objects for internal collaborators
- **Environment Configuration**: User choice implementation patterns

### 3. Production Validator Agent - Enhanced
**Key Additions:**
- **Hexagonal Architecture Validation**: Verify ports/adapters separation
- **Vertical Slice Completeness**: Validate complete business capabilities
- **Environment Configuration Validation**: Ensure user choice respected
- **Adapter Business Logic Detection**: Prevent business logic in adapters
- **Integration Test Requirements**: Separate adapter test suite validation

## Architecture Strategy

### Hexagonal Architecture with Vertical Slices
```
┌─────────────────────────────────────────────────────────┐
│                    E2E Tests                            │
├─────────────────────────────────────────────────────────┤
│ Application Services (Use Cases) - Ports               │
├─────────────────────────────────────────────────────────┤
│ Domain Services (Business Logic)                       │
├─────────────────────────────────────────────────────────┤
│ Infrastructure (Adapters) + Integration Tests          │
└─────────────────────────────────────────────────────────┘
```

### Environment Strategy
- **Local Development**: User choice between in-memory (~100ms) or real components (~2-5s)
- **CI/CD Pipeline**: Always use production-like real components
- **Same Test Scenarios**: Single source of truth across all environments
- **Framework Requirements**: FREE open source only (NUnit, xUnit, NSubstitute, Testcontainers)

## Key Patterns Implemented

### 1. User Environment Choice Pattern
```csharp
public static class TestEnvironmentSetup
{
    public static async Task<bool> AskUserForLocalComponentChoice()
    {
        Console.WriteLine("For local development, would you prefer:");
        Console.WriteLine("1. In-Memory Components (fastest feedback, ~100ms)");
        Console.WriteLine("2. Real Components Locally (more realistic, ~2-5s)");
        Console.WriteLine("Note: CI/CD will always use production-like real components");
        
        var choice = Console.ReadLine();
        return choice == "2";
    }
}
```

### 2. Hexagonal Architecture Development Pattern
```csharp
// 1. Define Port (Business Interface) - Drive from E2E test needs
public interface IUserRepository
{
    Task<User> FindByUsernameAsync(string username);
    Task SaveAsync(User user);
}

// 2. Domain Service using Port - Unit Test Driven
public class UserService
{
    private readonly IUserRepository _repository;
    // Business logic here - no infrastructure concerns
}

// 3. Adapter (Infrastructure Implementation) - Integration Test Driven
public class DatabaseUserRepository : IUserRepository
{
    // Only data access translation - NO business logic
}
```

### 3. Environment-Adaptive Configuration
```csharp
public static IServiceCollection ConfigureServices(bool useRealComponentsLocally)
{
    var services = new ServiceCollection();
    
    // Always register business logic (same in all environments)
    services.AddScoped<IUserService, UserService>();
    
    if (IsCI() || useRealComponentsLocally)
    {
        // Real components (CI/CD always, local by user choice)
        services.AddScoped<IUserRepository, DatabaseUserRepository>();
    }
    else
    {
        // In-memory components (local development, user choice)
        services.AddSingleton<IUserRepository, InMemoryUserRepository>();
    }
    
    return services;
}
```

### 4. Free Framework Requirements
```csharp
// ✅ ALLOWED - Free Open Source
using NUnit.Framework;              // MIT License
using NSubstitute;                 // BSD License
using Testcontainers;              // MIT License

// ❌ FORBIDDEN - Paid/Commercial
// using FluentAssertions; // Paid license for commercial use
// using JustMock; // Commercial license required
```

## Integration with Pipeline

### Enhanced Validation Checklist
- **Hexagonal Architecture Compliance**: Clear ports/adapters separation
- **Vertical Slice Completeness**: Complete business capabilities implemented
- **Environment Configuration**: User choice respected locally, real components in CI/CD
- **Free Framework Usage**: No paid/commercial testing frameworks
- **Minimal Mocking**: Real objects for internal collaborators
- **Adapter Integration Tests**: Separate test suite for infrastructure validation

### Quality Gates Enhancement
The production-validator and quality-gates agents now validate:
- Proper hexagonal architecture implementation
- Vertical slice completeness
- Environment configuration compliance
- Free framework usage
- Minimal mocking practices
- Adapter business logic prevention

This ensures the pipeline maintains architectural integrity while providing flexible development environment choices and cost-effective tooling.