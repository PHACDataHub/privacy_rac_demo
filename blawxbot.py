import gradio as gr
from agent.blawxagent import agent

block = gr.Blocks()

def chat_response(input, history):
    history = history or []
    output = agent.run(input)
    bot_message = output['output'] if isinstance(output, dict) and 'output' in output else output
    history.append((input,bot_message))
    return "", history, history

with block:
    chatbot = gr.Chatbot(show_label=False)
    message = gr.Textbox(placeholder="Ask your question here.",show_label=False)
    state = gr.State()
    message.submit(chat_response, inputs=[message,state], outputs=[message, chatbot,state])

block.launch(debug=True)