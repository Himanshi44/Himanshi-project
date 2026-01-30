from flask import Flask, render_template, request, jsonify
from chatbot import AQIChatbot

app = Flask(__name__)
chatbot = AQIChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    response = chatbot.process_message(user_message)
    
    # Check if response includes graph data
    if isinstance(response, dict) and 'graph_data' in response:
        return jsonify({
            'response': response['text'],
            'graph_data': response['graph_data']
        })
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
