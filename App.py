from flask import Flask,render_template,request
import pickle
import numpy as np

popular_df =pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_score.pkl','rb'))

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].str.title().values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_rating'].values),
                           rating = list(round(popular_df['avg_rating'], 1))
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input').lower()

    # Check if the user input exists in the pivot table
    if user_input not in pt.index:
        # Get 8 random book titles from the pt index
        random_books = pt.index.to_series().sample(5).tolist()

        # Fetch details for random books
        suggestions = []
        for book in random_books:
            temp_df = books[books['Book-Title'] == book]
            if not temp_df.empty:
                suggestion = [
                    temp_df['Book-Title'].iloc[0].title(),  # Title
                    temp_df['Book-Author'].iloc[0],         # Author
                    temp_df['Image-URL-M'].iloc[0],        # Image
                    temp_df['num_rating'].iloc[0],         # Votes
                    round(temp_df['avg_rating'].iloc[0], 1)  # Rating
                ]
                suggestions.append(suggestion)

        return render_template(
            'recommend.html',
            data=[],
            error=f"Book '{user_input}' not found. Here are some suggestions you can try:",
            suggestions=suggestions
        )

    # Find similar books
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        if not temp_df.empty:
            item = [
                temp_df['Book-Title'].iloc[0].title(),  # Title
                temp_df['Book-Author'].iloc[0],         # Author
                temp_df['Image-URL-M'].iloc[0],        # Image
                temp_df['num_rating'].iloc[0],         # Votes
                round(temp_df['avg_rating'].iloc[0], 1)  # Rating
            ]
            data.append(item)

    return render_template('recommend.html', data=data)




if __name__=="__main__":
    app.run(debug=True)
    print(popular_df.columns)