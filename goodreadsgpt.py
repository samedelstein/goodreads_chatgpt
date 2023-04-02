
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


with st.sidebar.form('input'):
    goodreads = st.sidebar.file_uploader("Upload Goodreads Data", type={"csv", "txt"})
    # Add start date input field
    start_date = st.sidebar.date_input('Start Date', datetime.date(2023,1,1))
    # Convert date to datetime object
    start_datetime = pd.to_datetime(start_date)        
    # Add fiction/non-fiction selection dropdown
    fiction_nonfiction = st.sidebar.radio("Select a book type:", ("Fiction", "NonFiction"))

    genre_selection = st.sidebar.selectbox(
        "Select Genre",
        ('Art',
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
        'Fiction',
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
        'Nonfiction',
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
        'Young Adult',),
    )
    submit_button = st.form_submit_button(label='Make Recommendations!')

if goodreads is not None:
    try:
        goodreads_df = pd.read_csv(goodreads)
        goodreads_df['Date Added'] =  pd.to_datetime(goodreads_df['Date Added'], format="%Y/%m/%d")
        goodreads_date_filtered = goodreads_df[goodreads_df['Date Added'] > start_datetime]
        goodreads_read = goodreads_date_filtered[goodreads_date_filtered['Exclusive Shelf'] == 'read'].sample(40, replace=True)
        goodreads_to_read = goodreads_date_filtered[goodreads_date_filtered['Exclusive Shelf'] == 'to-read'].sample(40, replace=True)
        books_read_expander = st.expander("List of Books I've Read")
        books_read_expander.write(goodreads_read[["Title", "Author", "My Rating", "Average Rating", "Date Added"]])
        books_to_read_expander = st.expander("List of Books To Read")
        books_to_read_expander.write(goodreads_to_read[["Title", "Author", "My Rating", "Average Rating", "Date Added"]])
        
    except Exception as e:
        st.error(e)

    with st.spinner(text='Extracting information...'):
        sleep(3)

#Filter for books read and to-read
    books_read = ', '.join([str(title) for title in goodreads_read['Title']])
    books_to_read = ', '.join([str(title) for title in goodreads_to_read['Title']])
# Define question string
    question = f"Based on this list of my previously read books, please recommend a {fiction_nonfiction} {genre_selection} book from my to-read list.\n\nHere is my read list:\n{books_read}\n\nHere is my to-read list:\n{books_to_read}"

# Use f-strings to dynamically construct the messages list
    messages = [
        {"role": "system", "content": "You are a helpful assistant that recommends books to read based on lists"},
        {"role": "user", "content": question},
        {"role": "user", "content": "Please list in bullet points the recommended book and why you are recommending it."}
    ]

# Call OpenAI API

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant that recommends books to read based on lists"},
            {"role": "user", "content": '\n'.join([m['content'] for m in messages])},
            {"role": "user", "content": 'Please list in bullet points the recommended book, why you are recommending it'}

        ]
    )

    # Extract answer from response
    answer = response["choices"][0]["message"]["content"]


# Main section content
    st.header('My Recommendation')
    st.write(f'Fiction/Nonfiction: {fiction_nonfiction}')
    st.write(f'Genre Selected: {genre_selection}')
    st.write(f'After Date: {start_date}')

    st.write(answer)