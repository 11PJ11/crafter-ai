"""Unit tests for TurnCounter component."""

import sys

from src.des.domain.turn_counter import TurnCounter


class TestTurnCounter:
    """Test suite for TurnCounter functionality."""

    def test_initialize_counter_with_zero_turns(self):
        """TurnCounter should start with zero turns for a phase."""
        counter = TurnCounter()

        assert counter.get_current_turn("DISCOVER") == 0

    def test_increment_turn_updates_count(self):
        """increment_turn() should increase turn count by 1."""
        counter = TurnCounter()

        counter.increment_turn("DISCOVER")

        assert counter.get_current_turn("DISCOVER") == 1

    def test_increment_turn_multiple_times(self):
        """increment_turn() should track multiple increments."""
        counter = TurnCounter()

        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")

        assert counter.get_current_turn("DISCOVER") == 3

    def test_is_limit_exceeded_returns_false_when_under_limit(self):
        """is_limit_exceeded() should return False when under turn limit."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")

        assert counter.is_limit_exceeded("DISCOVER", max_turns=5) is False

    def test_is_limit_exceeded_returns_false_when_at_limit(self):
        """is_limit_exceeded() should return False when exactly at turn limit."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")

        assert counter.is_limit_exceeded("DISCOVER", max_turns=5) is False

    def test_is_limit_exceeded_returns_true_when_over_limit(self):
        """is_limit_exceeded() should return True when exceeding turn limit."""
        counter = TurnCounter()
        for _ in range(6):
            counter.increment_turn("DISCOVER")

        assert counter.is_limit_exceeded("DISCOVER", max_turns=5) is True

    def test_multiple_phases_tracked_independently(self):
        """Different phases should maintain independent turn counts."""
        counter = TurnCounter()

        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCUSS")

        assert counter.get_current_turn("DISCOVER") == 2
        assert counter.get_current_turn("DISCUSS") == 1

    def test_reset_turn_resets_specific_phase(self):
        """reset_turn() should reset turn count for specific phase to zero."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCUSS")

        counter.reset_turn("DISCOVER")

        assert counter.get_current_turn("DISCOVER") == 0
        assert counter.get_current_turn("DISCUSS") == 1

    def test_is_limit_exceeded_with_negative_limit(self):
        """is_limit_exceeded() should handle negative limits correctly."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")

        # With negative limit, any positive count should exceed it
        assert counter.is_limit_exceeded("DISCOVER", max_turns=-1) is True

    def test_is_limit_exceeded_with_zero_limit(self):
        """is_limit_exceeded() should handle zero limit correctly."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")

        # With zero limit, any positive count should exceed it
        assert counter.is_limit_exceeded("DISCOVER", max_turns=0) is True

    def test_is_limit_exceeded_with_zero_turns_and_zero_limit(self):
        """is_limit_exceeded() should return False when both count and limit are zero."""
        counter = TurnCounter()

        # Zero turns should not exceed zero limit
        assert counter.is_limit_exceeded("DISCOVER", max_turns=0) is False

    def test_increment_turn_with_large_numbers(self):
        """increment_turn() should handle large turn counts without overflow."""
        counter = TurnCounter()

        # Increment to a very large number
        large_count = sys.maxsize - 10
        counter._turn_counts["DISCOVER"] = large_count

        counter.increment_turn("DISCOVER")

        assert counter.get_current_turn("DISCOVER") == large_count + 1

    def test_is_limit_exceeded_with_very_large_limit(self):
        """is_limit_exceeded() should handle very large limits correctly."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")

        # Should not exceed extremely large limit
        assert counter.is_limit_exceeded("DISCOVER", max_turns=sys.maxsize) is False

    def test_to_dict_serializes_state(self):
        """to_dict() should serialize counter state to dictionary."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCOVER")
        counter.increment_turn("DISCUSS")

        state = counter.to_dict()

        assert state == {"DISCOVER": 2, "DISCUSS": 1}

    def test_from_dict_deserializes_state(self):
        """from_dict() should restore counter state from dictionary."""
        counter = TurnCounter()
        state = {"DISCOVER": 3, "DISCUSS": 1, "DESIGN": 5}

        counter.from_dict(state)

        assert counter.get_current_turn("DISCOVER") == 3
        assert counter.get_current_turn("DISCUSS") == 1
        assert counter.get_current_turn("DESIGN") == 5

    def test_from_dict_with_empty_state(self):
        """from_dict() should handle empty state correctly."""
        counter = TurnCounter()
        counter.increment_turn("DISCOVER")

        counter.from_dict({})

        # All counts should be cleared
        assert counter.get_current_turn("DISCOVER") == 0

    def test_serialization_roundtrip_preserves_state(self):
        """Serializing and deserializing should preserve complete state."""
        original = TurnCounter()
        original.increment_turn("DISCOVER")
        original.increment_turn("DISCOVER")
        original.increment_turn("DISCUSS")
        original.increment_turn("DESIGN")

        state = original.to_dict()
        restored = TurnCounter()
        restored.from_dict(state)

        assert restored.get_current_turn("DISCOVER") == 2
        assert restored.get_current_turn("DISCUSS") == 1
        assert restored.get_current_turn("DESIGN") == 1
