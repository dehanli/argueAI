import unittest
from unittest.mock import MagicMock, patch
import json
from app import app

class TestEchoSystemAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.debate_manager')
    def test_start_debate(self, mock_debate_manager):
        response = self.app.post('/start_debate', 
                                 data=json.dumps({'topic': 'Test Topic'}),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'started')
        mock_debate_manager.start_debate.assert_called_with('Test Topic')

    @patch('app.debate_manager')
    @patch('app.fish_audio')
    def test_next_turn(self, mock_fish_audio, mock_debate_manager):
        # Setup mocks
        mock_debate_manager.next_turn.return_value = ('Lake Mendota', 'I am a lake.')
        mock_debate_manager.get_agent_voice_id.return_value = 'voice_123'
        mock_fish_audio.generate_speech.return_value = 'static/audio/test.mp3'

        response = self.app.post('/next_turn')
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['status'], 'ongoing')
        self.assertEqual(data['agent'], 'Lake Mendota')
        self.assertEqual(data['text'], 'I am a lake.')
        self.assertIn('/audio/', data['audio_url'])

    def test_start_debate_no_topic(self):
        response = self.app.post('/start_debate', 
                                 data=json.dumps({}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
