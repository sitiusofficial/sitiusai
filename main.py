import streamlit as st
import requests

# Set up page layout
st.set_page_config(page_title="Chatbot App", page_icon=":robot_face:", layout="wide")

# Create list of available AI models
AI_MODELS = {
    'ben_turbo': "spitfire4794/ben-2-turbo",
    'cucumber': "spitfire4794/cucumber-1",
    'ash': "spitfire4794/ash-1",
    'kim': "spitfire4794/kim-1",
    'ben_ultra': "spitfire4794/ben-ultra",
}

# Define conversation history data structure
model_history = {}
for model_name in AI_MODELS.values():
    model_history[model_name] = {'past_user_inputs': [], 'generated_responses': []}

def payloadify(content, model_name):
    """
    makes the payload payloadworthy
    """
    options = {'use_cache': False, 'wait_for_model': True}
    parameters = {'top_k': 100, 'top_p': 0.7, 'temperature': 75.0}
    payload = {
        'inputs': {
            'text': content,
            'generated_responses': model_history[model_name]['generated_responses'],
            'past_user_inputs': model_history[model_name]['past_user_inputs']
        },
        'options': options,
        'parameters': parameters
    }
    return payload

# Define function to generate bot response
def generate_response(text_input, model_name):
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": "Bearer " + st.secrets["hf"]}
    payload = payloadify(text_input, model_name)
    response = requests.post(url, headers=headers, json=payload).json()
    return response.get('generated_text', None)

# Create widgets for user input and AI model selection
with st.sidebar:
    model_selection = st.selectbox("Select an AI model", list(AI_MODELS))
output_container = st.container()
st.write('<style>.stInput {position: fixed; bottom: 0px; width: calc(100% - 64px);}</style>', unsafe_allow_html=True)
input = st.text_input('Input', key='text_input')
send_button = st.button("Enter")

# Generate bot response and display conversation history
if send_button:
    with output_container:
        # Get existing conversation history and add new message
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        st.session_state.conversation_history.append('You: ' + input)
        bot_response = generate_response(input, AI_MODELS[model_selection])
        st.session_state.conversation_history.append(model_selection + ': ' + bot_response)
        # Update conversation history for selected model
        model_history[AI_MODELS[model_selection]]['past_user_inputs'].append(input)
        model_history[AI_MODELS[model_selection]]['generated_responses'].append(bot_response)
        # Display updated conversation history
        st.text_area('Conversation History', value='\n'.join(st.session_state.conversation_history), height=400)
