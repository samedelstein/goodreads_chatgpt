import streamlit as st
import pandas as pd
import datetime
import openai

openai.api_key = '[OPEN AI KEY HERE]'


with st.sidebar.form('input'):

    date = st.sidebar.date_input('start date', datetime.date(2023,1,1))
    date = pd.to_datetime(date)        
    fiction_nonfiction = st.sidebar.selectbox(
        "Select Fiction or Nonfiction",
        ('Fiction', 'Nonfiction')
    )
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
    goodreads = st.sidebar.file_uploader("Upload Goodreads Data", type={"csv", "txt"})
    if goodreads is not None:
        goodreads_df = pd.read_csv(goodreads)
        goodreads_df['Date Added'] =  pd.to_datetime(goodreads_df['Date Added'], format="%Y/%m/%d")
        goodreads_date_filtered = goodreads_df[goodreads_df['Date Added'] > date]
        goodreads_date_filtered[["Title", "Author", "My Rating", "Average Rating", "Date Added"]]
        goodreads_read = goodreads_date_filtered[goodreads_date_filtered['Exclusive Shelf'] == 'read'].sample(40, replace=True)
        goodreads_to_read = goodreads_date_filtered[goodreads_date_filtered['Exclusive Shelf'] == 'to-read'].sample(40, replace=True)
    submit_button = st.form_submit_button(label='Extract data')

if submit_button:
    # Check that text field is not empty
    if not text.strip():
        st.error('WARNING: Please enter text')
    else:
        with st.spinner(text = 'Extracting information…'):
            sleep(3)

#Filter for books read and to-read
books_read =  ', '.join(goodreads_read['Title'].astype(str).values.flatten())
books_to_read =  ', '.join(goodreads_to_read['Title'].astype(str).values.flatten())


#Create question 
question = '''Based on this list of my previous read books, please recommend a ''' + fiction_nonfiction + ' ' + genre_selection +''' book from my to-read list and paste a link to the Amazon listing so I can buy it.

Here is my read list: ''' + books_read + '''

Here is my to-read list: ''' + books_to_read

#Run OpenAI Code
response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant that recommends books to read based on lists"},
        {"role": "user", "content": question},
        {"role": "user", "content": 'Please list in bullet points the recommended book, why you are recommending it'}

    ]
)

answer = response["choices"][0]["message"]["content"]

#Main section content
st.header('My Recommendation')
st.write('Fiction/Nonfiction: {}'.format(fiction_nonfiction))
st.write('Genre Selected: {}'.format(genre_selection))
st.write('After Date: {}'.format(date))

st.write(answer)