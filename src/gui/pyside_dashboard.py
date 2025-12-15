"""Modern PySide6 dashboard for OptimusPC."""

from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import QEasingCurve, QTimer, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QKeySequence, QPalette, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDockWidget,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.utils.hardware_monitor import HardwareMonitor
from src.utils.system_detector import SystemDetector


class StatusChip(QLabel):
    """Animated status chip used across the dashboard."""

    def __init__(self, label: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(label, parent)
        self.setMargin(8)
        self.setAlignment(Qt.AlignCenter)
        self.setProperty("status", "idle")
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(650)
        self._animation.setStartValue(QColor("#3d3d3d"))
        self._animation.setEndValue(QColor("#4b9bff"))
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._animation.valueChanged.connect(self._on_value_changed)
        self._apply_style("idle")

    def pulse(self, state: str) -> None:
        self._apply_style(state)
        self._animation.setDirection(QVariantAnimation.Forward if state != "idle" else QVariantAnimation.Backward)
        self._animation.start()

    def _apply_style(self, state: str) -> None:
        palette = {
            "idle": "rgba(255,255,255,0.08)",
            "ok": "rgba(34, 197, 94, 0.28)",
            "warn": "rgba(234, 179, 8, 0.28)",
            "critical": "rgba(248, 113, 113, 0.36)",
        }
        self.setStyleSheet(
            f"""
            QLabel {{
                background:{palette.get(state, palette['idle'])};
                color: #f5f5f5;
                border-radius: 14px;
                font-weight: 600;
                letter-spacing: 0.4px;
            }}
            """
        )
        self.setProperty("status", state)

    def _on_value_changed(self, color: QColor) -> None:
        self.setStyleSheet(self.styleSheet() + f"border: 1px solid {color.name()};")


class PresetToggle(QWidget):
    """Dashboard preset selector with per-mode interval."""

    def __init__(self, name: str, icon: str, interval_minutes: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)
        self.button = QPushButton(name)
        self.button.setIcon(self.style().standardIcon(getattr(QStyle, icon)))
        self.button.setCheckable(True)
        self.button.setAccessibleName(f"Activate {name} preset")
        self.button.setCursor(Qt.PointingHandCursor)

        self.interval = QSpinBox()
        self.interval.setRange(5, 240)
        self.interval.setValue(interval_minutes)
        self.interval.setSuffix(" min")
        self.interval.setAccessibleName(f"{name} preset refresh interval")

        layout.addWidget(self.button)
        layout.addStretch()
        layout.addWidget(QLabel("Interval"))
        layout.addWidget(self.interval)

    def is_checked(self) -> bool:
        return self.button.isChecked()

    def set_checked(self, value: bool) -> None:
        self.button.setChecked(value)


class InteractiveSystemMap(QGroupBox):
    """Hardware topology visualiser with live status overlays."""

    def __init__(self, monitor: HardwareMonitor, detector: SystemDetector, parent: Optional[QWidget] = None) -> None:
        super().__init__("System Map", parent)
        self.monitor = monitor
        self.detector = detector
        self.setAccessibleDescription("Displays CPU, memory, and storage topology with live status overlays.")

        layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Component", "Status"])
        self.tree.setRootIsDecorated(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tree)
        self.refresh_topology()

    def refresh_topology(self) -> None:
        self.tree.clear()
        cpu_info = self.detector.get_cpu_info()
        memory_info = self.detector.get_memory_info()
        disk_info = self.detector.get_disk_info()

        cpu_root = QTreeWidgetItem(["CPU", f"{cpu_info.get('physical_cores', 0)} physical / {cpu_info.get('total_cores', 0)} logical"])
        per_core = cpu_info.get("per_cpu_percent", [])
        for idx, usage in enumerate(per_core):
            QTreeWidgetItem(cpu_root, [f"Core {idx}", f"{usage:.1f}% load"])
        self.tree.addTopLevelItem(cpu_root)

        mem_root = QTreeWidgetItem([
            "Memory",
            f"{self._format_gb(memory_info.get('total', 0))} total / {memory_info.get('percent', 0)}% used",
        ])
        modules = memory_info.get("memory_modules", [])
        if modules:
            for idx, module in enumerate(modules):
                capacity = self._format_gb(module.get("capacity", 0))
                speed = module.get("speed", 0)
                QTreeWidgetItem(mem_root, [f"Channel {idx+1}", f"{capacity} @ {speed}MHz"])
        elif memory_info.get("memory_slots"):
            for idx in range(memory_info.get("memory_slots", 0)):
                QTreeWidgetItem(mem_root, [f"Channel {idx+1}", "available slot"])
        self.tree.addTopLevelItem(mem_root)

        storage_root = QTreeWidgetItem(["Storage", "Buses & partitions"])
        for partition in disk_info:
            label = f"{partition.get('mountpoint', '?')} ({partition.get('fstype', 'n/a')})"
            status = f"{self._format_gb(partition.get('total', 0))} / {partition.get('percent', 0):.1f}% used"
            QTreeWidgetItem(storage_root, [label, status])
        self.tree.addTopLevelItem(storage_root)
        self.tree.expandAll()

    def update_statuses(self, metrics: Dict) -> None:
        cpu_metrics = metrics.get("cpu", {})
        memory_metrics = metrics.get("memory", {})
        disk_metrics = metrics.get("disk", [])

        # CPU overlay
        cpu_root = self.tree.topLevelItem(0)
        if cpu_root and cpu_metrics:
            cpu_root.setText(1, f"{cpu_metrics.get('usage_percent', 0):.1f}% avg")
            for idx in range(cpu_root.childCount()):
                child = cpu_root.child(idx)
                if idx < len(cpu_metrics.get("per_cpu_usage", [])):
                    child.setText(1, f"{cpu_metrics['per_cpu_usage'][idx]:.1f}% load")

        # Memory overlay
        mem_root = self.tree.topLevelItem(1)
        if mem_root and memory_metrics:
            mem_root.setText(1, f"{self._format_gb(memory_metrics.get('total', 0))} / {memory_metrics.get('percent', 0)}%")

        # Disk overlay
        storage_root = self.tree.topLevelItem(2)
        if storage_root and disk_metrics:
            for idx, disk in enumerate(disk_metrics):
                if idx < storage_root.childCount():
                    storage_root.child(idx).setText(1, f"{self._format_gb(disk.get('total', 0))} / {disk.get('percent', 0):.1f}%")

    @staticmethod
    def _format_gb(value: float) -> str:
        if not value:
            return "0 GB"
        return f"{value / (1024 ** 3):.1f} GB"


class ModernDashboard(QMainWindow):
    """Modernized OptimusPC dashboard focused on accessibility and live insights."""

    def __init__(self, optimizer) -> None:
        super().__init__()
        self.optimizer = optimizer
        self.detector = SystemDetector()
        self.monitor = HardwareMonitor(self.detector)
        self.setWindowTitle("OptimusPC Dashboard")
        self.resize(1200, 760)
        self._configure_palette()
        self._configure_font()
        self._build_ui()
        self._connect_monitoring()
        self._connect_shortcuts()

    def _configure_palette(self) -> None:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(24, 24, 27, 240))
        palette.setColor(QPalette.WindowText, QColor("#f5f5f5"))
        palette.setColor(QPalette.Base, QColor(30, 30, 36, 240))
        palette.setColor(QPalette.AlternateBase, QColor(36, 36, 44, 240))
        palette.setColor(QPalette.Text, QColor("#f5f5f5"))
        palette.setColor(QPalette.Highlight, QColor(75, 155, 255))
        palette.setColor(QPalette.Button, QColor(42, 42, 52, 220))
        self.setPalette(palette)

    def _configure_font(self) -> None:
        font = QFont("Inter", 10)
        self.setFont(font)

    def _build_ui(self) -> None:
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(16, 12, 16, 12)
        central_layout.setSpacing(12)

        header = self._build_header()
        central_layout.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([520, 640])
        central_layout.addWidget(splitter)

        self.setCentralWidget(central)

    def _build_header(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 8)
        title = QLabel("OptimusPC Modern Dashboard")
        title.setAccessibleName("Window title")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")

        self.status_chip = StatusChip("Idle")
        self.status_chip.setAccessibleName("Optimization status chip")

        self.high_contrast_btn = QPushButton("High contrast")
        self.high_contrast_btn.setCheckable(True)
        self.high_contrast_btn.clicked.connect(self._toggle_contrast)
        self.high_contrast_btn.setAccessibleDescription("Toggle high contrast theme for better accessibility")

        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(8, 18)
        self.font_slider.setValue(self.font().pointSize())
        self.font_slider.setAccessibleName("Font scaling slider")
        self.font_slider.valueChanged.connect(self._update_font_scale)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(QLabel("Font size"))
        layout.addWidget(self.font_slider)
        layout.addWidget(self.high_contrast_btn)
        layout.addWidget(self.status_chip)
        return container

    def _build_left_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        presets_box = QGroupBox("Dashboard Presets")
        presets_layout = QVBoxLayout(presets_box)
        self.presets: List[PresetToggle] = [
            PresetToggle("Gamer", "SP_TitleBarMenuButtonHover", 30),
            PresetToggle("Creator", "SP_FileDialogDetailedView", 45),
            PresetToggle("Office", "SP_FileDialogListView", 60),
        ]
        self.preset_group = QButtonGroup(self)
        for preset in self.presets:
            self.preset_group.addButton(preset.button)
            presets_layout.addWidget(preset)
        presets_layout.addStretch()
        layout.addWidget(presets_box)

        controls = QGroupBox("Quick Controls")
        controls_layout = QGridLayout(controls)
        self.monitor_toggle = QPushButton("Start Live Monitoring")
        self.monitor_toggle.setCheckable(True)
        self.monitor_toggle.clicked.connect(self._toggle_monitoring)
        self.monitor_toggle.setAccessibleName("Toggle live monitoring")

        self.optimize_button = QPushButton("Run Optimization")
        self.optimize_button.clicked.connect(self._run_optimization)
        self.optimize_button.setAccessibleDescription("Start selected optimization tasks")

        self.accessibility_hint = QLabel("Press Alt+H for help, Alt+G/C/O for presets.")
        self.accessibility_hint.setAccessibleName("Keyboard shortcut hint")

        controls_layout.addWidget(self.monitor_toggle, 0, 0, 1, 2)
        controls_layout.addWidget(self.optimize_button, 1, 0, 1, 2)
        controls_layout.addWidget(self.accessibility_hint, 2, 0, 1, 2)
        layout.addWidget(controls)
        layout.addStretch()
        return container

    def _build_right_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        self.system_map = InteractiveSystemMap(self.monitor, self.detector)

        timeline_dock = QDockWidget("Activity", self)
        timeline_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.timeline = QListWidget()
        self.timeline.setAccessibleName("Live activity feed")
        timeline_dock.setWidget(self.timeline)

        stack = QStackedWidget()
        stack.addWidget(self.system_map)

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(stack)
        right_splitter.addWidget(timeline_dock)
        right_splitter.setSizes([520, 240])

        layout.addWidget(right_splitter)
        return container

    def _connect_monitoring(self) -> None:
        self.monitor.add_callback("cpu_update", self._on_metrics)
        self.monitor.add_callback("memory_update", self._on_metrics)
        self.monitor.add_callback("disk_update", self._on_metrics)
        refresh_timer = QTimer(self)
        refresh_timer.timeout.connect(self._refresh_topology)
        refresh_timer.start(120000)  # refresh topology every 2 minutes
        self._heartbeat = QTimer(self)
        self._heartbeat.timeout.connect(self._pulse_status)
        self._heartbeat.start(1800)

    def _connect_shortcuts(self) -> None:
        QShortcut(QKeySequence("Alt+G"), self, activated=lambda: self._select_preset(0))
        QShortcut(QKeySequence("Alt+C"), self, activated=lambda: self._select_preset(1))
        QShortcut(QKeySequence("Alt+O"), self, activated=lambda: self._select_preset(2))
        QShortcut(QKeySequence("Alt+H"), self, activated=self._show_shortcuts_help)
        QShortcut(QKeySequence("Ctrl+Plus"), self, activated=lambda: self.font_slider.setValue(min(18, self.font_slider.value() + 1)))
        QShortcut(QKeySequence("Ctrl+Minus"), self, activated=lambda: self.font_slider.setValue(max(8, self.font_slider.value() - 1)))

    def _select_preset(self, index: int) -> None:
        if index < len(self.presets):
            for idx, preset in enumerate(self.presets):
                preset.set_checked(idx == index)
            self._log_activity(f"Preset activated: {self.presets[index].button.text()}")

    def _refresh_topology(self) -> None:
        self.system_map.refresh_topology()

    def _pulse_status(self) -> None:
        state = self.status_chip.property("status") or "idle"
        self.status_chip.pulse(state)

    def _toggle_monitoring(self) -> None:
        if self.monitor_toggle.isChecked():
            self.monitor.start_monitoring(update_interval=1)
            self.monitor_toggle.setText("Stop Live Monitoring")
            self.status_chip.pulse("ok")
            self._log_activity("Live monitoring started")
        else:
            self.monitor.stop_monitoring()
            self.monitor_toggle.setText("Start Live Monitoring")
            self.status_chip.pulse("idle")
            self._log_activity("Live monitoring stopped")

    def _run_optimization(self) -> None:
        try:
            self.optimizer.run_optimization_tasks()
            self.status_chip.pulse("ok")
            self._log_activity("Optimization completed successfully")
        except Exception as exc:  # pragma: no cover - runtime safeguard
            self.status_chip.pulse("critical")
            self._log_activity(f"Optimization failed: {exc}")

    def _on_metrics(self, _data: Dict) -> None:
        metrics = self.monitor._get_current_metrics()
        self.system_map.update_statuses(metrics)
        cpu_usage = metrics.get("cpu", {}).get("usage_percent", 0)
        memory_usage = metrics.get("memory", {}).get("percent", 0)
        dominant = max(cpu_usage, memory_usage)
        if dominant < 60:
            state = "ok"
        elif dominant < 85:
            state = "warn"
        else:
            state = "critical"
        self.status_chip.pulse(state)
        self._log_activity(f"CPU {cpu_usage:.1f}% | Memory {memory_usage:.1f}%")

    def _toggle_contrast(self) -> None:
        if self.high_contrast_btn.isChecked():
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(12, 12, 12))
            palette.setColor(QPalette.Base, QColor(24, 24, 24))
            palette.setColor(QPalette.Text, QColor("#ffffff"))
            palette.setColor(QPalette.Highlight, QColor("#00eaff"))
            self.setPalette(palette)
        else:
            self._configure_palette()

    def _update_font_scale(self, value: int) -> None:
        new_font = QFont(self.font().family(), value)
        QApplication.instance().setFont(new_font)
        self._log_activity(f"Font size set to {value}")

    def _log_activity(self, text: str) -> None:
        item = QListWidgetItem(text)
        self.timeline.insertItem(0, item)

    def _show_shortcuts_help(self) -> None:
        help_lines = [
            "Alt+G / Alt+C / Alt+O - Switch presets",
            "Ctrl++ / Ctrl+- - Adjust font size",
            "Alt+H - Shortcut help",
        ]
        self._log_activity(" | ".join(help_lines))

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.monitor.stop_monitoring()
        super().closeEvent(event)


def launch_modern_dashboard(optimizer) -> None:
    """Entry point to launch the PySide6 dashboard."""
    app = QApplication.instance() or QApplication([])
    window = ModernDashboard(optimizer)
    window.show()
    app.exec()
