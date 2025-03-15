import streamlit as st
import json
import os
import requests
import altair as alt
import pandas as pd
from streamlit_lottie import st_lottie
import io

def local_css():
    st.markdown("""
    <style>
    /* Allow Streamlit's theme to take over (dark/light) */
    body { margin: 0; padding: 0; }
    h1, h2, h3, h4 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 0.5rem;
    }
    .stButton button {
        background-color: #2C3E50;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }
    /* Card styling for book display */
    .book-card {
        background: linear-gradient(135deg, #434343 0%, #000000 100%);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        color: #ffffff;
    }
    .book-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .book-info {
        font-size: 1rem;
        margin-bottom: 3px;
    }
    .header-title {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        st.error("Error loading animation: " + str(e))
        return None

FILENAME = "library.json"

def demo_library():
    return [
        {
            "title": "1984",
            "author": "George Orwell",
            "year": 1949,
            "genre": "Dystopian",
            "read": True,
            "cover_url": "https://images-na.ssl-images-amazon.com/images/I/71kxa1-0mfL.jpg",
            "rating": 5
        },
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "year": 1925,
            "genre": "Classic",
            "read": False,
            "cover_url": "https://images-na.ssl-images-amazon.com/images/I/71FTb9X6wsL.jpg",
            "rating": 4
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "year": 1813,
            "genre": "Romance",
            "read": True,
            "cover_url": "https://images-na.ssl-images-amazon.com/images/I/71xBLRBYOiL.jpg",
            "rating": 5
        }
    ]

def load_library():
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as file:
                library = json.load(file)
                return library
        except json.JSONDecodeError:
            st.error("Error decoding JSON from file. Initializing with demo data.")
    library = demo_library()
    save_library(library)
    return library

def save_library(library):
    with open(FILENAME, "w") as file:
        json.dump(library, file, indent=4)

def add_book(library, success_animation):
    st.header("Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=0, step=1, format="%d")
        genre = st.text_input("Genre")
        cover_url = st.text_input("Cover Image URL (optional)")
        read = st.checkbox("Have you read this book?")
        rating = st.slider("Rating (1 = Worst, 5 = Best)", min_value=1, max_value=5, value=3)
        submitted = st.form_submit_button("Add Book")
    
    if submitted:
        if title and author:
            book = {
                "title": title,
                "author": author,
                "year": int(year),
                "genre": genre,
                "read": read,
                "cover_url": cover_url.strip(),
                "rating": rating
            }
            library.append(book)
            save_library(library)
            st.success("Book added successfully!")
            if success_animation:
                st_lottie(success_animation, height=150, key="success_add")
        else:
            st.error("Title and Author are required.")

def remove_book(library, remove_animation):
    st.header("Remove a Book")
    title = st.text_input("Enter the title of the book to remove", key="remove_title")
    if st.button("Remove Book"):
        initial_length = len(library)
        library[:] = [book for book in library if book["title"].lower() != title.lower()]
        if len(library) < initial_length:
            save_library(library)
            st.success(f"Book '{title}' removed successfully!")
            if remove_animation:
                st_lottie(remove_animation, height=150, key="remove_anim")
        else:
            st.error("Book not found.")

def update_book(library, update_animation):
    st.header("Update a Book")
    titles = [book["title"] for book in library]
    if titles:
        selected_title = st.selectbox("Select a book to update", titles)
        book_to_update = next((book for book in library if book["title"] == selected_title), None)
        if book_to_update:
            with st.form("update_book_form"):
                new_title = st.text_input("Title", value=book_to_update["title"])
                new_author = st.text_input("Author", value=book_to_update["author"])
                new_year = st.number_input("Publication Year", min_value=0, step=1, format="%d", value=book_to_update["year"])
                new_genre = st.text_input("Genre", value=book_to_update["genre"])
                new_cover = st.text_input("Cover Image URL", value=book_to_update.get("cover_url", ""))
                new_read = st.checkbox("Have you read this book?", value=book_to_update["read"])
                new_rating = st.slider("Rating (1 = Worst, 5 = Best)", 1, 5, book_to_update.get("rating", 3))
                submitted = st.form_submit_button("Update Book")
            if submitted:
                book_to_update["title"] = new_title
                book_to_update["author"] = new_author
                book_to_update["year"] = int(new_year)
                book_to_update["genre"] = new_genre
                book_to_update["cover_url"] = new_cover.strip()
                book_to_update["read"] = new_read
                book_to_update["rating"] = new_rating
                save_library(library)
                st.success("Book updated successfully!")
                if update_animation:
                    st_lottie(update_animation, height=150, key="update_anim")
    else:
        st.info("No books available to update.")

def search_books(library):
    st.header("Search for Books")
    query = st.text_input("Enter title or author to search", key="search_query")
    if st.button("Search"):
        results = [book for book in library 
                   if query.lower() in book["title"].lower() or query.lower() in book["author"].lower()]
        if results:
            for book in results:
                display_book(book)
        else:
            st.info("No matching books found.")

def display_book(book):
    status = "Read" if book["read"] else "Unread"
    star_icons = "⭐" * book.get("rating", 3)
    cover_url = book.get("cover_url", "")
    st.markdown(f"""
    <div class="book-card">
      <div class="book-title">{book['title']}</div>
      <div class="book-info">Author: {book['author']}</div>
      <div class="book-info">Year: {book['year']} | Genre: {book['genre']}</div>
      <div class="book-info">Status: {status}</div>
      <div class="book-info">Rating: {star_icons}</div>
    </div>
    """, unsafe_allow_html=True)
    if cover_url:
        st.image(cover_url, width=150, caption=f"Cover: {book['title']}")

def display_all_books(library):
    st.header("All Books in Library")
    sort_options = ["Title (A–Z)", "Year (Newest First)", "Year (Oldest First)", "Rating (High to Low)", "Rating (Low to High)"]
    sort_choice = st.selectbox("Sort by", sort_options)
    
    genres = sorted(list(set(book["genre"] for book in library)))
    genres.insert(0, "All")
    selected_genre = st.selectbox("Filter by Genre", genres)
    
    filtered_books = library if selected_genre == "All" else [b for b in library if b["genre"] == selected_genre]
    if sort_choice == "Title (A–Z)":
        filtered_books.sort(key=lambda b: b["title"].lower())
    elif sort_choice == "Year (Newest First)":
        filtered_books.sort(key=lambda b: b["year"], reverse=True)
    elif sort_choice == "Year (Oldest First)":
        filtered_books.sort(key=lambda b: b["year"])
    elif sort_choice == "Rating (High to Low)":
        filtered_books.sort(key=lambda b: b.get("rating", 0), reverse=True)
    elif sort_choice == "Rating (Low to High)":
        filtered_books.sort(key=lambda b: b.get("rating", 0))
    
    if filtered_books:
        for book in filtered_books:
            display_book(book)
    else:
        st.info("No books found for the selected genre or sort criteria.")

def display_dashboard(library):
    st.header("Library Dashboard")
    total = len(library)
    if total > 0:
        genre_counts = {}
        for book in library:
            genre = book["genre"]
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        genre_data = [{"genre": k, "count": v} for k, v in genre_counts.items()]
        df_genre = pd.DataFrame(genre_data)
        genre_chart = alt.Chart(df_genre).mark_bar().encode(
            x=alt.X("genre:N", sort="-y", title="Genre"),
            y=alt.Y("count:Q", title="Number of Books"),
            tooltip=["genre", "count"]
        ).properties(width=300, height=300, title="Books by Genre")
        
        year_counts = {}
        for book in library:
            year = book["year"]
            year_counts[year] = year_counts.get(year, 0) + 1
        year_data = [{"year": k, "count": v} for k, v in year_counts.items()]
        df_year = pd.DataFrame(year_data)
        year_chart = alt.Chart(df_year).mark_bar().encode(
            x=alt.X("year:O", title="Publication Year"),
            y=alt.Y("count:Q", title="Number of Books"),
            tooltip=["year", "count"]
        ).properties(width=300, height=300, title="Books by Year")
        
        rating_counts = {}
        for book in library:
            rating = book.get("rating", 0)
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        rating_data = [{"rating": k, "count": v} for k, v in rating_counts.items()]
        df_rating = pd.DataFrame(rating_data)
        rating_chart = alt.Chart(df_rating).mark_bar().encode(
            x=alt.X("rating:O", title="Rating"),
            y=alt.Y("count:Q", title="Number of Books"),
            tooltip=["rating", "count"]
        ).properties(width=300, height=300, title="Books by Rating")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.altair_chart(genre_chart, use_container_width=True)
        with col2:
            st.altair_chart(year_chart, use_container_width=True)
        with col3:
            st.altair_chart(rating_chart, use_container_width=True)
    else:
        st.info("No books available for dashboard statistics.")

def export_library(library):
    if library:
        df = pd.DataFrame(library)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Library as CSV", csv, "library_export.csv", "text/csv")
    else:
        st.info("No data to export.")

def import_library():
    st.header("Import Library Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            new_library = df.to_dict(orient="records")
            save_library(new_library)
            st.success("Library imported successfully!")
        except Exception as e:
            st.error(f"Error importing CSV: {e}")

def reset_library():
    if st.button("Reset Library to Demo Data"):
        library = demo_library()
        save_library(library)
        st.success("Library reset to demo data.")
        return library
    return None

def data_management(library):
    st.header("Data Management")
    col1, col2 = st.columns(2)
    with col1:
        export_library(library)
    with col2:
        import_library()
    new_lib = reset_library()
    if new_lib is not None:
        return new_lib
    return library

def main():
    local_css()
    st.markdown('<div class="header-title">Personal Library Manager</div>', unsafe_allow_html=True)
    st.write("Manage your book collection with a polished, interactive interface!")
    
    header_animation = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_puciaact.json")
    success_animation = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_jbrw3hcz.json")
    remove_animation = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_RUr7rP.json")
    update_animation = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_0yfsb3a1.json")
    
    if header_animation:
        st_lottie(header_animation, height=200)
    
    library = load_library()
    
    menu_options = [
        "Add a Book", 
        "Remove a Book", 
        "Update a Book",
        "Search for a Book", 
        "Display All Books", 
        "Dashboard", 
        "Data Management"
    ]
    choice = st.sidebar.selectbox("Select an option", menu_options)
    
    if choice == "Add a Book":
        add_book(library, success_animation)
    elif choice == "Remove a Book":
        remove_book(library, remove_animation)
    elif choice == "Update a Book":
        update_book(library, update_animation)
    elif choice == "Search for a Book":
        search_books(library)
    elif choice == "Display All Books":
        display_all_books(library)
    elif choice == "Dashboard":
        display_dashboard(library)
    elif choice == "Data Management":
        library = data_management(library)
    
    st.markdown("---")
    st.write("Created by [Muhammad Saim Nadeem](https://github.com/SaimSM)")
if __name__ == "__main__":
    main()
