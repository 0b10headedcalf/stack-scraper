# """
# Cross-platform video player window with lockdown behavior.
# Prevents window closing but allows other interactions.
# """
#
# import vlc
# import sys
# from pathlib import Path
# from typing import Optional, List, Callable
# from PyQt6.QtWidgets import (
#     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
#     QPushButton, QLabel, QSlider
# )
# from PyQt6.QtCore import Qt, QTimer, QUrl
# from PyQt6.QtGui import QIcon
# from PyQt6.QtMultimediaWidgets import QVideoWidget
# from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
#
#
# class VideoPlayerWindow(QMainWindow):
#     """
#     Locked video player window.
#     - Cannot be closed by user (close button disabled, Ctrl+W ignored)
#     - Supports play/pause/skip controls
#     - Shows current video info and queue status
#     """
#
#     def __init__(self, video_paths: List[str], on_video_finished: Optional[Callable] = None):
#         """
#         Args:
#             video_paths: List of local file paths to videos
#             on_video_finished: Callback when a video finishes playing
#         """
#         super().__init__()
#         self.video_paths = [Path(p) for p in video_paths]
#         self.current_index = 0
#         self.on_video_finished = on_video_finished
#         self.is_playing = False
#
#         # VLC instance
#         self.vlc_instance = vlc.Instance()
#         self.media_list_player = self.vlc_instance.media_list_player_new()
#         self.media_list = self.vlc_instance.media_list_new()
#
#         # Populate media list
#         for video_path in self.video_paths:
#             media = self.vlc_instance.media_new(str(video_path))
#             self.media_list.add_media(media)
#
#         self.media_list_player.set_media_list(self.media_list)
#
#         self.setup_ui()
#         self.setWindowTitle("Video Lockdown Player")
#         self.setGeometry(100, 100, 1024, 720)
#
#         # Timer to update UI
#         self.update_timer = QTimer()
#         self.update_timer.timeout.connect(self.update_ui)
#         self.update_timer.start(500)
#
#     def setup_ui(self):
#         """Build the UI with video display and controls."""
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#
#         layout = QVBoxLayout()
#
#         # Video display (VLC widget)
#         self.video_widget = QWidget()
#         self.video_layout = QVBoxLayout()
#         self.video_widget.setLayout(self.video_layout)
#         layout.addWidget(self.video_widget)
#
#         # Info label
#         self.info_label = QLabel()
#         self.update_info_label()
#         layout.addWidget(self.info_label)
#
#         # Controls layout
#         controls_layout = QHBoxLayout()
#
#         self.play_btn = QPushButton("Play")
#         self.play_btn.clicked.connect(self.toggle_play)
#         controls_layout.addWidget(self.play_btn)
#
#         self.skip_btn = QPushButton("Next Video")
#         self.skip_btn.clicked.connect(self.next_video)
#         controls_layout.addWidget(self.skip_btn)
#
#         # Progress slider
#         self.progress_slider = QSlider(Qt.Orientation.Horizontal)
#         self.progress_slider.setMinimum(0)
#         self.progress_slider.sliderMoved.connect(self.seek)
#         controls_layout.addWidget(self.progress_slider)
#
#         # Time label
#         self.time_label = QLabel("0:00 / 0:00")
#         controls_layout.addWidget(self.time_label)
#
#         layout.addLayout(controls_layout)
#
#         central_widget.setLayout(layout)
#
#     def closeEvent(self, event):
#         """Override close event to prevent window closing."""
#         event.ignore()  # Ignore the close attempt
#         # Optionally show a message or do nothing silently
#
#     def keyPressEvent(self, event):
#         """Override key press to ignore Ctrl+W and other close shortcuts."""
#         if event.key() == Qt.Key.Key_W and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
#             event.ignore()
#             return
#         super().keyPressEvent(event)
#
#     def play_current_video(self):
#         """Start playing the current video."""
#         if self.current_index < len(self.video_paths):
#             self.media_list_player.play_item_at_index(self.current_index)
#             self.is_playing = True
#             self.play_btn.setText("Pause")
#             self.update_info_label()
#
#     def toggle_play(self):
#         """Toggle play/pause."""
#         if self.is_playing:
#             self.media_list_player.pause()
#             self.play_btn.setText("Play")
#             self.is_playing = False
#         else:
#             self.media_list_player.play()
#             self.play_btn.setText("Pause")
#             self.is_playing = True
#
#     def next_video(self):
#         """Move to next video in queue."""
#         if self.current_index < len(self.video_paths) - 1:
#             self.current_index += 1
#             self.play_current_video()
#
#     def seek(self, position):
#         """Seek to position in current video."""
#         media = self.media_list.item_at_index(self.current_index)
#         if media:
#             duration = self.media_list_player.get_media_player().get_length()
#             if duration > 0:
#                 self.media_list_player.get_media_player().set_time(
#                     int(position * duration / 1000)
#                 )
#
#     def update_ui(self):
#         """Update UI elements based on playback state."""
#         player = self.media_list_player.get_media_player()
#
#         # Update progress bar
#         length = player.get_length()
#         if length > 0:
#             current = player.get_time()
#             self.progress_slider.blockSignals(True)
#             self.progress_slider.setValue(int(current / length * 1000))
#             self.progress_slider.blockSignals(False)
#
#             # Update time label
#             current_min = current // 60000
#             current_sec = (current % 60000) // 1000
#             total_min = length // 60000
#             total_sec = (length % 60000) // 1000
#             self.time_label.setText(
#                 f"{int(current_min)}:{int(current_sec):02d} / {int(total_min)}:{int(total_sec):02d}"
#             )
#
#         # Check if video finished
#         if player.get_state() == vlc.State.Ended:
#             if self.on_video_finished:
#                 self.on_video_finished(self.current_index)
#             self.next_video()
#
#     def update_info_label(self):
#         """Update info label with current video info."""
#         if self.current_index < len(self.video_paths):
#             video_name = self.video_paths[self.current_index].name
#             self.info_label.setText(
#                 f"Playing {self.current_index + 1}/{len(self.video_paths)}: {video_name}"
#             )
#
#     def get_vlc_widget(self):
#         """Get VLC display widget (platform-specific)."""
#         # This attaches VLC output to our video widget
#         # Platform-specific implementation
#         if sys.platform == "linux":
#             self.media_list_player.get_media_player().set_xwindow(
#                 int(self.video_widget.winId())
#             )
#         elif sys.platform == "win32":
#             self.media_list_player.get_media_player().set_hwnd(
#                 int(self.video_widget.winId())
#             )
#         elif sys.platform == "darwin":
#             self.media_list_player.get_media_player().set_nsobject(
#                 int(self.video_widget.winId())
#             )
#
#     def closeApplication(self):
#         """Clean shutdown (only called programmatically)."""
#         self.media_list_player.stop()
#         super().closeEvent(None)
