
import os
import logging
import json

import click
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)

try:
    from . import (
        assistant_helpers,
        browser_helpers,
    )
except (SystemError, ImportError):
    import assistant_helpers
    import browser_helpers


ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5
PLAYING = embedded_assistant_pb2.ScreenOutConfig.PLAYING
DEVICE_MODEL_ID='unity-chatbot-24f7a'
DEVICE_ID='unity-chatbot-24f7a-unity-chatbot-c3ln9f'


class SampleTextAssistant(object):


    def __init__(self,channel):
        self.language_code = 'en-US'
        self.device_model_id = 'unity-chatbot-24f7a'
        self.device_id = 'unity-chatbot-24f7a-unity-chatbot-c3ln9f'
        self.conversation_state = None
        # Force reset of first conversation.
        self.is_new_conversation = True
        self.display = False
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
            channel
        )
        self.deadline = 60 * 3 + 5

    def __enter__(self):
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            return False

    def assist(self, text_query):
        """Send a text request to the Assistant and playback the response.
        """
        def iter_assist_requests():
            config = embedded_assistant_pb2.AssistConfig(
                audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                    encoding='LINEAR16',
                    sample_rate_hertz=16000,
                    volume_percentage=0,
                ),
                dialog_state_in=embedded_assistant_pb2.DialogStateIn(
                    language_code=self.language_code,
                    conversation_state=self.conversation_state,
                    is_new_conversation=self.is_new_conversation,
                ),
                device_config=embedded_assistant_pb2.DeviceConfig(
                    device_id=self.device_id,
                    device_model_id=self.device_model_id,
                ),
                text_query=text_query,
            )
            # Continue current conversation with later requests.
            self.is_new_conversation = False
            if self.display:
                config.screen_out_config.screen_mode = PLAYING
            req = embedded_assistant_pb2.AssistRequest(config=config)
            assistant_helpers.log_assist_request_without_audio(req)
            yield req

        text_response = None
        html_response = None
        for resp in self.assistant.Assist(iter_assist_requests(),
                                          self.deadline):
            assistant_helpers.log_assist_response_without_audio(resp)
            if resp.screen_out.data:
                html_response = resp.screen_out.data
            if resp.dialog_state_out.conversation_state:
                conversation_state = resp.dialog_state_out.conversation_state
                self.conversation_state = conversation_state
            if resp.dialog_state_out.supplemental_display_text:
                text_response = resp.dialog_state_out.supplemental_display_text
        return text_response, html_response






def GetAssistantObject():
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'credentials.json')

    # Load OAuth 2.0 credentials.
    try:
        with open(file_path, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        print("Exception aaya hai")
        return

    # Create an authorized gRPC channel.
    
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(credentials, http_request, ASSISTANT_API_ENDPOINT)
    assistant = SampleTextAssistant(grpc_channel)
    return assistant
    


def GetResponseForQuery(assistant,query): 
  response_text, response_html = assistant.assist(text_query=query)
  if response_text:
    return response_text
  else:
    return "Sorry, Didn't get You! Try Different Queries!"  

    

