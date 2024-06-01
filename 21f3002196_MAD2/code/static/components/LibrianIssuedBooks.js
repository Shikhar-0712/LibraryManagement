export default {
    template: `
    <div>
        <h1>Welcome to issued Books</h1>
        <div v-for="book in issuedBooks">
            <div>
                <h3>Book Name: {{book.name}}</h3>
                <p>Book Author: {{book.author}}</p>
                <p>Book Content: {{book.content}}</p>
                <p>Book Issued By: {{book.user.username}}</p>
                <p>Book Issued At: {{book.date_issue}}</p>
            </div>
            <div v-if="!book.date_issue">
            <button @click="acceptBook(book.id)">Accept</button>
            <button @click="revokeAccessOfBook(book.id, book.bookId)">Decline</button>
            </div>
            <button @click="revokeAccessOfBook(book.id, book.bookId)" v-if="book.date_issue">Revoke access of the book</button>
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
            const res = await fetch('/librarian/books-issued', {
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
        async revokeAccessOfBook(issuedBookId, bookId) {
            const res = await fetch(`/librarian/revoke-access-book/${issuedBookId}/${bookId}`, {
                method: 'GET',
                headers: {
                    'Authentication-Token': this.token,
                }
            })

            const data = await res.json()
            if (res.ok) {
                console.log(data);
                this.getIssuedBooks();
            }
        },
        async acceptBook(issuedBookId) {
            const res = await fetch(`/librarian/books-issued/${issuedBookId}/accept`, {
                method: 'GET',
                headers: {
                    'Authentication-Token': this.token,
                }
            })

            const data = await res.json()
            if (res.ok) {
                console.log(data);
                this.getIssuedBooks();
            }
        }
    },
    mounted() {
        this.getIssuedBooks();
    }
}