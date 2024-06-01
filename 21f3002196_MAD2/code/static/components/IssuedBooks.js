export default {
    template: `
    <div>
        <h1>Welcome to issued Books</h1>
        <div v-for="book in issuedBooks">
            <div>
                <h3>Book Name: {{book.name}}</h3>
                <p>Book Author: {{book.author}}</p>
                <p>Book Content: {{book.content}}</p>
                <p>Book Issued at : {{book.date_issue}}</p>
            </div>
            <button @click="returnBook(book.id)">Return the Book</button>
        </div> 
    </div>
    `,
    data() {
        return {
            issuedBooks: [],
            token: localStorage.getItem('auth-token'),
        }
    },
    methods: {
        async getIssuedBooks() {
            const res = await fetch('/user/books-issued', {
                method: 'GET',
                headers: {
                    'Authentication-Token': this.token,
                }
            })

            const data = await res.json()
            if (res.ok) {
                this.issuedBooks = data
            }
        },
        async returnBook(bookId) {
            try {
                const res = await fetch(`/user/book-return/${bookId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': this.token,
                    }
                });
                if (res.ok) {
                    this.getIssuedBooks();
                } else {
                    console.error('Failed to return the book.');
                }
            } catch (error) {
                console.error('Error returning the book:', error);
            }
        },
    },
    mounted() {
        this.getIssuedBooks();
    }
}