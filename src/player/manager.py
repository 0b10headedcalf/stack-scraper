# """
# Video playback manager.
# Handles loading videos from collections and launching the player.
# """
#
# import json
# from pathlib import Path
# from typing import List, Dict, Optional
# from src.player.video_player import VideoPlayerWindow
#
#
# class VideoPlaybackManager:
#     """Manages video queues and playback sessions."""
#
#     def __init__(self, collection_path: str):
#         """
#         Args:
#             collection_path: Path to a scraped collection directory
#         """
#         self.collection_path = Path(collection_path)
#         self.watched_log = self.collection_path / ".watched.json"
#         self.watched_videos = self._load_watched_log()
#
#     def _load_watched_log(self) -> Dict[str, bool]:
#         """Load the watched status log."""
#         if self.watched_log.exists():
#             with open(self.watched_log) as f:
#                 return json.load(f)
#         return {}
#
#     def _save_watched_log(self):
#         """Save the watched status log."""
#         with open(self.watched_log, "w") as f:
#             json.dump(self.watched_videos, f, indent=2)
#
#     def get_videos(self, unwatched_only: bool = False) -> List[str]:
#         """
#         Get list of video files in collection.
#
#         Args:
#             unwatched_only: If True, only return videos not yet watched
#
#         Returns:
#             List of absolute paths to video files
#         """
#         video_extensions = {".mp4", ".mkv", ".webm", ".mov", ".avi"}
#         videos = [
#             str(f) for f in self.collection_path.rglob("*")
#             if f.is_file() and f.suffix.lower() in video_extensions
#         ]
#
#         if unwatched_only:
#             return [
#                 v for v in videos
#                 if Path(v).name not in self.watched_videos or not self.watched_videos[Path(v).name]
#             ]
#
#         return sorted(videos)
#
#     def mark_watched(self, video_path: str):
#         """Mark a video as watched."""
#         video_name = Path(video_path).name
#         self.watched_videos[video_name] = True
#         self._save_watched_log()
#
#     def launch_player(self, unwatched_only: bool = False):
#         """
#         Launch the video player with videos from this collection.
#
#         Args:
#             unwatched_only: If True, only include unwatched videos
#
#         Returns:
#             VideoPlayerWindow instance
#         """
#         videos = self.get_videos(unwatched_only=unwatched_only)
#
#         if not videos:
#             raise ValueError(
#                 f"No videos found in {self.collection_path}"
#                 + (" (all watched)" if unwatched_only else "")
#             )
#
#         # TODO: Implement the callback to handle what happens when a video finishes
#         # Should you mark it as watched? Show progress? Add to a completion log?
#         def on_video_finished(index: int):
#             # This is where you'll define the business logic for video completion
#             # Right now it just moves to the next video automatically
#             pass
#
#         player = VideoPlayerWindow(videos, on_video_finished=on_video_finished)
#         return player
