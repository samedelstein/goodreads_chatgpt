
import streamlit as st
import pandas as pd
import datetime
import openai
from time import sleep


directions_expander = st.expander("Directions to make this app work")
directions_expander.write(
    '''
    First, you need an OpenAI API key which you can sign up for [here](https://platform.openai.com/signup?__cf_chl_rt_tk=VKUHnuTzDpc3gfI4Cy8m.HtdJ4UYoDSj3Nd1cRYRUEo-1680459300-0-gaNycGzNC9A)
    NOTE: There is a cost to using the OpenAI API - it should be minimal (less than a penny per recommendation). You get $18 of free use over three months, then you will have to subscribe.
    
    Once you have the key, please paste it on the left hand menu of this app in the text box that say "Add OpenAI API Key here". Assuming they are valid, you'll see a green box  with the text "API credentials valid"

    Next, [download your goodreads list](https://www.goodreads.com/review/import). It may take a few minutes to generate the download.

    Once downloaded, drag and drop or browse for your file. NOTE: This app relies on you having added books to your to-read and read lists.

    Then, you can select the type of book and also filter for the dates when you added books to your to-read list (this let's you force the app to only recommend certain books.)

    Finally, click the "Make Recommendations!" button and the app will take a few seconds to output the name of the book and the reasons why it is being recommended.
    '''
)

st.header(':books: Personalized :blue[Book Recommendations!] :book:')


open_api_key_input = st.sidebar.text_input("Add OpenAI API Key here")
openai.api_key = open_api_key_input 
# Check if API credentials are valid
try:
    prompt = "Hello, World!"
    openai.Completion.create(engine="text-davinci-002", prompt=prompt)
    st.sidebar.success("API credentials valid")
except:
    st.sidebar.error("Invalid API credentials")

goodreads = st.file_uploader("Upload Goodreads Data", type={"csv", "txt"})
if goodreads is not None:
        goodreads_df = pd.read_csv(goodreads)
        goodreads_df['Date Added'] =  pd.to_datetime(goodreads_df['Date Added'], format="%Y/%m/%d")
        min_date = pd.to_datetime(goodreads_df['Date Added'].min(), format="%Y/%m/%d")

# Create a form
with st.form('input'):
    with st.sidebar:

        # Add fiction/non-fiction selection dropdown
        fiction_nonfiction = st.radio("Select fiction or nonfiction:", ("Fiction", "Nonfiction"), horizontal = True)

        genre_options = [
        'Art',
        'Biography',
        'Business',
        'Chick Lit',
        "Children's",
        'Christian',
        'Classics',
        'Comics',
        'Contemporary',
        'Cookbooks',
        'Crime',
        'Ebooks',
        'Fantasy',
        'Gay and Lesbian',
        'Graphic Novels',
        'Historical Fiction',
        'History',
        'Horror',
        'Humor and Comedy',
        'Manga',
        'Memoir',
        'Music',
        'Mystery',
        'Paranormal',
        'Philosophy',
        'Poetry',
        'Psychology',
        'Religion',
        'Romance',
        'Science',
        'Science Fiction',
        'Self Help',
        'Suspense',
        'Spirituality',
        'Sports',
        'Thriller',
        'Travel',
        'Young Adult']
        genre_selection = st.multiselect("Select a genre", genre_options)
        # Add start date input field
        if goodreads is not None:
            start_date = st.date_input('Start Date', min_date)
            # Convert date to datetime object
            start_datetime = pd.to_datetime(start_date) 
        submit_button = st.form_submit_button(label="Make Recommendations")


if goodreads is not None:
    if submit_button:
        try:
            goodreads_date_filtered = goodreads_df[goodreads_df['Date Added'] > start_datetime]
            goodreads_read = goodreads_date_filtered[goodreads_date_filtered['Exclusive Shelf'] == 'read'].sample(40, replace=True)
            goodreads_to_read = goodreads_date_filtered[goodreads_date_filtered['Exclusive Shelf'] == 'to-read'].sample(40, replace=True)
            books_read_expander = st.expander("List of Books I've Read")
            books_read_expander.write(goodreads_read[["Title", "Author", "My Rating", "Average Rating", "Date Added"]])
            books_to_read_expander = st.expander("List of Books To Read")
            books_to_read_expander.write(goodreads_to_read[["Title", "Author", "My Rating", "Average Rating", "Date Added"]])

        #Filter for books read and to-read
            books_read = ', '.join([str(title) for title in goodreads_read['Title']])
            books_to_read = ', '.join([str(title) for title in goodreads_to_read['Title']])
        # Define question string
            #first_question = f"Please look at all of the books that I have previously read here: \n{books_read}"
            question = f"I like to read a lot and have maintain a database of books I've read and want to read in Goodreads. Sometimes I have a hard time figuring out the next book I should be reading, but have an idea for the genre I'm interested in. Since I generally have liked books I've read in the past, I'd like to use those books as a model for the books I should read next. Please use my \n{books_read} list and recommend a {fiction_nonfiction} {genre_selection} book from this to-read list \n{books_to_read}. You should not choose any books except for the ones from my to-read list here: {books_to_read} and it should be a  {fiction_nonfiction} book from the {genre_selection} genre. If you don't have any recommendations, please say 'I don't know'"

        # Call OpenAI API
            
            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant that recommends books to read based on lists"},
                    {"role": "user", "content": "Please look at all of the books that I have previously read here: \n{books_read}"},
                    {"role": "assistant", "content": "I see all of the books that you have read here: \n{books_read} and will use them to base my recommendation off of for you when you ask. "},
                    {"role": "user", "content": "Now, please look at all of the books that I would like to read in the future here: \n{books_to_read}. "},
                    {"role": "assistant", "content": "I see all of the books you want to read here: \n{books_to_read} and will choose from one of them to make my recommendation when you ask for it. I will also use your selections of a {fiction_nonfiction} book in the {genre_selection} genre when I make the recommendation."},
                    {"role": "user", "content": question},
                    {"role": "user", "content": 'Please describe using 3 bullet points, one sentence each, why you are recommending this book. You should not make up details about the book that are not true.'},
                    {"role": "assistant", "content": 'I will make your recommendations!'},
                    {"role": "user", "content": 'Please make sure this is a {fiction_nonfiction} book in the {genre_selection} genre before making the recommendation. When you make the recommendation, never apologize.'},
                ],
            temperature=0.4,
            #stream = True,
            )

            # Extract answer from response
            answer = response["choices"][0]["message"]["content"]

            story_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are the world's most creative short story writer who takes prompts and write one-paragraph engaging stories"},
                    {"role": "user", "content": 'Based on the information from ' + answer + ' please write a short story for us.'},

                ],
            temperature=1.2,
            )
            story_answer = story_response["choices"][0]["message"]["content"]
            story_expander = st.expander("Read a brand new short story customized for you based on the book recommendation")
            story_expander.write(story_answer)


# Main section content

            st.header('My Recommendation')
            st.write(f'Fiction/Nonfiction: {fiction_nonfiction}')
            st.write(f'Genre Selected: {genre_selection}')
            st.write(f'After Date: {start_date}')

            st.write(answer)

        except Exception as e:
            st.error(e)




