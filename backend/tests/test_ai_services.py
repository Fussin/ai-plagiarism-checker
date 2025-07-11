import unittest
from unittest.mock import patch, AsyncMock # AsyncMock for async methods

from fastapi import HTTPException

# Module to test
from backend.services import ai_services
from backend.config import settings

class TestAIServices(unittest.IsolatedAsyncioTestCase): # Use IsolatedAsyncioTestCase for async def tests

    def setUp(self):
        # Store original client and settings, then mock them
        self.original_async_client = ai_services.async_client
        self.original_api_key = settings.OPENAI_API_KEY

        # Ensure a mock client is set up for tests, even if API key isn't normally set
        settings.OPENAI_API_KEY = "fake_test_key" # Ensure client attempts initialization
        ai_services.async_client = AsyncMock() # Mock the client instance

    def tearDown(self):
        # Restore original client and settings
        ai_services.async_client = self.original_async_client
        settings.OPENAI_API_KEY = self.original_api_key
        # If ai_services re-initializes its client on import, this might need more careful handling
        # or a dedicated mock setup for the module's client.
        # For now, direct patching of the instance is assumed.
        if settings.OPENAI_API_KEY: # Re-initialize if there was a key
             ai_services.async_client = ai_services.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            ai_services.async_client = None


    async def test_humanize_text_with_gpt_async_success(self):
        mock_completion_choice = AsyncMock()
        mock_completion_choice.message.content = "This is a beautifully rephrased human text."

        mock_completion_response = AsyncMock()
        mock_completion_response.choices = [mock_completion_choice]

        # Configure the mock client's method
        ai_services.async_client.chat.completions.create = AsyncMock(return_value=mock_completion_response)

        original_text = "Original text for humanization."
        humanized = await ai_services.humanize_text_with_gpt_async(original_text)

        self.assertEqual(humanized, "This is a beautifully rephrased human text.")
        ai_services.async_client.chat.completions.create.assert_called_once()
        call_args = ai_services.async_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], "gpt-4-turbo") # Check new default model
        self.assertIn(original_text, call_args.kwargs['messages'][1]['content'])


    async def test_humanize_text_with_gpt_async_custom_model(self):
        mock_completion_choice = AsyncMock()
        mock_completion_choice.message.content = "Custom model rephrased text."
        mock_completion_response = AsyncMock()
        mock_completion_response.choices = [mock_completion_choice]
        ai_services.async_client.chat.completions.create = AsyncMock(return_value=mock_completion_response)

        original_text = "Original text for custom model."
        custom_model_name = "gpt-3.5-turbo-instruct" # Example of specifying a different model
        humanized = await ai_services.humanize_text_with_gpt_async(original_text, model=custom_model_name)

        self.assertEqual(humanized, "Custom model rephrased text.")
        ai_services.async_client.chat.completions.create.assert_called_once()
        call_args = ai_services.async_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], custom_model_name)


    async def test_humanize_text_with_gpt_async_empty_input(self):
        # No need to mock client here as it should return early
        result = await ai_services.humanize_text_with_gpt_async("   ")
        self.assertEqual(result, "   ")

    async def test_humanize_text_with_gpt_async_api_error(self):
        # Simulate an APIError from OpenAI
        # The actual APIError structure might be more complex, this is a simplified mock
        mock_api_error = ai_services.APIError(message="Test API Error", request=None, body={"message": "Test API Error Body"})
        ai_services.async_client.chat.completions.create = AsyncMock(side_effect=mock_api_error)

        with self.assertRaises(HTTPException) as cm:
            await ai_services.humanize_text_with_gpt_async("Some text.")
        self.assertEqual(cm.exception.status_code, 502) # HTTP_502_BAD_GATEWAY
        self.assertIn("OpenAI API error: Test API Error", str(cm.exception.detail))

    async def test_humanize_text_with_gpt_async_timeout_error(self):
        ai_services.async_client.chat.completions.create = AsyncMock(side_effect=ai_services.APITimeoutError())

        with self.assertRaises(HTTPException) as cm:
            await ai_services.humanize_text_with_gpt_async("Some text.")
        self.assertEqual(cm.exception.status_code, 504) # HTTP_504_GATEWAY_TIMEOUT
        self.assertIn("OpenAI API request timed out.", str(cm.exception.detail))

    async def test_humanize_text_with_gpt_async_rate_limit_error(self):
        # RateLimitError needs a response for its constructor typically
        mock_response = AsyncMock() # Mock a response object
        mock_response.status_code = 429
        # A more complete mock_response might be needed if RateLimitError constructor uses it extensively

        ai_services.async_client.chat.completions.create = AsyncMock(
            side_effect=ai_services.RateLimitError(message="Rate limit exceeded.", response=mock_response, body=None)
        )

        with self.assertRaises(HTTPException) as cm:
            await ai_services.humanize_text_with_gpt_async("Some text.")
        self.assertEqual(cm.exception.status_code, 429) # HTTP_429_TOO_MANY_REQUESTS
        self.assertIn("Rate limit exceeded with OpenAI API.", str(cm.exception.detail))

    @patch('backend.services.ai_services.async_client', None) # More direct way to mock client as None
    async def test_humanize_text_no_client(self):
         with self.assertRaises(HTTPException) as cm:
            await ai_services.humanize_text_with_gpt_async("Some text.")
         self.assertEqual(cm.exception.status_code, 503)
         self.assertIn("Text humanization service is not available.", str(cm.exception.detail))


if __name__ == '__main__':
    unittest.main()
