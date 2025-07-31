import unittest
from copy import deepcopy
from YouTubeApis import YouTubeApis, DEFAULT_STATE

class TestYouTubeApis(unittest.TestCase):
    def setUp(self):
        """Set up a fresh YouTubeApis instance for each test."""
        self.youtube_api = YouTubeApis()
        # Ensure a clean state for each test by explicitly loading the default scenario
        self.youtube_api._load_scenario(deepcopy(DEFAULT_STATE))

    # Unit Tests for Individual Audio/Caption Related Functions

    def test_youtube_captions_insert_success(self):
        """Test inserting a new caption track successfully."""
        # Ensure a video exists in the current channel for caption insertion
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        initial_caption_count = len(self.youtube_api.channels[self.youtube_api.current_channel].get("captions", {}))

        result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id=video_id,
            language="es",
            name="Spanish Captions"
        )
        self.assertTrue(result["success"])
        self.assertIn("caption_id", result)
        self.assertEqual(result["video_id"], video_id)
        self.assertEqual(result["language"], "es")

        # Verify the caption was added to the channel's captions
        updated_captions = self.youtube_api.channels[self.youtube_api.current_channel]["captions"]
        self.assertEqual(len(updated_captions), initial_caption_count + 1)
        new_caption_id = result["caption_id"]
        self.assertIn(new_caption_id, updated_captions)
        self.assertEqual(updated_captions[new_caption_id]["language"], "es")
        self.assertEqual(updated_captions[new_caption_id]["name"], "Spanish Captions")

    def test_youtube_captions_insert_no_current_channel(self):
        """Test inserting caption without a current channel set."""
        self.youtube_api.current_channel = None
        result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id="videoABC",
            language="fr"
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No current channel set.")

    def test_youtube_captions_insert_video_not_found(self):
        """Test inserting caption for a video that doesn't exist in the current channel."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id="nonExistentVideo",
            language="fr"
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Video not found in current channel.")

    def test_youtube_captions_list_success(self):
        """Test listing caption tracks for a video."""
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        result = self.youtube_api.youtube_captions_list(part="snippet", video_id=video_id)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)
        self.assertGreater(len(result["items"]), 0)
        self.assertEqual(result["items"][0]["snippet"]["videoId"], video_id)
        self.assertEqual(result["items"][0]["snippet"]["language"], "en")

    def test_youtube_captions_list_no_current_channel(self):
        """Test listing captions without a current channel set."""
        self.youtube_api.current_channel = None
        result = self.youtube_api.youtube_captions_list(part="snippet", video_id="videoABC")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No current channel set.")

    def test_youtube_captions_list_no_captions_for_video(self):
        """Test listing captions for a video with no captions."""
        self.youtube_api.current_channel = "channel2@example.com" # channel2 has no captions
        result = self.youtube_api.youtube_captions_list(part="snippet", video_id="someVideo")
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 0)

    def test_youtube_captions_update_success(self):
        """Test updating an existing caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        caption_id = "caption1"
        new_name = "Updated English Captions"
        result = self.youtube_api.youtube_captions_update(
            part="snippet",
            caption_id=caption_id,
            is_draft=True,
            file_path="/new/path/to/captions1.vtt"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["caption_id"], caption_id)
        self.assertTrue(self.youtube_api.channels[self.youtube_api.current_channel]["captions"][caption_id]["is_draft"])
        self.assertEqual(self.youtube_api.channels[self.youtube_api.current_channel]["captions"][caption_id]["file_path"], "/new/path/to/captions1.vtt")

    def test_youtube_captions_update_not_found(self):
        """Test updating a non-existent caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_update(
            part="snippet",
            caption_id="nonExistentCaption",
            is_draft=True
        )
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Caption track not found.")

    def test_youtube_captions_download_success(self):
        """Test downloading a caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        caption_id = "caption1"
        result = self.youtube_api.youtube_captions_download(id=caption_id, tfmt="srt")
        self.assertTrue(result["success"])
        self.assertEqual(result["caption_id"], caption_id)
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], str)
        self.assertIn("dummy caption", result["content"])

    def test_youtube_captions_download_not_found(self):
        """Test downloading a non-existent caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_download(id="nonExistentCaption")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Caption track not found.")

    def test_youtube_captions_delete_success(self):
        """Test deleting a caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        caption_id_to_delete = "caption1"
        initial_caption_count = len(self.youtube_api.channels[self.youtube_api.current_channel].get("captions", {}))

        result = self.youtube_api.youtube_captions_delete(id=caption_id_to_delete)
        self.assertTrue(result["success"])
        self.assertEqual(result["deleted_caption_id"], caption_id_to_delete)
        self.assertEqual(len(self.youtube_api.channels[self.youtube_api.current_channel]["captions"]), initial_caption_count - 1)
        self.assertNotIn(caption_id_to_delete, self.youtube_api.channels[self.youtube_api.current_channel]["captions"])

    def test_youtube_captions_delete_not_found(self):
        """Test deleting a non-existent caption track."""
        self.youtube_api.current_channel = "channel1@example.com"
        result = self.youtube_api.youtube_captions_delete(id="nonExistentCaption")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Caption track not found.")

    def test_youtube_videos_rate_success(self):
        """Test rating a video."""
        video_id = "videoABC"
        result = self.youtube_api.youtube_videos_rate(id=video_id, rating="like")
        self.assertTrue(result["success"])
        self.assertEqual(result["video_id"], video_id)
        self.assertEqual(result["rating"], "like")

    def test_youtube_videos_rate_invalid_rating(self):
        """Test rating a video with an invalid rating."""
        video_id = "videoABC"
        result = self.youtube_api.youtube_videos_rate(id=video_id, rating="invalid")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid rating. Must be 'like', 'dislike', or 'none'.")

    def test_youtube_videos_get_rating_success(self):
        """Test getting a video's rating."""
        video_id = "videoABC"
        result = self.youtube_api.youtube_videos_get_rating(id=video_id)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["videoId"], video_id)
        self.assertEqual(result["items"][0]["rating"], "none") # Dummy backend always returns 'none'

    # Combined Functionality Tests

    def test_caption_workflow_insert_list_update_delete(self):
        """
        Combined test: Insert a caption, list it, update it, and then delete it.
        """
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        initial_caption_count = len(self.youtube_api.channels[self.youtube_api.current_channel].get("captions", {}))

        # 1. Insert a caption
        insert_result = self.youtube_api.youtube_captions_insert(
            part="snippet",
            video_id=video_id,
            language="fr",
            name="French Captions for Workflow Test"
        )
        self.assertTrue(insert_result["success"])
        new_caption_id = insert_result["caption_id"]
        self.assertEqual(len(self.youtube_api.channels[self.youtube_api.current_channel]["captions"]), initial_caption_count + 1)

        # 2. List captions and verify the new caption is present
        list_result_after_insert = self.youtube_api.youtube_captions_list(part="snippet", video_id=video_id)
        self.assertTrue(any(item["id"] == new_caption_id for item in list_result_after_insert["items"]))

        # 3. Update the caption
        update_result = self.youtube_api.youtube_captions_update(
            part="snippet",
            caption_id=new_caption_id,
            is_draft=True
        )
        self.assertTrue(update_result["success"])
        self.assertTrue(self.youtube_api.channels[self.youtube_api.current_channel]["captions"][new_caption_id]["is_draft"])

        # 4. Delete the caption
        delete_result = self.youtube_api.youtube_captions_delete(id=new_caption_id)
        self.assertTrue(delete_result["success"])
        self.assertEqual(self.youtube_api.channels[self.youtube_api.current_channel]["captions"].get(new_caption_id), None)
        self.assertEqual(len(self.youtube_api.channels[self.youtube_api.current_channel]["captions"]), initial_caption_count)

        # 5. Verify it's no longer in the list
        list_result_after_delete = self.youtube_api.youtube_captions_list(part="snippet", video_id=video_id)
        self.assertFalse(any(item["id"] == new_caption_id for item in list_result_after_delete["items"]))

    def test_video_rating_and_retrieval(self):
        """
        Combined test: Rate a video and then retrieve its rating.
        Note: Dummy backend always returns 'none' for get_rating.
        """
        video_id = "videoDEF" # Use a different video
        
        # 1. Rate the video as 'like'
        rate_result_like = self.youtube_api.youtube_videos_rate(id=video_id, rating="like")
        self.assertTrue(rate_result_like["success"])
        self.assertEqual(rate_result_like["rating"], "like")

        # 2. Retrieve the rating (will still be 'none' due to dummy backend)
        get_rating_result_like = self.youtube_api.youtube_videos_get_rating(id=video_id)
        self.assertIn("items", get_rating_result_like)
        self.assertEqual(get_rating_result_like["items"][0]["rating"], "none")

        # 3. Rate the video as 'dislike'
        rate_result_dislike = self.youtube_api.youtube_videos_rate(id=video_id, rating="dislike")
        self.assertTrue(rate_result_dislike["success"])
        self.assertEqual(rate_result_dislike["rating"], "dislike")

        # 4. Retrieve the rating again (will still be 'none' due to dummy backend)
        get_rating_result_dislike = self.youtube_api.youtube_videos_get_rating(id=video_id)
        self.assertIn("items", get_rating_result_dislike)
        self.assertEqual(get_rating_result_dislike["items"][0]["rating"], "none")

    def test_comment_thread_creation_and_reply(self):
        """
        Combined test: Create a comment thread and then add a reply to it.
        """
        self.youtube_api.current_channel = "channel1@example.com"
        video_id = "videoABC"
        initial_thread_count = len(self.youtube_api.comment_threads)
        initial_comment_count = len(self.youtube_api.comments)

        # 1. Create a new comment thread
        thread_text = "What are your thoughts on this video?"
        create_thread_result = self.youtube_api.youtube_comment_threads_insert(
            part="snippet",
            video_id=video_id,
            text_original=thread_text
        )
        self.assertTrue(create_thread_result["success"])
        new_thread_id = create_thread_result["thread_id"]
        self.assertEqual(len(self.youtube_api.comment_threads), initial_thread_count + 1)
        self.assertEqual(self.youtube_api.comment_threads[new_thread_id]["text_original"], thread_text)

        # 2. Add a reply to the newly created thread
        reply_text = "I think it's great!"
        create_reply_result = self.youtube_api.youtube_comments_insert(
            part="snippet",
            parent_id=new_thread_id,
            text_original=reply_text
        )
        self.assertTrue(create_reply_result["success"])
        new_reply_id = create_reply_result["comment_id"]
        self.assertEqual(len(self.youtube_api.comments), initial_comment_count + 1)
        self.assertEqual(self.youtube_api.comments[new_reply_id]["text_original"], reply_text)
        self.assertIn(new_reply_id, self.youtube_api.comment_threads[new_thread_id]["replies"])

        # 3. List comment threads and verify the reply count
        list_threads_result = self.youtube_api.youtube_comment_threads_list(
            part="snippet,replies",
            video_id=video_id,
            id=new_thread_id
        )
        self.assertEqual(len(list_threads_result["items"]), 1)
        retrieved_thread = list_threads_result["items"][0]
        self.assertEqual(retrieved_thread["snippet"]["totalReplyCount"], 1)
        self.assertEqual(retrieved_thread["replies"]["comments"][0]["id"], new_reply_id)

        # 4. Delete the thread (should also delete the reply in this dummy implementation)
        delete_thread_result = self.youtube_api.youtube_comments_delete(id=new_thread_id)
        self.assertTrue(delete_thread_result["success"])
        self.assertNotIn(new_thread_id, self.youtube_api.comment_threads)
        self.assertNotIn(new_reply_id, self.youtube_api.comments) # Verify reply is also gone

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
