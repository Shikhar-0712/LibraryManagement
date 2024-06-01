export default {
    template: `<div style="background-color: #f0f0f0; padding: 20px;">
    <h1>Welcome Home Librarian</h1>
    <div v-for="section in sections" style="background-color: #e0e0e0; margin-top: 20px; padding: 10px;">
        <h2>SECTION: {{section.name}}</h2>
        <button @click="deleteSection(section.id)" style="padding: 5px;">Delete Section</button>
        <button @click="editSection(section)" style="padding: 5px;">Edit Section</button>
        <button @click="openDialog('add', book, section.id)" style="padding: 5px;">Add Book</button>
        <div v-for="book in books" >
            <div v-if="book.section_id == section.id" style="background-color: #f8f8f8; border: 1px solid #ccc; margin-top: 10px; padding: 10px;">
                <h3>Book Name: {{book.name}}</h3>
                <p>Book Author: {{book.author}}</p>
                <p>Book Content: {{book.content}}</p>
                <p>Book Quantity: {{book.quantity}}</p>
                <button @click="openDialog('update', book, section.id)" style="padding: 5px;">Update Book</button>
                <button @click="deleteBook(book.id)" style="padding: 5px;">Delete Book</button>
            </div>
        </div>
    </div>
    <dialog ref="sectionDialog" style="background-color: #fff; border: 1px solid #ccc; padding: 10px;">
        <form @submit.prevent="updateSection">
            <input v-model="editedSection.name" placeholder="Section Name" style="padding: 5px;">
            <input v-model="editedSection.description" placeholder="Description" style="padding: 5px;">
            <button type="submit" style="padding: 5px;">Update Section</button>
        </form>
        <button @click="closeDialog" style="padding: 5px;">Close</button>
    </dialog>
    <dialog ref="bookDialog" style="background-color: #fff; border: 1px solid #ccc; padding: 10px;">
        <form @submit.prevent="submitBook">
            <input v-model="bookData.name" placeholder="Book Name" style="padding: 5px;">
            <input v-model="bookData.author" placeholder="Book Author" style="padding: 5px;">
            <input v-model="bookData.content" placeholder="Book Content" style="padding: 5px;">
            <input v-model="bookData.quantity" placeholder="Book Quantity" style="padding: 5px;">
            <select v-model="bookData.section_id" placeholder="Select Section" style="padding: 5px;">
                <option v-for="section in sections" :value="section.id">{{ section.name }}</option>
            </select>
            <button type="submit" style="padding: 5px;">{{ dialogMode === 'add' ? 'Add Book' : 'Update Book' }}</button>
        </form>
        <button @click="closeBookDialog" style="padding: 5px;">Close</button>
    </dialog>
</div>
`,

    data() {
        return {
            sections: [],
            books: [],
            token: localStorage.getItem('auth-token'),
            editedSection: {
                id: null,
                name: '',
                description: ''
            },
            bookData: {
                id: null,
                name: '',
                author: '',
                content: '',
                quantity: '',
                section_id: 0
            }
        }
    },
    created() {
        this.getSections()
        this.getBooks()
    },
    methods: {
        async getSections() {
            const res = await fetch('/api/section', {
                method: 'GET',
                headers: {
                    'Authentication-Token': this.token,
                }
            })

            const data = await res.json()
            if (res.ok) {
                this.sections = data
            }
        },
        async deleteSection(id) {
            const res = await fetch(`/api/section/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authentication-Token': this.token,
                }
            })

            const data = await res.json()
            if (res.ok) {
                this.getSections();
                console.log(data);
            }
        },
        editSection(section) {
            this.editedSection.id = section.id;
            this.editedSection.name = section.name;
            this.editedSection.description = section.description;
            this.$refs.sectionDialog.showModal();
        },
        async updateSection() {
            const res = await fetch(`/api/section/${this.editedSection.id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': this.token,
                },
                body: JSON.stringify({
                    name: this.editedSection.name,
                    description: this.editedSection.description
                })
            });
            if (res.ok) {
                this.getSections();
                this.closeDialog();
            }
        },
        async getBooks() {
            const res = await fetch('/api/book', {
                method: 'GET',
                headers: {
                    'Authentication-Token': this.token,
                }
            })

            const data = await res.json()
            if (res.ok) {
                this.books = data
            }
        },
        async submitBook() {
            if (this.dialogMode === 'add') {
                fetch('/api/book', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': this.token,
                    },
                    body: JSON.stringify({
                        name: this.bookData.name,
                        author: this.bookData.author,
                        content: this.bookData.content,
                        quantity: this.bookData.quantity,
                        section_id: this.bookData.section_id
                    })
                })
                    .then(response => {
                        if (response.ok) {
                            this.getBooks();
                            this.closeDialog();
                        } else {
                            console.error('Error adding book:', response.statusText);
                        }
                    })
                    .catch(error => {
                        console.error('Error adding book:', error);
                    });
            } else if (this.dialogMode === 'update') {
                this.updateBook();
            }
        },
        async deleteBook(id) {
            const res = await fetch(`/api/book/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authentication-Token': this.token,
                }
            });

            if (res.ok) {
                this.getBooks();
                console.log(`Book with ID ${id} deleted.`);
            }
        },
        openDialog(mode, book = null, sectionId) {
            this.dialogMode = mode;
            if (mode === 'update' && book) {
                this.bookData.id = book.id;
                this.bookData.name = book.name;
                this.bookData.author = book.author;
                this.bookData.content = book.content;
                this.bookData.quantity = book.quantity;
                this.bookData.section_id = sectionId;
            } else if (mode === 'add') {
                this.bookData.id = null;
                this.bookData.name = '';
                this.bookData.author = '';
                this.bookData.content = '';
                this.bookData.quantity = '';
                this.bookData.section_id = sectionId;
            }
            this.$refs.bookDialog.showModal();
        },
        async updateBook() {
            const res = await fetch(`/api/book/${this.bookData.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': this.token,
                },
                body: JSON.stringify(this.bookData)
            });
            if (res.ok) {
                this.getBooks();
                this.updatedBook = {
                    name: '',
                    author: '',
                    content: '',
                    quantity: ''
                };
            }
        },
        closeDialog() {
            this.$refs.sectionDialog.close();
        },
        closeBookDialog() {
            this.$refs.bookDialog.close();
        }
    },
}