from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Create a SentimentIntensityAnalyzer object.
sid_obj = SentimentIntensityAnalyzer()

def sentiment_scores(sentence):
    # polarity_scores method of SentimentIntensityAnalyzer
    # object gives a sentiment dictionary.
    # which contains pos, neg, neu, and compound scores.
    sentiment_dict = sid_obj.polarity_scores(sentence)
    # sentiment_dict format:
    # sentiment_dict = \
    #     {"neg": round(neg, 3),
    #      "neu": round(neu, 3),
    #      "pos": round(pos, 3),
    #      "compound": round(compound, 4)}

    return sentiment_dict


def get_sentiment_scores_text(sentiment_dict):
    # decide sentiment as positive, negative and neutral
    if sentiment_dict['compound'] >= 0.05 :
        final="Positive"
    elif sentiment_dict['compound'] <= - 0.05 :
        final="Negative"
    else :
        final="Neutral"

    # responses
    response1=f"Overall sentiment dictionary is : {sentiment_dict}"
    response2=f"Feedback text was {round(sentiment_dict['neg']*100, 2)}% Negative"
    response3=f"Feedback text was {round(sentiment_dict['neu']*100, 2)}% Neutral"
    response4=f"Feedback text was {round(sentiment_dict['pos']*100,2 )}% Positive"
    response5=f"Sentence Overall Rated As {final}"
    return response1, response2, response3, response4, response5
