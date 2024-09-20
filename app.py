import openai
from flask import Flask, request, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer


openai.api_key = "sk-ejARedkRC4Aau-S8M62HTg6xu_MCkFBkepIRAGX1J-T3BlbkFJjdEJnICAqGyMzlPe81KPaKtYyvAPZsOe6EP0zTe64A" #API_KEY


app = Flask(__name__)


sia = SentimentIntensityAnalyzer()


MIN_PRICE = 100
MAX_PRICE = 500
bot_price = MAX_PRICE  


def get_bot_response(user_input):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=user_input,
        max_tokens=150
    )
    return response.choices[0].text.strip()


def analyze_sentiment(text):
    sentiment = sia.polarity_scores(text)
    return sentiment['compound']  


@app.route("/negotiate", methods=["POST"])
def negotiate():
    global bot_price

    user_input = request.json['message']
    sentiment_score = analyze_sentiment(user_input)
    
    
    user_price = int(request.json['price'])
    

    if sentiment_score >= 0.5:
        discount_factor = 0.2  
    elif sentiment_score >= 0.0:
        discount_factor = 0.1  
    else:
        discount_factor = 0.05  
    
    
    counter_offer = max(MIN_PRICE, bot_price - (bot_price * discount_factor))
    

    if user_price >= bot_price:
        negotiation_response = f"Great! We'll accept your offer of ${user_price}."
        bot_price = user_price  
    elif user_price < MIN_PRICE:
        negotiation_response = f"Your offer of ${user_price} is too low. We can't go lower than ${MIN_PRICE}."
    else:
        
        negotiation_response = f"We can't agree to your price of ${user_price}, but we can offer you a deal of ${counter_offer:.2f}."
        bot_price = counter_offer  

    
    gpt_prompt = f"Customer said: '{user_input}'. The bot's counteroffer is ${counter_offer:.2f}. Respond as a negotiation bot."
    conversational_response = get_bot_response(gpt_prompt)
    
    
    final_response = f"{negotiation_response}\n\n{conversational_response}"

    
    return jsonify({"response": final_response})

if __name__ == "__main__":
    app.run(debug=True)
