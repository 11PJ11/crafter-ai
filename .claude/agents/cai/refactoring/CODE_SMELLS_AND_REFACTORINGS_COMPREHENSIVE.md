# Comprehensive Code Smells and Refactoring Techniques Collection

## Research Sources
- **Refactoring.guru**: Complete catalog of code smells and refactoring techniques
- **Refactoring.com**: Martin Fowler's refactoring catalog with detailed mechanics
- **Alcor Academy Training Materials**: Refactoring Priority Premise and systematic approach

---

## Part 1: Complete Code Smell Taxonomy

### 1. Bloaters (BLO) - Code that has grown too large or complex

#### Long Method
- **Description**: Method that has grown too large and does too many things
- **Symptoms**: Method is difficult to understand, contains many lines of code
- **Causes**: Adding new functionality to existing methods over time
- **Treatment**: Extract Method, Compose Method, Replace Method with Method Object
- **Priority**: Critical
- **Refactoring Level**: Level 2 (Complexity Reduction)

#### Large Class
- **Description**: Class trying to do too much, has too many instance variables/methods
- **Symptoms**: Class is hard to understand, maintain, and modify
- **Causes**: Accumulating responsibilities over time
- **Treatment**: Extract Class, Extract Subclass, Extract Interface, Replace Data Value with Object
- **Priority**: High
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Primitive Obsession
- **Description**: Using primitives instead of small objects for simple tasks
- **Symptoms**: Use of constants for coding information, use of string constants as field names
- **Causes**: Creating a field instead of a separate class
- **Treatment**: Replace Data Value with Object, Introduce Parameter Object, Replace Type Code with Class, Replace Type Code with Subclasses, Replace Type Code with State/Strategy, Replace Array with Object
- **Priority**: Critical
- **Refactoring Level**: Level 4 (Abstraction Refinement)

#### Long Parameter List
- **Description**: Method has four or more parameters
- **Symptoms**: Method signature is hard to understand and use
- **Causes**: Merging several types of algorithms into single method, passing everything needed as parameters
- **Treatment**: Replace Parameter with Method Call, Preserve Whole Object, Introduce Parameter Object
- **Priority**: High
- **Refactoring Level**: Level 4 (Abstraction Refinement)

#### Data Clumps
- **Description**: Same group of variables found in different parts of code
- **Symptoms**: Same fields in different classes, same parameters in method signatures
- **Causes**: Poor program structure or copy-paste programming
- **Treatment**: Extract Class, Introduce Parameter Object, Preserve Whole Object
- **Priority**: Medium
- **Refactoring Level**: Level 4 (Abstraction Refinement)

### 2. Object-Orientation Abusers (OOA) - Improper use of OO principles

#### Switch Statements
- **Description**: Complex switch operator or sequence of if statements
- **Symptoms**: Adding new variant requires searching for all switch statements
- **Causes**: Type code that should be replaced with polymorphism
- **Treatment**: Replace Conditional with Polymorphism, Replace Type Code with Subclasses, Replace Type Code with State/Strategy, Replace Parameter with Explicit Methods, Introduce Null Object
- **Priority**: Critical
- **Refactoring Level**: Level 5 (Design Pattern Application)

#### Temporary Field
- **Description**: Instance variables set only under certain circumstances
- **Symptoms**: Objects contain fields that are empty most of the time
- **Causes**: Complex algorithms require many inputs
- **Treatment**: Extract Class, Introduce Null Object
- **Priority**: Medium
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Refused Bequest
- **Description**: Subclass uses only some methods/properties inherited from parent
- **Symptoms**: Hierarchy is wrong, subclass doesn't support parent interface
- **Causes**: Wrong inheritance hierarchy design
- **Treatment**: Push Down Method, Push Down Field, Replace Inheritance with Delegation
- **Priority**: Medium
- **Refactoring Level**: Level 6 (SOLID++ Principles)

#### Alternative Classes with Different Interfaces
- **Description**: Two classes perform identical functions but have different method names
- **Symptoms**: Duplicate functionality with different interfaces
- **Causes**: Programmer unaware of existing class with needed functionality
- **Treatment**: Rename Method, Move Method, Extract Superclass
- **Priority**: Medium
- **Refactoring Level**: Level 3 (Responsibility Organization)

### 3. Change Preventers (CHP) - Code that makes changes difficult

#### Divergent Change
- **Description**: One class commonly changed for different reasons
- **Symptoms**: Adding new feature requires changing multiple unrelated methods
- **Causes**: Poor program structure, violation of Single Responsibility Principle
- **Treatment**: Extract Class
- **Priority**: Critical
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Shotgun Surgery
- **Description**: Change requires making many small changes to many classes
- **Symptoms**: Hard to find all places needing changes
- **Causes**: Single responsibility split among many classes
- **Treatment**: Move Method, Move Field, Inline Class
- **Priority**: Critical
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Parallel Inheritance Hierarchies
- **Description**: Creating subclass for one class requires creating subclass for another
- **Symptoms**: Two inheritance hierarchies with similar prefixes
- **Causes**: Initially acceptable but becomes problematic as hierarchy grows
- **Treatment**: Move Method, Move Field
- **Priority**: Medium
- **Refactoring Level**: Level 6 (SOLID++ Principles)

### 4. Dispensables (DIS) - Code that serves no useful purpose

#### Comments
- **Description**: Method filled with explanatory comments
- **Symptoms**: Comments used to explain complex code
- **Causes**: Code is not self-explanatory
- **Treatment**: Extract Method, Rename Method, Introduce Assertion
- **Priority**: Low
- **Refactoring Level**: Level 1 (Foundation Refactoring)

#### Duplicate Code
- **Description**: Code fragments that look almost identical
- **Symptoms**: Same code structure in multiple places
- **Causes**: Copy-paste programming, multiple programmers working on same program
- **Treatment**: Extract Method, Pull Up Method, Form Template Method, Substitute Algorithm, Extract Class
- **Priority**: Critical
- **Refactoring Level**: Level 2 (Complexity Reduction)

#### Lazy Class
- **Description**: Class doesn't do enough to earn its keep
- **Symptoms**: Class with few methods and little functionality
- **Causes**: Class was useful but became too small after refactoring
- **Treatment**: Inline Class, Collapse Hierarchy
- **Priority**: Low
- **Refactoring Level**: Level 1 (Foundation Refactoring)

#### Data Class
- **Description**: Class contains only fields and crude methods for accessing them
- **Symptoms**: Class acts like data container without behavior
- **Causes**: Fields made public or extensive use of getting/setting methods
- **Treatment**: Move Method, Encapsulate Field, Encapsulate Collection
- **Priority**: Medium
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Dead Code
- **Description**: Variable, parameter, field, method, or class no longer used
- **Symptoms**: Unreachable code, unused variables
- **Causes**: Requirements changed but code wasn't cleaned up
- **Treatment**: Delete unused code
- **Priority**: Low
- **Refactoring Level**: Level 1 (Foundation Refactoring)

#### Speculative Generality
- **Description**: Code created to support anticipated future features that never come
- **Symptoms**: Abstract classes/interfaces with single implementation
- **Causes**: "Just in case" programming
- **Treatment**: Collapse Hierarchy, Inline Class, Remove Parameter, Rename Method
- **Priority**: Low
- **Refactoring Level**: Level 1 (Foundation Refactoring)

### 5. Couplers (COU) - Code with excessive coupling between classes

#### Feature Envy
- **Description**: Method accesses data of another object more than its own
- **Symptoms**: Method uses multiple getter methods from another class
- **Causes**: Fields moved to data class after Extract Class
- **Treatment**: Move Method, Extract Method
- **Priority**: High
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Inappropriate Intimacy
- **Description**: Classes know too much about each other's private details
- **Symptoms**: Classes use each other's private fields and methods
- **Causes**: Poor encapsulation design
- **Treatment**: Move Method, Move Field, Extract Class, Hide Delegate, Replace Inheritance with Delegation
- **Priority**: High
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Message Chains
- **Description**: Sequence of calls to get needed object
- **Symptoms**: Code like a.getB().getC().getD()
- **Causes**: Client coupled to navigation structure
- **Treatment**: Hide Delegate, Extract Method
- **Priority**: Medium
- **Refactoring Level**: Level 3 (Responsibility Organization)

#### Middle Man
- **Description**: Class performs only one action - delegating work to another class
- **Symptoms**: Most methods simply delegate to methods of another class
- **Causes**: Over-application of Hide Delegate
- **Treatment**: Remove Middle Man, Inline Method, Replace Delegation with Inheritance
- **Priority**: Medium
- **Refactoring Level**: Level 4 (Abstraction Refinement)

---

## Part 2: Complete Refactoring Techniques Catalog

### Composing Methods

#### Extract Method / Extract Function
- **Motivation**: Break down methods that are too long or do too much, improve code readability and maintainability
- **When to Apply**: Method is difficult to understand, contains many lines of code, code fragment can be logically grouped
- **Mechanics**:
  1. Create new method with clear, descriptive, intention-revealing name
  2. Copy relevant code fragment to new method
  3. Scan extracted code for references to variables that are local in scope to original method
  4. Handle variables carefully:
     - Local variables declared within fragment can remain unchanged
     - Variables declared before extraction may need to be passed as parameters
     - If local variable changes, ensure changed value is returned if needed
  5. Replace extracted code in original method with call to new method
  6. Test after transformation
- **Benefits**: Improves code readability, reduces code duplication, isolates independent code parts, reduces likelihood of errors
- **Solves Code Smells**: Long Method, Duplicate Code, Comments (by creating self-documenting method names)
- **Example**:
  ```javascript
  // Before
  function printOwing(invoice) {
    printBanner();
    let outstanding = calculateOutstanding();
    console.log(`name: ${invoice.customer}`);
    console.log(`amount: ${outstanding}`);
  }

  // After
  function printOwing(invoice) {
    printBanner();
    let outstanding = calculateOutstanding();
    printDetails(outstanding);
  }

  function printDetails(outstanding) {
    console.log(`name: ${invoice.customer}`);
    console.log(`amount: ${outstanding}`);
  }
  ```

#### Inline Method / Inline Function
- **Motivation**: When method body is more obvious than the method itself, or method simply delegates to another method
- **When to Apply**: Method simply delegates, many small confusing methods, methods became redundant through code changes
- **Mechanics**:
  1. Verify method isn't redefined in subclasses
  2. Find all calls to the method
  3. Replace each method call with the method's actual content
  4. Delete the original method definition
  5. Test after each replacement
- **Benefits**: Minimizes unneeded methods, makes code more straightforward, reduces unnecessary method delegation
- **Solves Code Smells**: Middle Man, unnecessary indirection
- **Safety Protocol**: Check for polymorphic redefinition before inlining
- **Example**:
  ```java
  // Before
  int getRating() {
    return moreThanFiveLateDeliveries() ? 2 : 1;
  }
  boolean moreThanFiveLateDeliveries() {
    return numberOfLateDeliveries > 5;
  }

  // After
  int getRating() {
    return numberOfLateDeliveries > 5 ? 2 : 1;
  }
  ```

#### Extract Variable
- **Motivation**: Make complex expressions more understandable by breaking them into self-explanatory parts
- **When to Apply**: Expression is hard to understand, complex conditional logic, magic numbers/strings
- **Mechanics**:
  1. Ensure expression has no side effects
  2. Insert new line before complex expression
  3. Declare immutable variable, set to copy of expression
  4. Replace original expression part with new variable
  5. Test and repeat for all complex parts
- **Benefits**: Improved code readability, more self-documenting code, easier comprehension of complex logic
- **Solves Code Smells**: Complex expressions, magic numbers/strings, poor readability
- **Drawbacks**: Increased number of variables, potential minor performance overhead
- **Example**:
  ```java
  // Before
  if ((platform.toUpperCase().indexOf("MAC") > -1) &&
       (browser.toUpperCase().indexOf("IE") > -1) &&
        wasInitialized() && resize > 0)

  // After
  final boolean isMacOs = platform.toUpperCase().indexOf("MAC") > -1;
  final boolean isIE = browser.toUpperCase().indexOf("IE") > -1;
  final boolean wasResized = resize > 0;

  if (isMacOs && isIE && wasInitialized() && wasResized) {
    // do something
  }
  ```

#### Inline Variable / Inline Temp
- **Motivation**: Variable name doesn't communicate more than expression itself
- **When to Apply**: Unnecessary temporary variables, variable name adds no clarity
- **Mechanics**:
  1. Check that right-hand side of assignment has no side effects
  2. Declare variable as immutable if it isn't already
  3. Find first usage of variable and replace with expression
  4. Test and repeat for other usages
  5. Remove declaration and assignment
- **Solves Code Smells**: Unnecessary variables, temporary variable clutter

#### Replace Temp with Query
- **Motivation**: Using temporary variable to hold result of expression that could be calculated when needed
- **When to Apply**: Temporary variables that hold calculated values, reducing method-level variables
- **Mechanics**:
  1. Check that variable is determined completely before used and only assigned once
  2. Extract right-hand side of assignment into method with intention-revealing name
  3. Test extracted method
  4. Use Inline Variable to remove temporary variable
- **Benefits**: Cleaner methods, reusable calculations, better encapsulation
- **Solves Code Smells**: Long Method, temporary variable overuse

#### Split Temporary Variable
- **Motivation**: Temporary variable assigned more than once for different purposes
- **When to Apply**: Variable serves multiple roles, confusing variable usage
- **Mechanics**:
  1. Change name of temp at its declaration and first assignment
  2. Change all references to temp up to second assignment
  3. Test
  4. Repeat for each subsequent assignment
- **Solves Code Smells**: Confusing variable usage, multiple responsibilities

#### Remove Assignments to Parameters
- **Motivation**: Code assigns to parameter, causing confusion
- **When to Apply**: Parameters are modified within method body
- **Mechanics**:
  1. Create temporary variable for parameter
  2. Replace all references to parameter with temp
  3. Change assignment to assign to temp
- **Solves Code Smells**: Confusing parameter usage

#### Replace Method with Method Object
- **Motivation**: Method too complex to extract smaller methods due to heavy local variable usage
- **When to Apply**: Long method with many local variables that prevent extraction
- **Mechanics**:
  1. Create new class with same name as method
  2. Give class final field for object that hosted original method
  3. Give class field for each temporary variable and parameter
  4. Create constructor that takes method object and parameters
  5. Create compute method
  6. Copy method body to compute method
  7. Replace old method with new class creation and compute call
- **Solves Code Smells**: Long Method, complex local variable dependencies

#### Substitute Algorithm
- **Motivation**: Replace existing algorithm with clearer, simpler, or more efficient one
- **When to Apply**: Algorithm is overly complicated, simpler algorithm discovered, requirements changed
- **Mechanics**:
  1. Simplify existing algorithm as much as possible (use Extract Method to remove unimportant code)
  2. Create new algorithm in separate method
  3. Replace old algorithm with new one
  4. Compare results between old and new implementations
  5. Delete old algorithm once testing complete
- **Safety Protocol**: Incremental testing, maintain original until confidence achieved
- **Benefits**: Simpler code, better performance, clearer logic

#### Inline Method
- **Motivation**: Method body is as clear as its name
- **Mechanics**:
  1. Check that method isn't redefined in subclasses
  2. Find all calls to method
  3. Replace each call with method body
  4. Remove method definition
- **Solves**: Middle Man, unnecessary indirection

#### Extract Variable
- **Motivation**: Expression is hard to understand
- **Mechanics**:
  1. Ensure expression has no side effects
  2. Declare immutable variable, set to copy of expression
  3. Replace original expression with new variable
  4. Test
- **Solves**: Complex expressions, magic numbers/strings

#### Inline Variable
- **Motivation**: Variable name doesn't communicate more than expression itself
- **Mechanics**:
  1. Check that right-hand side of assignment has no side effects
  2. Declare variable as immutable if it isn't already
  3. Find first usage of variable and replace with expression
  4. Test and repeat for other usages
  5. Remove declaration and assignment
- **Solves**: Unnecessary variables

#### Replace Temp with Query
- **Motivation**: Using temporary variable to hold result of expression
- **Mechanics**:
  1. Check that variable is determined completely before used
  2. Extract right-hand side of assignment into method
  3. Test
  4. Use Inline Variable to remove temp
- **Solves**: Long methods, temporary variables

#### Split Temporary Variable
- **Motivation**: Temporary variable assigned more than once
- **Mechanics**:
  1. Change name of temp at its declaration and first assignment
  2. Change all references to temp up to second assignment
  3. Test
  4. Repeat for each assignment
- **Solves**: Confusing variable usage

#### Remove Assignments to Parameters
- **Motivation**: Code assigns to parameter
- **Mechanics**:
  1. Create temporary variable for parameter
  2. Replace all references to parameter with temp
  3. Change assignment to assign to temp
- **Solves**: Confusing parameter usage

### Moving Features Between Objects

#### Move Method
- **Motivation**: Method is used more in another class than in its own class, improve class internal coherence, reduce dependencies between classes
- **When to Apply**: Method more relevant to another class, reduces coupling, increases class cohesion
- **Mechanics**:
  1. Verify and potentially move features used by the old method
     - Check if method is declared in superclasses/subclasses
     - Consider moving related methods/features
  2. Declare new method in recipient class
     - Optional: Rename method to fit new context
  3. Determine how to reference the recipient class
     - Use existing field/method or create new method/field to store recipient object
  4. Copy code to target class, adjust to fit new home
  5. Replace old method with delegation or remove it entirely
     - Turn original method into delegating method or remove it
     - Update all references to use new method location
  6. Test after each step
- **Benefits**: Improved class organization, reduced coupling, better encapsulation
- **Solves Code Smells**: Feature Envy, Inappropriate Intimacy, Shotgun Surgery
- **Safety Protocol**: Ensure method isn't critical to original class functionality, minimize breaking dependencies

#### Move Field
- **Motivation**: Field is used by another class more than the class it's defined in
- **Mechanics**:
  1. Encapsulate field if it isn't already
  2. Test
  3. Create field and accessing methods in target class
  4. Determine reference to target object from source
  5. Replace field access with call to target
  6. Test
  7. Remove field in source class
- **Solves**: Feature Envy, Inappropriate Intimacy

#### Extract Class
- **Motivation**: Class has grown too large and accumulated too many responsibilities, violates Single Responsibility Principle
- **When to Apply**: Class doing work of two classes, class too large and complex, methods and fields clustered around specific functionality
- **Mechanics**:
  1. Decide how to split responsibilities of class
  2. Create new class to express split-off responsibilities
  3. Establish relationship between old and new class
  4. Use Move Field and Move Method to transfer responsibilities:
     - Start with private methods to minimize errors
     - Move incrementally and test after each move
  5. Review and reduce interfaces of both classes
  6. Rename classes if needed
  7. Evaluate accessibility of new class (public vs package-private)
- **Benefits**: Improves code clarity, increases reliability, makes classes more tolerant to changes, reduces risk of breaking functionality
- **Drawbacks**: Over-application leads to unnecessary complexity, may require Inline Class if taken too far
- **Solves Code Smells**: Large Class, Divergent Change, Shotgun Surgery
- **Key Principle**: "When one class does the work of two, awkwardness results"

#### Inline Class
- **Motivation**: Class isn't doing very much
- **Mechanics**:
  1. Declare public methods of source class on absorbing class
  2. Change all references to use absorbing class
  3. Test
  4. Use Move Method and Move Field to move features from source to absorbing class
  5. Hold funeral for source class
- **Solves**: Lazy Class, result of other refactorings

#### Hide Delegate
- **Motivation**: Client getting object from field of server object, then calling method on result
- **Mechanics**:
  1. For each method on delegate, create simple delegating method on server
  2. Adjust client to call server
  3. Test after adjusting each method
  4. Remove delegate accessor from server
- **Solves**: Message Chains

#### Remove Middle Man
- **Motivation**: Class doing too much delegation
- **Mechanics**:
  1. Create accessor for delegate
  2. For each client use of delegating method, remove method from server and make client call delegate directly
  3. Test after each method
- **Solves**: Middle Man

### Organizing Data

#### Self Encapsulate Field
- **Motivation**: Direct access to field but access becomes awkward
- **Mechanics**:
  1. Create getting and setting methods for field
  2. Replace all direct references to field with getting/setting methods
  3. Make field private
- **Benefits**: Subclass override access, lazy initialization

#### Replace Data Value with Object
- **Motivation**: Data item needs additional data or behavior
- **Mechanics**:
  1. Create class for value, give it equivalent field to original
  2. Add getting method and constructor that takes field
  3. Change type of field to new class
  4. Change getting method to call getting method of new class
  5. If field is set, create setting method for new class
  6. Change setting method to create new instance of class
- **Solves**: Primitive Obsession

#### Change Value to Reference
- **Motivation**: Many equal instances of class that you want to replace with single object
- **Mechanics**:
  1. Use Replace Constructor with Factory Method
  2. Create repository that handles access to objects
  3. Decide what should be responsible for providing access to objects
  4. Change constructors to return reference objects from repository
- **Benefits**: Shared object state

#### Change Reference to Value
- **Motivation**: Reference object small and immutable and becoming awkward to manage
- **Mechanics**:
  1. Check that candidate class is immutable or can become immutable
  2. Create equals method and hash method
  3. Test
- **Benefits**: Simplified object management

### Simplifying Conditional Expressions

#### Decompose Conditional
- **Motivation**: Complex conditional statements are difficult to understand - "The longer a piece of code is, the harder it's to understand"
- **When to Apply**: Complex conditional (if-then/else or switch) that is hard to parse and comprehend
- **Mechanics**:
  1. Extract the conditional expression to a separate method with intention-revealing name
  2. Extract the `then` block to its own method with descriptive name
  3. Extract the `else` block to its own method with descriptive name
  4. Test after each extraction
- **Benefits**: Improves code readability, makes maintenance easier, creates more descriptive method names, breaks complex logic into smaller pieces
- **Solves Code Smells**: Long Method, Complex Conditionals, Comments (by creating self-documenting method names)
- **Example**:
  ```java
  // Before
  if (date.before(SUMMER_START) || date.after(SUMMER_END)) {
    charge = quantity * winterRate + winterServiceCharge;
  }
  else {
    charge = quantity * summerRate;
  }

  // After
  if (isSummer(date)) {
    charge = summerCharge(quantity);
  }
  else {
    charge = winterCharge(quantity);
  }
  ```

#### Consolidate Conditional Expression
- **Motivation**: Series of conditional tests with same result
- **Mechanics**:
  1. Check that none of conditionals have side effects
  2. Replace string of conditionals with single conditional using logical operators
  3. Test
  4. Extract condition into separate method
- **Benefits**: Clearer intention

#### Consolidate Duplicate Conditional Fragments
- **Motivation**: Same fragment of code in all branches of conditional
- **Mechanics**:
  1. Identify code executed same way regardless of condition
  2. If at beginning, move before conditional
  3. If at end, move after conditional
  4. If in middle, look for code changes or use Extract Method
- **Solves**: Duplicate Code

#### Remove Control Flag
- **Motivation**: Variable acting as control flag for series of boolean expressions
- **Mechanics**:
  1. Find value that gets control flag to exit
  2. Replace assignments to control flag with breaks or returns
  3. Test after each replacement
- **Benefits**: Clearer control flow

#### Replace Nested Conditional with Guard Clauses
- **Motivation**: Method has conditional behavior for normal course of action and unusual cases
- **Mechanics**:
  1. For each check, put check and return on single line
  2. Test after each check is replaced
  3. If all guard clauses return same value, use Consolidate Conditional Expression
- **Benefits**: Clearer main path

#### Replace Conditional with Polymorphism
- **Motivation**: Code contains conditionals that vary behavior based on object class/interface, object field values, or method call results
- **When to Apply**: Switch statements on type, complex if-else chains based on object type, behavior varies by class
- **Benefits**: Adheres to "Tell-Don't-Ask" principle, removes duplicate code, enables easy addition of new behavior variants, follows Open/Closed Principle
- **Mechanics**:
  1. Prepare class hierarchy for alternative behaviors (create inheritance structure if needed)
  2. Extract the conditional method if it contains multiple actions (use Extract Method)
  3. For each subclass:
     - Redefine the method in subclass
     - Copy corresponding conditional branch code to subclass method
     - Delete that branch from original conditional
     - Test after each branch removal
  4. Repeat until conditional is empty
  5. Delete original conditional
  6. Declare original method abstract in superclass
- **Solves Code Smells**: Switch Statements, Type Code, Alternative Classes with Different Interfaces
- **Example**:
  ```java
  // Before (with switch/conditional logic)
  class Bird {
    double getSpeed() {
      switch (type) {
        case EUROPEAN:
          return getBaseSpeed();
        case AFRICAN:
          return getBaseSpeed() - getLoadFactor() * numberOfCoconuts;
        // other cases...
      }
    }
  }

  // After (using polymorphism)
  abstract class Bird {
    abstract double getSpeed();
  }

  class European extends Bird {
    double getSpeed() {
      return getBaseSpeed();
    }
  }

  class African extends Bird {
    double getSpeed() {
      return getBaseSpeed() - getLoadFactor() * numberOfCoconuts;
    }
  }
  ```

### Simplifying Method Calls

#### Rename Method
- **Motivation**: Name of method doesn't reveal its purpose
- **Mechanics**:
  1. Check to see whether method signature is implemented by superclass or subclass
  2. Declare new method with new name, copy old body to new name, change old body to call new method
  3. Test
  4. Find all references to old method and change them
  5. Test
  6. Remove old method
  7. If old method is part of interface, leave it and mark as deprecated
- **Solves**: Poor naming, Comments

#### Add Parameter
- **Motivation**: Method needs more information from its caller
- **Mechanics**:
  1. Check whether method signature is implemented by superclass or subclass
  2. Declare new method with added parameter, copy old body
  3. Change body of old method to call new method
  4. Test
  5. Find all callers and change them to use new method
  6. Test
  7. Remove old method
- **When needed**: Method needs additional information

#### Remove Parameter
- **Motivation**: Parameter no longer used by method body
- **Mechanics**:
  1. Check whether method signature is implemented by superclass or subclass
  2. Declare new method without parameter, copy old body
  3. Change body of old method to call new method
  4. Test
  5. Find all callers and change them to use new method
  6. Test
  7. Remove old method
- **Solves**: Unused parameters, Speculative Generality

#### Separate Query from Modifier
- **Motivation**: Method returns value but also changes something
- **Mechanics**:
  1. Create query method that returns value that original method returns
  2. Modify original method so it calls query method and returns result
  3. Test
  4. Replace every call to original method with call to query method followed by call to original method
  5. Make original method return void
  6. Test
- **Benefits**: Side-effect free queries

#### Parameterize Method
- **Motivation**: Several methods do similar things but with different values contained in method body
- **Mechanics**:
  1. Create parameterized method that can substitute for each repetitive method
  2. Test
  3. Replace one old method with call to new parameterized method
  4. Test
  5. Repeat for all methods
- **Solves**: Duplicate Code in methods

#### Replace Parameter with Explicit Methods
- **Motivation**: Method runs different code depending on values of enumerated parameter
- **Mechanics**:
  1. Create explicit method for each value of parameter
  2. For each leg of conditional, create separate method and call appropriate one
  3. Test
  4. Replace conditional with calls to explicit methods
  5. Test
  6. Use Remove Parameter
- **Alternative to**: Parameterized methods when behavior very different

#### Preserve Whole Object
- **Motivation**: Getting several values from object and passing these values as parameters to method
- **Mechanics**:
  1. Create new parameter for whole object from which values come
  2. Test
  3. Determine which parameters can be obtained from whole object parameter
  4. Take one parameter and replace references to it within method body with calls to appropriate method on whole object parameter
  5. Delete parameter
  6. Test and repeat for other parameters
- **Solves**: Long Parameter List, Data Clumps

#### Replace Parameter with Method
- **Motivation**: Object invokes method on another object and passes result as parameter to method. Receiver can also invoke this method.
- **Mechanics**:
  1. If necessary, use Extract Method on calculation of parameter
  2. Replace references to parameter in method body with references to method
  3. Use Remove Parameter
- **Benefits**: Simplified parameter lists

#### Introduce Parameter Object
- **Motivation**: Multiple methods share identical parameter groups, parameters create code duplication, parameter lists becoming unwieldy
- **When to Apply**: Methods contain repeating group of parameters, multiple methods share identical parameter groups, parameter lists are unwieldy
- **Mechanics**:
  1. Create new immutable class representing the parameter group
  2. Add new parameter object to the method
  3. Replace individual parameters with object field references
  4. Test incrementally while replacing parameters
  5. Optionally move related methods/behaviors to new parameter object class
- **Benefits**: More readable code, reduces parameter duplication, consolidates related data and potential behaviors
- **Drawbacks**: Risk of creating "Data Class" if no behavior added, increases complexity if not implemented thoughtfully
- **Solves Code Smells**: Long Parameter List, Data Clumps, Primitive Obsession
- **Key Considerations**: Make parameter object immutable, consider moving related method logic to new class
- **Example**:
  ```javascript
  // Before
  function amountInvoiced(startDate, endDate) {...}
  function amountReceived(startDate, endDate) {...}
  function amountOverdue(startDate, endDate) {...}

  // After
  function amountInvoiced(aDateRange) {...}
  function amountReceived(aDateRange) {...}
  function amountOverdue(aDateRange) {...}

  class DateRange {
    constructor(startDate, endDate) {
      this.startDate = startDate;
      this.endDate = endDate;
    }
  }
  ```

### Dealing with Generalization

#### Pull Up Field
- **Motivation**: Two subclasses have same field
- **Mechanics**:
  1. Inspect all uses of candidate fields to ensure they are used in same way
  2. If fields have different names, use Rename Field to give them same name
  3. Test
  4. Create new field in superclass
  5. Remove fields from subclasses
  6. Test
- **Benefits**: Eliminates duplicate data

#### Pull Up Method
- **Motivation**: Subclasses grew and developed independently, causing identical (or nearly identical) methods - eliminates duplicate code
- **When to Apply**: Methods have identical results on subclasses, duplicate code in inheritance hierarchy
- **Mechanics**:
  1. Investigate similar methods in superclasses to avoid conflicts
  2. Standardize method formatting if needed (use Rename Method if different signatures)
  3. Adjust method parameters to desired superclass form
  4. Copy method to superclass
  5. Handle potential compatibility issues:
     - For fields: Use "Pull Up Field" or "Self-Encapsulate Field"
     - For methods: Declare abstract methods in superclass
  6. Remove duplicated methods from subclasses one by one
  7. Review method call locations and update if necessary
  8. Test after each method removal
- **Benefits**: Eliminates duplicate code, centralizes method maintenance, simplifies inheritance hierarchy
- **Challenges**: Ensuring method semantics remain consistent, managing dependencies, maintaining clear class responsibilities
- **Solves Code Smells**: Duplicate Code in inheritance hierarchy
- **Note**: Class may become abstract during this process

#### Pull Up Constructor Body
- **Motivation**: Constructors on subclasses with mostly identical bodies
- **Mechanics**:
  1. Define superclass constructor
  2. Move common code from beginning of subclass constructors to superclass constructor
  3. Try to use Extract Method on common code and call extracted method from constructors
  4. If common code is later in constructor, use Extract Method and then call from end of superclass constructor
- **Benefits**: Eliminates duplicate constructor code

#### Push Down Method
- **Motivation**: Method in superclass used by only one or few subclasses, rather than being universally applicable
- **When to Apply**: Behavior on superclass relevant only to some subclasses, planned features failed to materialize, functionality partially extracted from class hierarchy
- **Problem**: "Is behavior implemented in a superclass used by only one (or a few) subclasses?"
- **Mechanics**:
  1. Declare method in all subclasses that need it
  2. Copy method's code from superclass to relevant subclasses
  3. Remove method from superclass
  4. Test after method removal
  5. Remove method from subclasses that don't need it
  6. Verify method is now called from correct subclasses
- **Benefits**: Improves class coherence, places methods where they are logically expected, avoids code duplication
- **Solves Code Smells**: Refused Bequest, methods not universally applicable in inheritance hierarchy

#### Push Down Field
- **Motivation**: Field used only by some subclasses
- **Mechanics**:
  1. Declare field in all subclasses that need it
  2. Remove field from superclass
  3. Test
  4. Remove field from subclasses that don't need it
  5. Test
- **Benefits**: Reduces unused fields

#### Extract Subclass
- **Motivation**: Class has features used only in some instances
- **Mechanics**:
  1. Define new subclass of source class
  2. Provide constructors for new subclass
  3. Find calls to constructors of source class and replace with calls to new subclass constructor when features are needed
  4. Use Push Down Method and Push Down Field to move features to subclass
  5. Test after each push down
- **Solves**: Large Class when subset of features form coherent group

#### Extract Superclass
- **Motivation**: Two classes with similar features
- **Mechanics**:
  1. Create abstract superclass
  2. Make original classes subclasses of superclass
  3. Test
  4. Use Pull Up Field, Pull Up Method, and Pull Up Constructor Body to move common features to superclass
  5. Test after each pull up
  6. Examine methods left on subclasses and see if you can generalize them
- **Benefits**: Eliminates duplicate code between similar classes

#### Extract Interface
- **Motivation**: Several clients use same subset of class's interface, or two classes have part of interface in common
- **Mechanics**:
  1. Create empty interface
  2. Declare common operations in interface
  3. Have relevant class implement interface
  4. Test
  5. Adjust client type declarations to use interface
- **Benefits**: Clear subset interface

#### Collapse Hierarchy
- **Motivation**: Superclass and subclass not very different
- **Mechanics**:
  1. Choose which class to remove
  2. Use Pull Up Field and Pull Up Method or Push Down Field and Push Down Method to move behavior to single class
  3. Test after each move
  4. Adjust references to class being removed to use remaining class
  5. Remove empty class
  6. Test
- **Solves**: Unnecessary inheritance, Lazy Class

#### Form Template Method
- **Motivation**: Subclasses implement algorithms that contain similar steps in same order, leading to code duplication and maintenance challenges
- **When to Apply**: Subclasses develop algorithms in parallel, duplicate code in algorithmic structure, need to add new algorithm versions
- **Key Problem**: Subclasses have methods with identical algorithmic structure but different implementations
- **Mechanics**:
  1. Split algorithms in subclasses into constituent methods (use Extract Method)
  2. Move identical methods to superclass (use Pull Up Method)
  3. Rename non-similar methods consistently (use Rename Method for consistent signatures)
  4. Create abstract method signatures in superclass for different implementations
  5. Pull up main algorithm method to superclass
  6. Test after each step
- **Benefits**: Reduces code duplication, supports Open/Closed Principle, simplifies adding new algorithm versions, allows creating new subclasses without modifying existing code
- **Implementation Strategy**: Extract Method → Pull Up Method → Rename Method → Create abstract methods
- **Solves Code Smells**: Duplicate Code in algorithms, Template Method pattern violations
- **Design Pattern**: Closely related to Template Method design pattern for managing algorithmic variations

#### Replace Inheritance with Delegation
- **Motivation**: Subclass uses only part of superclass interface or doesn't want to inherit data
- **Mechanics**:
  1. Create field in subclass that refers to instance of superclass
  2. Change methods to delegate to superclass
  3. Test after changing each method
  4. Remove inheritance link
  5. Test
- **Solves**: Refused Bequest

#### Replace Delegation with Inheritance
- **Motivation**: Using delegation and often writing many simple delegations for entire interface
- **Mechanics**:
  1. Make delegating class subclass of delegate
  2. Test
  3. Remove delegation field
  4. Test
  5. Replace all delegating methods with inherited methods
  6. Test after replacing each method
- **Solves**: Middle Man when delegation is to full interface

### Additional Key Refactoring Techniques

#### Split Phase
- **Motivation**: Separate complex, multi-step computations into distinct phases for improved readability and modularity
- **When to Apply**: Complex computation that can be logically divided, mixed parsing and calculation logic
- **Mechanics**:
  1. Identify complex computation that can be logically divided
  2. Break computation into separate functions with clear responsibilities
  3. Extract parsing/data preparation logic into separate function
  4. Extract calculation logic into another function
  5. Create intermediate data structure to pass between phases
- **Benefits**: Separates concerns, improves readability, makes each function's purpose explicit, easier to test individual components
- **Example**:
  ```javascript
  // Before
  const orderData = orderString.split(/\s+/);
  const productPrice = priceList[orderData[0].split("-")[1]];
  const orderPrice = parseInt(orderData[1]) * productPrice;

  // After
  function parseOrder(aString) {
    const values = aString.split(/\s+/);
    return ({
      productID: values[0].split("-")[1],
      quantity: parseInt(values[1]),
    });
  }

  function price(order, priceList) {
    return order.quantity * priceList[order.productID];
  }

  const orderRecord = parseOrder(order);
  const orderPrice = price(orderRecord, priceList);
  ```

#### Encapsulate Field
- **Motivation**: Support object-oriented encapsulation principle by making fields private and creating access methods
- **When to Apply**: Public fields that can be directly accessed, need data protection and modularity, want flexibility for validation/complex logic
- **Mechanics**:
  1. Create getter and setter methods for the field
  2. Find all direct field invocations
  3. Replace field access with getter/setter methods
  4. Make the field private
  5. Test after each change
- **Benefits**: Improves code maintainability, allows performing complex operations related to field access, brings data and behaviors closer together
- **Solves Code Smells**: Data Class, poor encapsulation
- **Key Principle**: "One of the pillars of object-oriented programming is Encapsulation, the ability to conceal object data"
- **Example**:
  ```java
  // Before
  class Person {
    public String name;
  }

  // After
  class Person {
    private String name;

    public String getName() {
      return name;
    }

    public void setName(String arg) {
      name = arg;
    }
  }
  ```

#### Change Function Declaration / Change Signature
- **Motivation**: Function name doesn't reveal purpose, or function needs different parameters
- **When to Apply**: Method name unclear, need to add/remove parameters, signature doesn't match usage
- **Aliases**: Rename Function, Rename Method, Add Parameter, Remove Parameter, Change Signature
- **Mechanics**:
  1. Check if method signature implemented by superclass/subclass
  2. Create new method with desired signature
  3. Copy implementation to new method
  4. Change body of old method to call new method
  5. Find all callers and change them to use new method
  6. Remove old method
  7. Test after each change
- **Benefits**: Clear communication of intent, proper parameter usage, better API design
- **Example**:
  ```javascript
  // Before
  function circum(radius) {
    return 2 * Math.PI * radius;
  }

  // After
  function circumference(radius) {
    return 2 * Math.PI * radius;
  }
  ```

---

## Part 3: Atomic Transformation Mechanics

### Five Core Atomic Transformations

Based on Martin Fowler and industry best practices, all refactoring operations can be broken down into five atomic transformations:

#### 1. Rename
- **Description**: Change name of code element without changing behavior
- **Applies to**: Variables, methods, classes, fields, parameters
- **Safety Protocol**:
  1. Use IDE refactoring tools when available
  2. Verify all references updated
  3. Run tests to ensure no behavioral changes
- **Example**: `calculateTotal()` → `calculateOrderTotal()`

#### 2. Extract
- **Description**: Take portion of code and create new code element
- **Applies to**: Methods, classes, variables, constants, interfaces
- **Safety Protocol**:
  1. Identify code to extract
  2. Create new element with intention-revealing name
  3. Move code to new element
  4. Replace original code with call to new element
  5. Test after each step
- **Example**: Extract method from long method body

#### 3. Inline
- **Description**: Replace code element with its implementation
- **Applies to**: Methods, variables, classes
- **Safety Protocol**:
  1. Verify element has no side effects
  2. Replace all calls with implementation
  3. Remove original element
  4. Test after each replacement
- **Example**: Replace method call with method body

#### 4. Move
- **Description**: Relocate code element to different scope or class
- **Applies to**: Methods, fields, classes
- **Safety Protocol**:
  1. Check dependencies and usage
  2. Create element in target location
  3. Update all references
  4. Remove from original location
  5. Test after each step
- **Example**: Move method from one class to another

#### 5. Safe Delete
- **Description**: Remove unused code elements
- **Applies to**: Methods, fields, classes, parameters, variables
- **Safety Protocol**:
  1. Verify element is truly unused
  2. Check for dynamic references (reflection, etc.)
  3. Remove element
  4. Compile and test
- **Example**: Remove unused private method

### Compound Refactorings

Most named refactorings are combinations of these atomic transformations:

- **Extract Method** = Extract + Rename
- **Move Method** = Extract + Move + Inline + Safe Delete
- **Extract Class** = Extract + Move (multiple) + Rename
- **Replace Conditional with Polymorphism** = Extract + Move + Safe Delete (multiple times)

### Test Preservation Protocols

#### "Stay in Green" Methodology
1. **Start with green tests**: All tests must pass before refactoring
2. **Atomic changes**: Make smallest possible changes
3. **Test after each atomic transformation**: Verify tests still pass
4. **Rollback on red**: If tests fail, immediately rollback last change
5. **Commit frequently**: Save progress after successful transformations

#### Safety Checklist for Each Transformation
- [ ] All tests pass before transformation
- [ ] Transformation is truly atomic (single responsibility)
- [ ] No behavioral changes intended
- [ ] All references properly updated
- [ ] Tests pass after transformation
- [ ] Code compiles without errors
- [ ] No new warnings introduced

---

## Part 4: Alcor Academy Integration

### Refactoring Priority Premise (RPP)

The Alcor Academy approach emphasizes a systematic 6-level refactoring hierarchy that maximizes value through the 80-20 rule:

#### 80-20 Rule Application
- **80% of refactoring value** comes from **readability improvements** (Levels 1-2)
- **20% additional value** comes from **structural improvements** (Levels 3-6)
- **Focus effort** on Level 1-2 for maximum impact

#### Level Progression Strategy
1. **Start with Level 1-2**: Focus on readability and simplicity
2. **Measure impact**: Assess code quality improvements
3. **Progressive enhancement**: Move to higher levels only when needed
4. **Avoid premature complexity**: Don't jump to patterns without proven need

### Object Calisthenics to Code Smell Mapping

Object Calisthenics rules and their corresponding code smells:

1. **Only one level of indentation per method** → Long Method, Complex Conditionals
2. **Don't use the else keyword** → Complex Conditionals, Nested Conditionals
3. **Wrap all primitives and strings** → Primitive Obsession
4. **First class collections** → Primitive Obsession, Data Clumps
5. **One dot per line** → Message Chains, Feature Envy
6. **Don't abbreviate** → Poor naming, Comments needed
7. **Keep all entities small** → Large Class, Long Method, Long Parameter List
8. **No classes with more than two instance variables** → Large Class, Data Clumps
9. **No getters/setters/properties** → Data Class, Feature Envy

### Parallel Change Pattern

For complex refactorings that might break functionality:

#### Expand Phase
1. Create new implementation alongside existing code
2. Ensure both implementations work
3. Add feature toggles if necessary
4. Test both paths thoroughly

#### Migrate Phase
1. Gradually switch consumers to new implementation
2. Update one consumer at a time
3. Test after each migration
4. Monitor for issues

#### Contract Phase
1. Remove old implementation
2. Clean up feature toggles
3. Remove dead code
4. Final testing and validation

This pattern ensures zero downtime and safe transformation of critical code.

---

## Part 5: Integration with 6-Level Refactoring System

### Mapping Code Smells to Refactoring Levels

#### Level 1: Foundation Refactoring (Readability) 🟨
**Code Smells Addressed:**
- Dead Code → Safe Delete transformations
- Comments → Extract Method with intention-revealing names
- Speculative Generality → Safe Delete unused abstractions
- Magic Numbers/Strings → Extract Variable/Constant

**Primary Atomic Transformations:** Rename, Extract (variables/constants), Safe Delete

#### Level 2: Complexity Reduction (Simplification) 🟢
**Code Smells Addressed:**
- Long Method → Extract Method
- Duplicate Code → Extract Method, Pull Up Method
- Complex Conditionals → Decompose Conditional

**Primary Atomic Transformations:** Extract (methods), Move (common code)

#### Level 3: Responsibility Organization 🟢
**Code Smells Addressed:**
- Large Class → Extract Class
- Feature Envy → Move Method
- Inappropriate Intimacy → Move Method/Field, Extract Class
- Data Class → Move Method (add behavior)
- Divergent Change → Extract Class
- Shotgun Surgery → Move Method/Field

**Primary Atomic Transformations:** Move, Extract (classes)

#### Level 4: Abstraction Refinement 🟢
**Code Smells Addressed:**
- Long Parameter List → Introduce Parameter Object
- Data Clumps → Extract Class, Introduce Parameter Object
- Primitive Obsession → Replace Data Value with Object
- Middle Man → Inline Method, Safe Delete

**Primary Atomic Transformations:** Extract (objects), Inline, Move

#### Level 5: Design Pattern Application 🔵
**Code Smells Addressed:**
- Switch Statements → Replace Conditional with Polymorphism (Strategy Pattern)
- Temporary Field → State Pattern
- Alternative Classes with Different Interfaces → Adapter Pattern

**Primary Atomic Transformations:** Extract (interfaces), Move (to polymorphic structure)

#### Level 6: SOLID++ Principles Application 🔵
**Code Smells Addressed:**
- Refused Bequest → Liskov Substitution + Interface Segregation
- Parallel Inheritance Hierarchies → Interface Segregation
- God Class patterns → Single Responsibility Principle

**Primary Atomic Transformations:** Extract (interfaces), Move (responsibilities), Safe Delete (violations)

### Automated Detection Patterns

#### Syntax-Based Detection
- **Long Method**: Lines of code > threshold, cyclomatic complexity > threshold
- **Large Class**: Number of methods/fields > threshold, lines of code > threshold
- **Long Parameter List**: Parameter count > 4
- **Duplicate Code**: Identical code blocks, similar structure patterns

#### Semantic Analysis Detection
- **Feature Envy**: Method uses more external class methods than internal
- **Data Class**: Class with only getters/setters, no business logic
- **Dead Code**: Unreferenced methods/fields, unreachable code blocks
- **Message Chains**: Call chains longer than 3 levels (a.getB().getC().getD())

#### Pattern Recognition Detection
- **Switch Statements**: switch/case blocks, long if-else chains on type
- **Primitive Obsession**: String/int used for domain concepts
- **Middle Man**: Class where >50% methods delegate to another class
- **Refused Bequest**: Subclass doesn't use >50% of inherited interface

### Quality Metrics Integration

#### Before Refactoring (Baseline)
- Cyclomatic complexity per method
- Lines of code per class/method
- Coupling between objects (CBO)
- Lack of cohesion of methods (LCOM)
- Depth of inheritance tree (DIT)

#### After Refactoring (Validation)
- Complexity reduction metrics
- Improved cohesion scores
- Reduced coupling measurements
- Better inheritance hierarchy balance
- Maintained or improved test coverage

#### Success Criteria
- Complexity reduced by measurable amount
- No increase in coupling
- Improved cohesion scores
- All tests continue to pass
- No performance degradation

---

## Conclusion

This comprehensive collection provides:

1. **Complete code smell taxonomy** with 22 smells across 5 categories
2. **Full refactoring catalog** with detailed mechanics for 60+ techniques
3. **Atomic transformation framework** with 5 core operations
4. **Integration with 6-level systematic approach** from existing agent
5. **Alcor Academy methodology integration** with 80-20 rule and RPP
6. **Automated detection patterns** for systematic code smell identification
7. **Safety protocols** for test preservation during refactoring

This knowledge base will enable the systematic refactorer to provide comprehensive, safe, and effective refactoring guidance following industry best practices and proven methodologies.