"""Debug script to test EventType import in pytest context."""
import sys
print("Python path:", sys.path)

try:
    from des.adapters.driven.logging.audit_events import EventType
    print("SUCCESS: EventType imported")
    print("EventType values:", [e.name for e in EventType])
except ImportError as e:
    print(f"FAILED: ImportError - {e}")
    import traceback
    traceback.print_exc()
