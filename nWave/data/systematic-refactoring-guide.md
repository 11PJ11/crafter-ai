# Systematic Refactoring Guide - Six-Level Hierarchy Implementation

## Overview

This comprehensive guide implements the systematic six-level refactoring hierarchy for progressive code quality improvement, integrated with the nWave methodology and supporting multiple technology stacks.

### Refactoring Philosophy

**Core Principle**: "Simplicity first, maintainability always, performance when measured"

**Progressive Enhancement Approach**:

- **Bottom-Up Progression**: Start with foundational improvements before advanced patterns
- **Continuous Application**: Refactoring is part of every TDD cycle, not a separate phase
- **Evidence-Based Decisions**: All refactoring supported by measurable quality improvements
- **Domain-Driven Focus**: Preserve and enhance business language throughout technical implementation

## Six-Level Refactoring Hierarchy

### Level 1: 🟨 Refactor Readability (Foundation)

**Focus**: Tackle clutter, comments, dead code, implicit knowledge, scattering, bad naming

**When to Apply**: After every GREEN test in TDD cycle, during code review, before commit

**Core Techniques**:

#### Clean Comments

```csharp
// ❌ Before: How-comments that explain implementation
public async Task<User> GetUserAsync(int id)
{
    // Call the database to get user by ID
    var user = await _context.Users.FindAsync(id);
    // Check if user exists
    if (user == null)
    {
        // Throw exception if not found
        throw new UserNotFoundException($"User with ID {id} not found");
    }
    // Return the user
    return user;
}

// ✅ After: Method name reveals intent, no how-comments needed
public async Task<User> GetUserAsync(int id)
{
    var user = await _context.Users.FindAsync(id);
    if (user == null)
    {
        throw new UserNotFoundException($"User with ID {id} not found");
    }
    return user;
}
```

#### Dead Code Removal

```typescript
// ❌ Before: Unused imports, variables, and methods
import { useState, useEffect, useCallback, useMemo } from 'react'; // useMemo unused
import { UserService } from './services/UserService'; // UserService unused
import { debounce } from 'lodash'; // debounce unused

export const UserProfile: FC<Props> = ({ userId }) => {
  const [user, setUser] = useState<User>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>(); // error unused

  // Unused method
  const handleUnusedAction = useCallback(() => {
    console.log('This is never called');
  }, []);

  useEffect(() => {
    fetchUser();
  }, [userId]);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const userData = await fetch(`/api/users/${userId}`);
      setUser(await userData.json());
    } finally {
      setLoading(false);
    }
  };

  return loading ? <Spinner /> : <UserDetails user={user} />;
};

// ✅ After: Only used imports and variables
import { useState, useEffect } from 'react';

export const UserProfile: FC<Props> = ({ userId }) => {
  const [user, setUser] = useState<User>();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUser();
  }, [userId]);

  const fetchUser = async () => {
    setLoading(true);
    try {
      const userData = await fetch(`/api/users/${userId}`);
      setUser(await userData.json());
    } finally {
      setLoading(false);
    }
  };

  return loading ? <Spinner /> : <UserDetails user={user} />;
};
```

#### Magic Strings/Numbers Extraction

```python
# ❌ Before: Magic numbers and strings scattered throughout
def calculate_discount(customer_type, order_amount):
    if customer_type == "premium":
        if order_amount > 1000:
            return order_amount * 0.15
        else:
            return order_amount * 0.10
    elif customer_type == "regular":
        if order_amount > 500:
            return order_amount * 0.05
        else:
            return 0
    return 0

# ✅ After: Named constants reveal business intent
PREMIUM_CUSTOMER = "premium"
REGULAR_CUSTOMER = "regular"
HIGH_ORDER_THRESHOLD_PREMIUM = 1000
HIGH_ORDER_THRESHOLD_REGULAR = 500
PREMIUM_HIGH_DISCOUNT_RATE = 0.15
PREMIUM_LOW_DISCOUNT_RATE = 0.10
REGULAR_DISCOUNT_RATE = 0.05

def calculate_discount(customer_type, order_amount):
    if customer_type == PREMIUM_CUSTOMER:
        if order_amount > HIGH_ORDER_THRESHOLD_PREMIUM:
            return order_amount * PREMIUM_HIGH_DISCOUNT_RATE
        else:
            return order_amount * PREMIUM_LOW_DISCOUNT_RATE
    elif customer_type == REGULAR_CUSTOMER:
        if order_amount > HIGH_ORDER_THRESHOLD_REGULAR:
            return order_amount * REGULAR_DISCOUNT_RATE
        else:
            return 0
    return 0
```

#### Scope Optimization

```java
// ❌ Before: Variables with unnecessarily wide scope
public class OrderProcessor {
    private String tempProcessingResult; // Instance variable used only in one method
    private List<OrderItem> allItems; // Instance variable used only in processOrder

    public ProcessingResult processOrder(Order order) {
        allItems = order.getItems();
        tempProcessingResult = "";

        for (OrderItem item : allItems) {
            tempProcessingResult += validateItem(item);
        }

        return new ProcessingResult(tempProcessingResult);
    }

    private String validateItem(OrderItem item) {
        return item.isValid() ? "OK " : "ERROR ";
    }
}

// ✅ After: Variables scoped to minimum necessary
public class OrderProcessor {
    public ProcessingResult processOrder(Order order) {
        List<OrderItem> items = order.getItems();
        StringBuilder processingResult = new StringBuilder();

        for (OrderItem item : items) {
            processingResult.append(validateItem(item));
        }

        return new ProcessingResult(processingResult.toString());
    }

    private String validateItem(OrderItem item) {
        return item.isValid() ? "OK " : "ERROR ";
    }
}
```

### Level 2: 🟢 Reduce Complexity (Simplification)

**Focus**: Tackle complexity and duplication through method extraction and elimination

**When to Apply**: After every GREEN test, when cyclomatic complexity >10, during code review

#### Long Method Extraction

```csharp
// ❌ Before: Long method with multiple responsibilities
public async Task<OrderResult> ProcessOrderAsync(Order order)
{
    // Validation logic
    if (order == null) throw new ArgumentNullException(nameof(order));
    if (order.Items.Count == 0) throw new InvalidOperationException("Order must have items");
    foreach (var item in order.Items)
    {
        if (item.Quantity <= 0) throw new InvalidOperationException("Item quantity must be positive");
        if (string.IsNullOrEmpty(item.ProductId)) throw new InvalidOperationException("Item must have product ID");
    }

    // Inventory checking
    var unavailableItems = new List<string>();
    foreach (var item in order.Items)
    {
        var product = await _productRepository.GetByIdAsync(item.ProductId);
        if (product == null || product.StockQuantity < item.Quantity)
        {
            unavailableItems.Add(item.ProductId);
        }
    }
    if (unavailableItems.Count > 0)
    {
        return OrderResult.Failed($"Items not available: {string.Join(", ", unavailableItems)}");
    }

    // Price calculation
    decimal totalPrice = 0;
    foreach (var item in order.Items)
    {
        var product = await _productRepository.GetByIdAsync(item.ProductId);
        totalPrice += product.Price * item.Quantity;
    }

    // Apply discount
    if (order.Customer.Type == CustomerType.Premium && totalPrice > 1000)
    {
        totalPrice *= 0.9m; // 10% discount
    }

    // Payment processing
    var paymentResult = await _paymentService.ProcessPaymentAsync(order.Customer.PaymentInfo, totalPrice);
    if (!paymentResult.IsSuccess)
    {
        return OrderResult.Failed($"Payment failed: {paymentResult.ErrorMessage}");
    }

    // Save order
    order.TotalPrice = totalPrice;
    order.Status = OrderStatus.Confirmed;
    await _orderRepository.SaveAsync(order);

    return OrderResult.Success(order.Id);
}

// ✅ After: Extracted methods with business-meaningful names
public async Task<OrderResult> ProcessOrderAsync(Order order)
{
    ValidateOrder(order);

    var inventoryResult = await CheckInventoryAvailabilityAsync(order.Items);
    if (!inventoryResult.IsSuccess)
    {
        return OrderResult.Failed(inventoryResult.ErrorMessage);
    }

    var totalPrice = await CalculateOrderTotalAsync(order);
    totalPrice = ApplyDiscountIfEligible(order.Customer, totalPrice);

    var paymentResult = await ProcessPaymentAsync(order.Customer, totalPrice);
    if (!paymentResult.IsSuccess)
    {
        return OrderResult.Failed($"Payment failed: {paymentResult.ErrorMessage}");
    }

    await FinalizeOrderAsync(order, totalPrice);

    return OrderResult.Success(order.Id);
}

private void ValidateOrder(Order order)
{
    if (order == null) throw new ArgumentNullException(nameof(order));
    if (order.Items.Count == 0) throw new InvalidOperationException("Order must have items");

    foreach (var item in order.Items)
    {
        ValidateOrderItem(item);
    }
}

private void ValidateOrderItem(OrderItem item)
{
    if (item.Quantity <= 0)
        throw new InvalidOperationException("Item quantity must be positive");
    if (string.IsNullOrEmpty(item.ProductId))
        throw new InvalidOperationException("Item must have product ID");
}

private async Task<InventoryResult> CheckInventoryAvailabilityAsync(IEnumerable<OrderItem> items)
{
    var unavailableItems = new List<string>();

    foreach (var item in items)
    {
        if (!await IsItemAvailableAsync(item))
        {
            unavailableItems.Add(item.ProductId);
        }
    }

    return unavailableItems.Count > 0
        ? InventoryResult.Failed($"Items not available: {string.Join(", ", unavailableItems)}")
        : InventoryResult.Success();
}
```

#### Duplicated Code Elimination

```javascript
// ❌ Before: Duplicated validation logic
function validateUserRegistration(userData) {
  if (!userData.email || userData.email.trim() === "") {
    throw new Error("Email is required");
  }
  if (!/\S+@\S+\.\S+/.test(userData.email)) {
    throw new Error("Email format is invalid");
  }
  if (!userData.password || userData.password.length < 8) {
    throw new Error("Password must be at least 8 characters");
  }
  if (!/(?=.*[A-Z])(?=.*[a-z])(?=.*\d)/.test(userData.password)) {
    throw new Error("Password must contain uppercase, lowercase, and number");
  }
}

function validateUserProfileUpdate(userData) {
  if (!userData.email || userData.email.trim() === "") {
    throw new Error("Email is required");
  }
  if (!/\S+@\S+\.\S+/.test(userData.email)) {
    throw new Error("Email format is invalid");
  }
  // Different password rules for updates
  if (userData.password && userData.password.length < 6) {
    throw new Error("Password must be at least 6 characters");
  }
}

// ✅ After: Extracted common validation logic
function validateEmail(email) {
  if (!email || email.trim() === "") {
    throw new Error("Email is required");
  }
  if (!/\S+@\S+\.\S+/.test(email)) {
    throw new Error("Email format is invalid");
  }
}

function validateNewPassword(password) {
  if (!password || password.length < 8) {
    throw new Error("Password must be at least 8 characters");
  }
  if (!/(?=.*[A-Z])(?=.*[a-z])(?=.*\d)/.test(password)) {
    throw new Error("Password must contain uppercase, lowercase, and number");
  }
}

function validateUpdatePassword(password) {
  if (password && password.length < 6) {
    throw new Error("Password must be at least 6 characters");
  }
}

function validateUserRegistration(userData) {
  validateEmail(userData.email);
  validateNewPassword(userData.password);
}

function validateUserProfileUpdate(userData) {
  validateEmail(userData.email);
  validateUpdatePassword(userData.password);
}
```

### Level 3: 🟢 Reorder Responsibilities (Organization)

**Focus**: Tackle misplaced responsibilities and class organization

**When to Apply**: Sprint boundaries, when class >200 lines, when cohesion is low

#### Long Class Breakdown

```csharp
// ❌ Before: God class with multiple responsibilities
public class UserService
{
    private readonly IDbContext _context;
    private readonly IEmailService _emailService;
    private readonly IFileStorage _fileStorage;
    private readonly IPaymentService _paymentService;

    // User management
    public async Task<User> CreateUserAsync(UserRegistrationData data) { ... }
    public async Task<User> GetUserAsync(int id) { ... }
    public async Task UpdateUserAsync(User user) { ... }

    // Email operations
    public async Task SendWelcomeEmailAsync(User user) { ... }
    public async Task SendPasswordResetEmailAsync(User user) { ... }
    public async Task SendNewsletterAsync(List<User> users) { ... }

    // File management
    public async Task<string> UploadProfileImageAsync(int userId, Stream imageStream) { ... }
    public async Task<Stream> GetProfileImageAsync(int userId) { ... }
    public async Task DeleteProfileImageAsync(int userId) { ... }

    // Payment operations
    public async Task<PaymentResult> ProcessPaymentAsync(User user, decimal amount) { ... }
    public async Task<List<Payment>> GetUserPaymentsAsync(int userId) { ... }
    public async Task RefundPaymentAsync(string paymentId) { ... }
}

// ✅ After: Separated responsibilities into focused classes
public class UserService
{
    private readonly IUserRepository _userRepository;
    private readonly IUserNotificationService _notificationService;

    public async Task<User> CreateUserAsync(UserRegistrationData data)
    {
        var user = new User(data.Email, data.Name);
        await _userRepository.SaveAsync(user);
        await _notificationService.SendWelcomeNotificationAsync(user);
        return user;
    }

    public async Task<User> GetUserAsync(int id)
    {
        return await _userRepository.GetByIdAsync(id);
    }

    public async Task UpdateUserAsync(User user)
    {
        await _userRepository.UpdateAsync(user);
    }
}

public class UserNotificationService : IUserNotificationService
{
    private readonly IEmailService _emailService;

    public async Task SendWelcomeNotificationAsync(User user)
    {
        await _emailService.SendAsync(user.Email, "Welcome", GetWelcomeTemplate(user));
    }

    public async Task SendPasswordResetNotificationAsync(User user)
    {
        await _emailService.SendAsync(user.Email, "Password Reset", GetPasswordResetTemplate(user));
    }

    public async Task SendNewsletterAsync(List<User> users)
    {
        foreach (var user in users)
        {
            await _emailService.SendAsync(user.Email, "Newsletter", GetNewsletterTemplate());
        }
    }
}

public class UserProfileImageService
{
    private readonly IFileStorage _fileStorage;
    private readonly IUserRepository _userRepository;

    public async Task<string> UploadProfileImageAsync(int userId, Stream imageStream)
    {
        var user = await _userRepository.GetByIdAsync(userId);
        var imageUrl = await _fileStorage.UploadAsync($"profiles/{userId}", imageStream);

        user.ProfileImageUrl = imageUrl;
        await _userRepository.UpdateAsync(user);

        return imageUrl;
    }
}

public class UserPaymentService
{
    private readonly IPaymentService _paymentService;
    private readonly IUserRepository _userRepository;

    public async Task<PaymentResult> ProcessPaymentAsync(User user, decimal amount)
    {
        return await _paymentService.ProcessAsync(user.PaymentInfo, amount);
    }

    public async Task<List<Payment>> GetUserPaymentsAsync(int userId)
    {
        return await _paymentService.GetPaymentsForUserAsync(userId);
    }
}
```

#### Feature Envy Resolution

```python
# ❌ Before: Method in wrong class, envies data from another class
class Order:
    def __init__(self, customer, items):
        self.customer = customer
        self.items = items
        self.total_price = 0

class OrderProcessor:
    def calculate_discount(self, order):
        # This method is envious of Customer data
        if order.customer.membership_type == "premium":
            if order.customer.years_active >= 5:
                return 0.20  # 20% discount
            elif order.customer.years_active >= 2:
                return 0.15  # 15% discount
            else:
                return 0.10  # 10% discount
        elif order.customer.membership_type == "regular":
            if order.customer.years_active >= 3:
                return 0.05  # 5% discount
        return 0

# ✅ After: Method moved to appropriate class
class Customer:
    def __init__(self, membership_type, years_active):
        self.membership_type = membership_type
        self.years_active = years_active

    def calculate_discount_rate(self):
        """Calculate discount rate based on customer loyalty"""
        if self.membership_type == "premium":
            if self.years_active >= 5:
                return 0.20
            elif self.years_active >= 2:
                return 0.15
            else:
                return 0.10
        elif self.membership_type == "regular":
            if self.years_active >= 3:
                return 0.05
        return 0

class Order:
    def __init__(self, customer, items):
        self.customer = customer
        self.items = items
        self.total_price = 0

class OrderProcessor:
    def calculate_total_with_discount(self, order):
        base_total = sum(item.price * item.quantity for item in order.items)
        discount_rate = order.customer.calculate_discount_rate()
        return base_total * (1 - discount_rate)
```

### Level 4: 🟢 Refine Abstractions (Architecture Foundation)

**Focus**: Tackle missing abstractions and parameter organization

**When to Apply**: Sprint boundaries, when parameter lists >3, when data clumps appear

#### Long Parameter List Reduction

```java
// ❌ Before: Long parameter list with related data scattered
public class ReportGenerator {
    public Report generateUserReport(
        String userId,
        String userName,
        String userEmail,
        String userDepartment,
        LocalDate startDate,
        LocalDate endDate,
        String reportType,
        String outputFormat,
        boolean includeDetails,
        boolean includeCharts,
        String sortBy,
        String sortDirection
    ) {
        // Report generation logic...
    }
}

// ✅ After: Grouped related parameters into cohesive objects
public class UserReportRequest {
    private final UserInfo userInfo;
    private final DateRange dateRange;
    private final ReportOptions options;

    public UserReportRequest(UserInfo userInfo, DateRange dateRange, ReportOptions options) {
        this.userInfo = userInfo;
        this.dateRange = dateRange;
        this.options = options;
    }

    // Getters...
}

public class UserInfo {
    private final String userId;
    private final String userName;
    private final String userEmail;
    private final String userDepartment;

    // Constructor and getters...
}

public class DateRange {
    private final LocalDate startDate;
    private final LocalDate endDate;

    public DateRange(LocalDate startDate, LocalDate endDate) {
        if (startDate.isAfter(endDate)) {
            throw new IllegalArgumentException("Start date must be before end date");
        }
        this.startDate = startDate;
        this.endDate = endDate;
    }

    // Business methods
    public long getDurationInDays() {
        return ChronoUnit.DAYS.between(startDate, endDate);
    }
}

public class ReportOptions {
    private final String reportType;
    private final String outputFormat;
    private final boolean includeDetails;
    private final boolean includeCharts;
    private final SortOptions sortOptions;

    // Constructor and getters...
}

public class ReportGenerator {
    public Report generateUserReport(UserReportRequest request) {
        validateRequest(request);
        return buildReport(request);
    }

    private void validateRequest(UserReportRequest request) {
        if (request.getDateRange().getDurationInDays() > 365) {
            throw new IllegalArgumentException("Report period cannot exceed 365 days");
        }
    }
}
```

#### Data Clumps Elimination

```typescript
// ❌ Before: Address data scattered throughout codebase
interface User {
  id: string;
  name: string;
  email: string;
  streetAddress: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

interface Company {
  id: string;
  name: string;
  streetAddress: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

function formatUserAddress(user: User): string {
  return `${user.streetAddress}, ${user.city}, ${user.state} ${user.zipCode}, ${user.country}`;
}

function calculateShippingCost(
  streetAddress: string,
  city: string,
  state: string,
  zipCode: string,
  country: string,
  weight: number,
): number {
  // Shipping calculation logic using address components...
}

// ✅ After: Address extracted as cohesive value object
class Address {
  constructor(
    public readonly streetAddress: string,
    public readonly city: string,
    public readonly state: string,
    public readonly zipCode: string,
    public readonly country: string,
  ) {
    this.validateAddress();
  }

  private validateAddress(): void {
    if (!this.streetAddress.trim())
      throw new Error("Street address is required");
    if (!this.city.trim()) throw new Error("City is required");
    if (!this.zipCode.trim()) throw new Error("ZIP code is required");
  }

  format(): string {
    return `${this.streetAddress}, ${this.city}, ${this.state} ${this.zipCode}, ${this.country}`;
  }

  isInternational(): boolean {
    return this.country.toLowerCase() !== "usa";
  }

  getShippingZone(): string {
    // Business logic for determining shipping zone
    if (this.isInternational()) return "international";
    return ["CA", "NY", "NJ"].includes(this.state) ? "northeast" : "domestic";
  }
}

interface User {
  id: string;
  name: string;
  email: string;
  address: Address;
}

interface Company {
  id: string;
  name: string;
  address: Address;
}

function calculateShippingCost(address: Address, weight: number): number {
  const zone = address.getShippingZone();
  const baseRate = getBaseRateForZone(zone);
  const weightMultiplier = Math.ceil(weight / 5) * 0.5;

  return baseRate + weightMultiplier;
}
```

#### Primitive Obsession Resolution

```csharp
// ❌ Before: Primitive obsession with string-based identifiers
public class OrderService
{
    public async Task<Order> GetOrderAsync(string orderId)
    {
        if (string.IsNullOrEmpty(orderId))
            throw new ArgumentException("Order ID cannot be empty");

        return await _repository.GetByIdAsync(orderId);
    }

    public async Task<User> GetOrderCustomerAsync(string orderId)
    {
        var order = await GetOrderAsync(orderId);
        return await _userService.GetUserAsync(order.CustomerId); // string customer ID
    }

    public async Task AssignOrderToUser(string orderId, string userId)
    {
        // Risk: Could accidentally swap parameters
        var order = await GetOrderAsync(orderId);
        order.CustomerId = userId;
        await _repository.SaveAsync(order);
    }
}

// ✅ After: Strong typing with value objects
public record OrderId(string Value)
{
    public OrderId(string value) : this(value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("Order ID cannot be empty", nameof(value));
        if (!Guid.TryParse(value, out _))
            throw new ArgumentException("Order ID must be a valid GUID", nameof(value));

        Value = value;
    }

    public static implicit operator string(OrderId orderId) => orderId.Value;
    public static implicit operator OrderId(string value) => new(value);
}

public record UserId(string Value)
{
    public UserId(string value) : this(value)
    {
        if (string.IsNullOrWhiteSpace(value))
            throw new ArgumentException("User ID cannot be empty", nameof(value));
        if (!Guid.TryParse(value, out _))
            throw new ArgumentException("User ID must be a valid GUID", nameof(value));

        Value = value;
    }

    public static implicit operator string(UserId userId) => userId.Value;
    public static implicit operator UserId(string value) => new(value);
}

public class Order
{
    public OrderId Id { get; set; }
    public UserId CustomerId { get; set; }
    // Other properties...
}

public class OrderService
{
    public async Task<Order> GetOrderAsync(OrderId orderId)
    {
        return await _repository.GetByIdAsync(orderId);
    }

    public async Task<User> GetOrderCustomerAsync(OrderId orderId)
    {
        var order = await GetOrderAsync(orderId);
        return await _userService.GetUserAsync(order.CustomerId);
    }

    public async Task AssignOrderToUser(OrderId orderId, UserId userId)
    {
        // Compiler prevents parameter swapping
        var order = await GetOrderAsync(orderId);
        order.CustomerId = userId;
        await _repository.SaveAsync(order);
    }
}
```

### Level 5: 🔵 Refactor to Design Patterns (Pattern Application)

**Focus**: Apply strategic design patterns for polymorphic behavior

**When to Apply**: Release preparation, when switch statements appear, when behavior varies by type

#### Switch Statements to Strategy Pattern

```python
# ❌ Before: Switch statement handling different payment types
class PaymentProcessor:
    def process_payment(self, payment_type, amount, payment_details):
        if payment_type == "credit_card":
            # Credit card processing logic
            card_number = payment_details['card_number']
            expiry = payment_details['expiry']
            cvv = payment_details['cvv']

            if not self.validate_credit_card(card_number, expiry, cvv):
                return {"success": False, "error": "Invalid card details"}

            # Process with credit card gateway
            gateway_response = self.credit_card_gateway.charge(amount, card_number, expiry, cvv)
            return {
                "success": gateway_response.success,
                "transaction_id": gateway_response.transaction_id,
                "fee": amount * 0.029  # 2.9% fee
            }

        elif payment_type == "paypal":
            # PayPal processing logic
            email = payment_details['email']

            if not self.validate_paypal_email(email):
                return {"success": False, "error": "Invalid PayPal email"}

            # Process with PayPal API
            paypal_response = self.paypal_api.create_payment(amount, email)
            return {
                "success": paypal_response.success,
                "transaction_id": paypal_response.payment_id,
                "fee": amount * 0.034  # 3.4% fee
            }

        elif payment_type == "bank_transfer":
            # Bank transfer processing logic
            account_number = payment_details['account_number']
            routing_number = payment_details['routing_number']

            if not self.validate_bank_account(account_number, routing_number):
                return {"success": False, "error": "Invalid bank account"}

            # Process with ACH
            ach_response = self.ach_processor.process_transfer(amount, account_number, routing_number)
            return {
                "success": ach_response.success,
                "transaction_id": ach_response.transfer_id,
                "fee": 0.50  # Fixed fee
            }

        else:
            return {"success": False, "error": "Unsupported payment type"}

# ✅ After: Strategy pattern with polymorphic behavior
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def validate_payment_details(self, payment_details: dict) -> bool:
        pass

    @abstractmethod
    def process_payment(self, amount: float, payment_details: dict) -> dict:
        pass

    @abstractmethod
    def calculate_fee(self, amount: float) -> float:
        pass

class CreditCardPaymentStrategy(PaymentStrategy):
    def __init__(self, gateway):
        self.gateway = gateway

    def validate_payment_details(self, payment_details: dict) -> bool:
        required_fields = ['card_number', 'expiry', 'cvv']
        return all(field in payment_details for field in required_fields)

    def process_payment(self, amount: float, payment_details: dict) -> dict:
        if not self.validate_payment_details(payment_details):
            return {"success": False, "error": "Invalid card details"}

        response = self.gateway.charge(
            amount,
            payment_details['card_number'],
            payment_details['expiry'],
            payment_details['cvv']
        )

        return {
            "success": response.success,
            "transaction_id": response.transaction_id,
            "fee": self.calculate_fee(amount)
        }

    def calculate_fee(self, amount: float) -> float:
        return amount * 0.029  # 2.9% fee

class PayPalPaymentStrategy(PaymentStrategy):
    def __init__(self, api):
        self.api = api

    def validate_payment_details(self, payment_details: dict) -> bool:
        return 'email' in payment_details and '@' in payment_details['email']

    def process_payment(self, amount: float, payment_details: dict) -> dict:
        if not self.validate_payment_details(payment_details):
            return {"success": False, "error": "Invalid PayPal email"}

        response = self.api.create_payment(amount, payment_details['email'])

        return {
            "success": response.success,
            "transaction_id": response.payment_id,
            "fee": self.calculate_fee(amount)
        }

    def calculate_fee(self, amount: float) -> float:
        return amount * 0.034  # 3.4% fee

class BankTransferPaymentStrategy(PaymentStrategy):
    def __init__(self, ach_processor):
        self.ach_processor = ach_processor

    def validate_payment_details(self, payment_details: dict) -> bool:
        required_fields = ['account_number', 'routing_number']
        return all(field in payment_details for field in required_fields)

    def process_payment(self, amount: float, payment_details: dict) -> dict:
        if not self.validate_payment_details(payment_details):
            return {"success": False, "error": "Invalid bank account"}

        response = self.ach_processor.process_transfer(
            amount,
            payment_details['account_number'],
            payment_details['routing_number']
        )

        return {
            "success": response.success,
            "transaction_id": response.transfer_id,
            "fee": self.calculate_fee(amount)
        }

    def calculate_fee(self, amount: float) -> float:
        return 0.50  # Fixed fee

class PaymentProcessor:
    def __init__(self):
        self.strategies = {
            "credit_card": CreditCardPaymentStrategy(CreditCardGateway()),
            "paypal": PayPalPaymentStrategy(PayPalAPI()),
            "bank_transfer": BankTransferPaymentStrategy(ACHProcessor())
        }

    def process_payment(self, payment_type: str, amount: float, payment_details: dict) -> dict:
        strategy = self.strategies.get(payment_type)
        if not strategy:
            return {"success": False, "error": "Unsupported payment type"}

        return strategy.process_payment(amount, payment_details)

    def add_payment_strategy(self, payment_type: str, strategy: PaymentStrategy):
        """Easily extensible for new payment methods"""
        self.strategies[payment_type] = strategy
```

#### State Pattern for Complex State Behavior

```javascript
// ❌ Before: Complex state-dependent behavior with conditionals
class OrderManager {
  constructor() {
    this.status = "pending";
  }

  processPayment() {
    if (this.status === "pending") {
      console.log("Processing payment for pending order");
      this.status = "paid";
      return { success: true, message: "Payment processed" };
    } else if (this.status === "paid") {
      return { success: false, message: "Order already paid" };
    } else if (this.status === "shipped") {
      return {
        success: false,
        message: "Cannot process payment for shipped order",
      };
    } else if (this.status === "delivered") {
      return {
        success: false,
        message: "Cannot process payment for delivered order",
      };
    } else if (this.status === "cancelled") {
      return {
        success: false,
        message: "Cannot process payment for cancelled order",
      };
    }
  }

  ship() {
    if (this.status === "paid") {
      console.log("Shipping order");
      this.status = "shipped";
      return { success: true, message: "Order shipped" };
    } else if (this.status === "pending") {
      return { success: false, message: "Cannot ship unpaid order" };
    } else if (this.status === "shipped") {
      return { success: false, message: "Order already shipped" };
    } else if (this.status === "delivered") {
      return { success: false, message: "Order already delivered" };
    } else if (this.status === "cancelled") {
      return { success: false, message: "Cannot ship cancelled order" };
    }
  }

  cancel() {
    if (this.status === "pending" || this.status === "paid") {
      console.log("Cancelling order");
      this.status = "cancelled";
      return { success: true, message: "Order cancelled" };
    } else {
      return {
        success: false,
        message: "Cannot cancel order in current state",
      };
    }
  }
}

// ✅ After: State pattern with polymorphic state behavior
class OrderState {
  processPayment(order) {
    return { success: false, message: "Invalid operation for current state" };
  }

  ship(order) {
    return { success: false, message: "Invalid operation for current state" };
  }

  cancel(order) {
    return { success: false, message: "Invalid operation for current state" };
  }

  getStatusName() {
    return "unknown";
  }
}

class PendingOrderState extends OrderState {
  processPayment(order) {
    console.log("Processing payment for pending order");
    order.setState(new PaidOrderState());
    return { success: true, message: "Payment processed" };
  }

  cancel(order) {
    console.log("Cancelling pending order");
    order.setState(new CancelledOrderState());
    return { success: true, message: "Order cancelled" };
  }

  getStatusName() {
    return "pending";
  }
}

class PaidOrderState extends OrderState {
  ship(order) {
    console.log("Shipping paid order");
    order.setState(new ShippedOrderState());
    return { success: true, message: "Order shipped" };
  }

  cancel(order) {
    console.log("Cancelling paid order (refund required)");
    order.setState(new CancelledOrderState());
    // Trigger refund process
    order.processRefund();
    return { success: true, message: "Order cancelled, refund initiated" };
  }

  getStatusName() {
    return "paid";
  }
}

class ShippedOrderState extends OrderState {
  deliver(order) {
    console.log("Marking order as delivered");
    order.setState(new DeliveredOrderState());
    return { success: true, message: "Order delivered" };
  }

  getStatusName() {
    return "shipped";
  }
}

class DeliveredOrderState extends OrderState {
  getStatusName() {
    return "delivered";
  }
}

class CancelledOrderState extends OrderState {
  getStatusName() {
    return "cancelled";
  }
}

class OrderManager {
  constructor() {
    this.state = new PendingOrderState();
  }

  setState(state) {
    this.state = state;
  }

  processPayment() {
    return this.state.processPayment(this);
  }

  ship() {
    return this.state.ship(this);
  }

  cancel() {
    return this.state.cancel(this);
  }

  getStatus() {
    return this.state.getStatusName();
  }

  processRefund() {
    // Refund logic here
    console.log("Processing refund");
  }
}
```

### Level 6: 🔵 Refactor to SOLID++ (Advanced Principles)

**Focus**: Advanced architectural principles and SOLID compliance

**When to Apply**: Release preparation, major architectural changes, when SOLID violations detected

#### Single Responsibility Principle Resolution

```java
// ❌ Before: Class with multiple responsibilities (Divergent Change smell)
public class UserManager {
    private final DatabaseConnection db;
    private final EmailService emailService;
    private final FileSystem fileSystem;
    private final PaymentGateway paymentGateway;

    // User data management
    public User createUser(String email, String name) {
        User user = new User(email, name);
        String sql = "INSERT INTO users (email, name) VALUES (?, ?)";
        db.execute(sql, user.getEmail(), user.getName());
        return user;
    }

    public User getUserById(int id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        ResultSet rs = db.query(sql, id);
        return mapResultSetToUser(rs);
    }

    // Email operations
    public void sendWelcomeEmail(User user) {
        String subject = "Welcome to our platform!";
        String body = generateWelcomeEmailBody(user);
        emailService.send(user.getEmail(), subject, body);
    }

    public void sendPasswordReset(User user) {
        String resetToken = generateResetToken();
        String subject = "Password Reset Request";
        String body = generatePasswordResetBody(user, resetToken);
        emailService.send(user.getEmail(), subject, body);
    }

    // File management
    public void uploadProfileImage(int userId, byte[] imageData) {
        String fileName = "profile_" + userId + ".jpg";
        fileSystem.writeFile("/uploads/profiles/" + fileName, imageData);

        String sql = "UPDATE users SET profile_image = ? WHERE id = ?";
        db.execute(sql, fileName, userId);
    }

    // Payment processing
    public PaymentResult processPayment(User user, BigDecimal amount) {
        return paymentGateway.charge(user.getPaymentInfo(), amount);
    }

    // Validation logic
    public boolean isValidEmail(String email) {
        return email.contains("@") && email.contains(".");
    }

    // Utility methods
    private String generateResetToken() { /* implementation */ }
    private String generateWelcomeEmailBody(User user) { /* implementation */ }
    private String generatePasswordResetBody(User user, String token) { /* implementation */ }
    private User mapResultSetToUser(ResultSet rs) { /* implementation */ }
}

// ✅ After: Separated into single-responsibility classes
public interface UserRepository {
    User save(User user);
    User findById(int id);
    void updateProfileImage(int userId, String fileName);
}

public class DatabaseUserRepository implements UserRepository {
    private final DatabaseConnection db;

    public DatabaseUserRepository(DatabaseConnection db) {
        this.db = db;
    }

    @Override
    public User save(User user) {
        String sql = "INSERT INTO users (email, name) VALUES (?, ?)";
        db.execute(sql, user.getEmail(), user.getName());
        return user;
    }

    @Override
    public User findById(int id) {
        String sql = "SELECT * FROM users WHERE id = ?";
        ResultSet rs = db.query(sql, id);
        return mapResultSetToUser(rs);
    }

    @Override
    public void updateProfileImage(int userId, String fileName) {
        String sql = "UPDATE users SET profile_image = ? WHERE id = ?";
        db.execute(sql, fileName, userId);
    }

    private User mapResultSetToUser(ResultSet rs) {
        // Mapping logic
    }
}

public interface UserNotificationService {
    void sendWelcomeEmail(User user);
    void sendPasswordResetEmail(User user, String resetToken);
}

public class EmailUserNotificationService implements UserNotificationService {
    private final EmailService emailService;

    public EmailUserNotificationService(EmailService emailService) {
        this.emailService = emailService;
    }

    @Override
    public void sendWelcomeEmail(User user) {
        String subject = "Welcome to our platform!";
        String body = generateWelcomeEmailBody(user);
        emailService.send(user.getEmail(), subject, body);
    }

    @Override
    public void sendPasswordResetEmail(User user, String resetToken) {
        String subject = "Password Reset Request";
        String body = generatePasswordResetBody(user, resetToken);
        emailService.send(user.getEmail(), subject, body);
    }

    private String generateWelcomeEmailBody(User user) { /* implementation */ }
    private String generatePasswordResetBody(User user, String token) { /* implementation */ }
}

public interface ProfileImageService {
    void uploadProfileImage(int userId, byte[] imageData);
}

public class FileSystemProfileImageService implements ProfileImageService {
    private final FileSystem fileSystem;
    private final UserRepository userRepository;

    public FileSystemProfileImageService(FileSystem fileSystem, UserRepository userRepository) {
        this.fileSystem = fileSystem;
        this.userRepository = userRepository;
    }

    @Override
    public void uploadProfileImage(int userId, byte[] imageData) {
        String fileName = "profile_" + userId + ".jpg";
        fileSystem.writeFile("/uploads/profiles/" + fileName, imageData);
        userRepository.updateProfileImage(userId, fileName);
    }
}

public interface UserPaymentService {
    PaymentResult processPayment(User user, BigDecimal amount);
}

public class GatewayUserPaymentService implements UserPaymentService {
    private final PaymentGateway paymentGateway;

    public GatewayUserPaymentService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }

    @Override
    public PaymentResult processPayment(User user, BigDecimal amount) {
        return paymentGateway.charge(user.getPaymentInfo(), amount);
    }
}

// Coordinating service following Single Responsibility Principle
public class UserService {
    private final UserRepository userRepository;
    private final UserNotificationService notificationService;
    private final UserValidator validator;

    public UserService(
        UserRepository userRepository,
        UserNotificationService notificationService,
        UserValidator validator
    ) {
        this.userRepository = userRepository;
        this.notificationService = notificationService;
        this.validator = validator;
    }

    public User createUser(String email, String name) {
        validator.validateEmail(email);

        User user = new User(email, name);
        User savedUser = userRepository.save(user);

        notificationService.sendWelcomeEmail(savedUser);

        return savedUser;
    }

    public User getUserById(int id) {
        return userRepository.findById(id);
    }
}
```

## Technology-Specific Refactoring Examples

### React/TypeScript Refactoring

```typescript
// ❌ Before: Component with multiple responsibilities and complex state
export const UserDashboard: FC = () => {
  const [user, setUser] = useState<User>();
  const [orders, setOrders] = useState<Order[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order>();
  const [notificationFilter, setNotificationFilter] = useState<'all' | 'unread'>('all');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Multiple API calls in component
      const [userResponse, ordersResponse, notificationsResponse] = await Promise.all([
        fetch('/api/user/profile'),
        fetch('/api/user/orders'),
        fetch('/api/user/notifications')
      ]);

      setUser(await userResponse.json());
      setOrders(await ordersResponse.json());
      setNotifications(await notificationsResponse.json());
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleOrderClick = (order: Order) => {
    setSelectedOrder(order);
    setShowOrderModal(true);
  };

  const filteredNotifications = notifications.filter(notification =>
    notificationFilter === 'all' || !notification.isRead
  );

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Welcome, {user?.name}</h1>
        <img src={user?.profileImage} alt="Profile" />
      </header>

      <section className="orders-section">
        <h2>Recent Orders</h2>
        <div className="orders-grid">
          {orders.map(order => (
            <div key={order.id} onClick={() => handleOrderClick(order)}>
              <span>Order #{order.id}</span>
              <span>{order.status}</span>
              <span>${order.total}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="notifications-section">
        <div className="notifications-header">
          <h2>Notifications</h2>
          <select
            value={notificationFilter}
            onChange={(e) => setNotificationFilter(e.target.value as 'all' | 'unread')}
          >
            <option value="all">All</option>
            <option value="unread">Unread</option>
          </select>
        </div>
        <div className="notifications-list">
          {filteredNotifications.map(notification => (
            <div key={notification.id} className={notification.isRead ? 'read' : 'unread'}>
              <span>{notification.title}</span>
              <span>{notification.message}</span>
            </div>
          ))}
        </div>
      </section>

      {showOrderModal && selectedOrder && (
        <OrderDetailsModal
          order={selectedOrder}
          onClose={() => setShowOrderModal(false)}
        />
      )}
    </div>
  );
};

// ✅ After: Separated responsibilities with custom hooks and focused components
// Custom hook for dashboard data management
export const useDashboardData = () => {
  const [user, setUser] = useState<User>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  const loadUserProfile = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/user/profile');
      const userData = await response.json();
      setUser(userData);
    } catch (err) {
      setError('Failed to load user profile');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUserProfile();
  }, [loadUserProfile]);

  return { user, loading, error, reloadUser: loadUserProfile };
};

// Custom hook for orders management
export const useUserOrders = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  const loadOrders = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/user/orders');
      const ordersData = await response.json();
      setOrders(ordersData);
    } catch (err) {
      setError('Failed to load orders');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOrders();
  }, [loadOrders]);

  return { orders, loading, error, reloadOrders: loadOrders };
};

// Custom hook for notifications management
export const useUserNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  const loadNotifications = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/user/notifications');
      const notificationsData = await response.json();
      setNotifications(notificationsData);
    } catch (err) {
      setError('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  const filteredNotifications = useMemo(() =>
    notifications.filter(notification =>
      filter === 'all' || !notification.isRead
    ), [notifications, filter]
  );

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  return {
    notifications: filteredNotifications,
    filter,
    setFilter,
    loading,
    error,
    reloadNotifications: loadNotifications
  };
};

// Focused component for user profile header
const UserProfileHeader: FC<{ user: User }> = ({ user }) => (
  <header className="dashboard-header">
    <h1>Welcome, {user.name}</h1>
    <img src={user.profileImage} alt="Profile" />
  </header>
);

// Focused component for orders section
const OrdersSection: FC<{ orders: Order[], onOrderClick: (order: Order) => void }> = ({
  orders,
  onOrderClick
}) => (
  <section className="orders-section">
    <h2>Recent Orders</h2>
    <div className="orders-grid">
      {orders.map(order => (
        <OrderCard
          key={order.id}
          order={order}
          onClick={() => onOrderClick(order)}
        />
      ))}
    </div>
  </section>
);

const OrderCard: FC<{ order: Order, onClick: () => void }> = ({ order, onClick }) => (
  <div className="order-card" onClick={onClick}>
    <span>Order #{order.id}</span>
    <span className={`status ${order.status.toLowerCase()}`}>{order.status}</span>
    <span className="total">${order.total}</span>
  </div>
);

// Focused component for notifications section
const NotificationsSection: FC = () => {
  const { notifications, filter, setFilter, loading, error } = useUserNotifications();

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <section className="notifications-section">
      <NotificationsHeader filter={filter} onFilterChange={setFilter} />
      <NotificationsList notifications={notifications} />
    </section>
  );
};

const NotificationsHeader: FC<{
  filter: 'all' | 'unread',
  onFilterChange: (filter: 'all' | 'unread') => void
}> = ({ filter, onFilterChange }) => (
  <div className="notifications-header">
    <h2>Notifications</h2>
    <select value={filter} onChange={(e) => onFilterChange(e.target.value as 'all' | 'unread')}>
      <option value="all">All</option>
      <option value="unread">Unread</option>
    </select>
  </div>
);

// Main dashboard component with single responsibility
export const UserDashboard: FC = () => {
  const { user, loading: userLoading, error: userError } = useDashboardData();
  const { orders, loading: ordersLoading, error: ordersError } = useUserOrders();
  const [selectedOrder, setSelectedOrder] = useState<Order>();

  const handleOrderClick = useCallback((order: Order) => {
    setSelectedOrder(order);
  }, []);

  const handleCloseOrderModal = useCallback(() => {
    setSelectedOrder(undefined);
  }, []);

  if (userLoading) return <LoadingSpinner />;
  if (userError) return <ErrorMessage message={userError} />;
  if (!user) return <ErrorMessage message="User not found" />;

  return (
    <div className="dashboard">
      <UserProfileHeader user={user} />

      {ordersLoading ? (
        <LoadingSpinner />
      ) : ordersError ? (
        <ErrorMessage message={ordersError} />
      ) : (
        <OrdersSection orders={orders} onOrderClick={handleOrderClick} />
      )}

      <NotificationsSection />

      {selectedOrder && (
        <OrderDetailsModal
          order={selectedOrder}
          onClose={handleCloseOrderModal}
        />
      )}
    </div>
  );
};
```

## Refactoring Timing Integration with TDD

### TDD Cycle Integration

**GREEN State Refactoring** (Every Cycle):

```
🔴 RED (Write failing test)
      ↓
🟢 GREEN (Make test pass)
      ↓
🔵 REFACTOR (Level 1-2: Readability & Complexity)
      ↓
Commit → Next RED test
```

**Sprint Boundary Refactoring**:

- **Level 3-4**: Responsibilities and Abstractions
- **Quality Review**: Code review focusing on architectural patterns
- **Architecture Validation**: Ensure design principles compliance

**Release Preparation Refactoring**:

- **Level 5-6**: Design Patterns and SOLID principles
- **Comprehensive Quality Assessment**: Full codebase analysis
- **Performance Validation**: Ensure refactoring hasn't degraded performance

### Parallel Change Integration

**EXPAND Phase** (Level 5-6 Application):

```csharp
// Create new implementation alongside existing
public class ModernPaymentProcessor : IPaymentProcessor
{
    // New strategy pattern implementation
}

// Keep old implementation working
public class LegacyPaymentProcessor : IPaymentProcessor
{
    // Original implementation
}
```

**MIGRATE Phase** (Level 3-4 Application):

```csharp
// Gradually switch consumers
public class OrderService
{
    public OrderService(IPaymentProcessor processor)
    {
        // Can receive either implementation
        _processor = processor;
    }
}
```

**CONTRACT Phase** (Level 1-2 Cleanup):

```csharp
// Remove old implementation
// Clean up unused code and dependencies
// Apply naming improvements
```

## Best Practices and Guidelines

### Refactoring Safety

1. **Comprehensive Test Coverage**: ≥80% coverage before major refactoring
2. **Small Steps**: Make incremental changes within each level
3. **Frequent Commits**: Commit after each level completion
4. **Green State Maintenance**: All tests must remain green during refactoring
5. **Performance Monitoring**: Validate that refactoring doesn't degrade performance

### Quality Metrics

- **Cyclomatic Complexity**: Target <10 per method, <20 per class
- **Maintainability Index**: Target >70 (Visual Studio scale)
- **Code Coverage**: Maintain or improve coverage during refactoring
- **Coupling Metrics**: Reduce afferent/efferent coupling
- **Cohesion Metrics**: Improve LCOM (Lack of Cohesion in Methods)

### Success Indicators

- **Readability**: New team members can understand code intent quickly
- **Extensibility**: New features added with minimal existing code changes
- **Testability**: Easy to write unit tests for components
- **Maintainability**: Bug fixes require changes in single location
- **Performance**: System performance maintained or improved

This systematic refactoring guide provides the foundation for progressive code quality improvement, ensuring maintainable, extensible, and high-quality software throughout the nWave methodology development process.
