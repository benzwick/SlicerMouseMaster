"""Tests for PlatformAdapter classes."""

from __future__ import annotations


class TestCanonicalButton:
    """Tests for CanonicalButton enum."""

    def test_button_values(self) -> None:
        """Test canonical button values match Qt conventions."""
        from MouseMasterLib.platform_adapter import CanonicalButton

        assert CanonicalButton.LEFT == 1
        assert CanonicalButton.RIGHT == 2
        assert CanonicalButton.MIDDLE == 4
        assert CanonicalButton.BACK == 8
        assert CanonicalButton.FORWARD == 16


class TestWindowsAdapter:
    """Tests for WindowsAdapter."""

    def test_normalize_button(self) -> None:
        """Test button normalization on Windows."""
        from MouseMasterLib.platform_adapter import CanonicalButton, WindowsAdapter

        adapter = WindowsAdapter()

        assert adapter.normalize_button(1) == CanonicalButton.LEFT
        assert adapter.normalize_button(2) == CanonicalButton.RIGHT
        assert adapter.normalize_button(4) == CanonicalButton.MIDDLE
        assert adapter.normalize_button(8) == CanonicalButton.BACK
        assert adapter.normalize_button(16) == CanonicalButton.FORWARD
        assert adapter.normalize_button(999) == CanonicalButton.UNKNOWN

    def test_normalize_modifiers(self) -> None:
        """Test modifier normalization on Windows."""
        from MouseMasterLib.platform_adapter import WindowsAdapter

        adapter = WindowsAdapter()

        # No modifiers
        assert adapter.normalize_modifiers(0) == set()

        # Shift
        assert adapter.normalize_modifiers(0x02000000) == {"shift"}

        # Ctrl
        assert adapter.normalize_modifiers(0x04000000) == {"ctrl"}

        # Multiple modifiers
        assert adapter.normalize_modifiers(0x02000000 | 0x04000000) == {"shift", "ctrl"}


class TestMacOSAdapter:
    """Tests for MacOSAdapter."""

    def test_normalize_button(self) -> None:
        """Test button normalization on macOS."""
        from MouseMasterLib.platform_adapter import CanonicalButton, MacOSAdapter

        adapter = MacOSAdapter()

        assert adapter.normalize_button(1) == CanonicalButton.LEFT
        assert adapter.normalize_button(8) == CanonicalButton.BACK

    def test_normalize_modifiers_with_swap(self) -> None:
        """Test modifier normalization with Ctrl/Meta swap enabled."""
        from MouseMasterLib.platform_adapter import MacOSAdapter

        adapter = MacOSAdapter(swap_ctrl_meta=True)

        # Qt Ctrl (Cmd on macOS) -> canonical Ctrl
        assert adapter.normalize_modifiers(0x04000000) == {"ctrl"}

        # Qt Meta (Ctrl on macOS) -> canonical Meta
        assert adapter.normalize_modifiers(0x10000000) == {"meta"}

    def test_normalize_modifiers_without_swap(self) -> None:
        """Test modifier normalization without Ctrl/Meta swap."""
        from MouseMasterLib.platform_adapter import MacOSAdapter

        adapter = MacOSAdapter(swap_ctrl_meta=False)

        # Qt Ctrl (Cmd on macOS) -> canonical Meta
        assert adapter.normalize_modifiers(0x04000000) == {"meta"}

        # Qt Meta (Ctrl on macOS) -> canonical Ctrl
        assert adapter.normalize_modifiers(0x10000000) == {"ctrl"}


class TestLinuxAdapter:
    """Tests for LinuxAdapter."""

    def test_normalize_button(self) -> None:
        """Test button normalization on Linux."""
        from MouseMasterLib.platform_adapter import CanonicalButton, LinuxAdapter

        adapter = LinuxAdapter()

        assert adapter.normalize_button(1) == CanonicalButton.LEFT
        assert adapter.normalize_button(2) == CanonicalButton.RIGHT
        assert adapter.normalize_button(8) == CanonicalButton.BACK
        assert adapter.normalize_button(32) == CanonicalButton.EXTRA1

    def test_normalize_modifiers(self) -> None:
        """Test modifier normalization on Linux."""
        from MouseMasterLib.platform_adapter import LinuxAdapter

        adapter = LinuxAdapter()

        assert adapter.normalize_modifiers(0x08000000) == {"alt"}
        assert adapter.normalize_modifiers(0x02000000 | 0x08000000) == {"shift", "alt"}


class TestPlatformAdapter:
    """Tests for PlatformAdapter base class."""

    def test_get_instance_returns_singleton(self) -> None:
        """Test that get_instance returns the same instance."""
        from MouseMasterLib.platform_adapter import PlatformAdapter

        # Reset first
        PlatformAdapter.reset_instance()

        instance1 = PlatformAdapter.get_instance()
        instance2 = PlatformAdapter.get_instance()

        assert instance1 is instance2

    def test_button_to_id(self) -> None:
        """Test converting canonical button to string ID."""
        from MouseMasterLib.platform_adapter import (
            CanonicalButton,
            PlatformAdapter,
        )

        PlatformAdapter.reset_instance()
        adapter = PlatformAdapter.get_instance()

        assert adapter.button_to_id(CanonicalButton.LEFT) == "left"
        assert adapter.button_to_id(CanonicalButton.BACK) == "back"
        assert adapter.button_to_id(CanonicalButton.UNKNOWN) == "unknown"

    def test_normalize_event(self, mock_mouse_event) -> None:
        """Test normalizing a mock mouse event."""
        from MouseMasterLib.platform_adapter import PlatformAdapter

        PlatformAdapter.reset_instance()
        adapter = PlatformAdapter.get_instance()

        event = mock_mouse_event(button=8, modifiers=0x02000000, x=100, y=200)
        normalized = adapter.normalize_event(event)

        assert normalized.button_id == "back"
        assert "shift" in normalized.modifiers
        assert normalized.x == 100
        assert normalized.y == 200
