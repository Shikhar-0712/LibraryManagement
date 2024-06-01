export default {
    template: `<div>
    <div style="margin-bottom: 20px;">
        <input type="text" v-model="sectionSearch" placeholder="Search Section" @input="filterSections" style="padding: 5px;">
        <input type="text" v-model="bookSearch" placeholder="Search Book" style="padding: 5px;">
    </div>
    <h1 style="background-color: #f0f0f0; padding: 10px;">Welcome Home </h1>
    <div v-for="section in filteredSections" style="border: 1px solid #ccc; margin-top: 20px; padding: 10px; background-color: #e0e0e0;">
        <h2 style="margin-bottom: 10px;">{{section.name}}</h2>
        <div v-for="book in filteredBooks(section.id)" style="border: 1px solid #ddd; margin-top: 10px; padding: 10px; background-color: #f0f0f0;">
            <div v-if="book.section_id == section.id">
                <h3 style="margin-bottom: 5px;">Book Name: {{book.name}}</h3>
                <p style="margin-bottom: 5px;">Book Author: {{book.author}}</p>
                <p style="margin-bottom: 5px;">Book Content: {{book.content}}</p>
                <p style="margin-bottom: 5px;">Book Quantity: {{book.quantity}}</p>
                <button @click="issueBook(book.id)" style="padding: 5px;">Issue Book</button>
                <button @click="openFeedbackDialog(book)" style="padding: 5px;">Give Feedback</button>
            </div>
        </div>
    </div>
    <dialog ref="feedbackDialog" style="border: 1px solid #ccc; padding: 10px; background-color: #f0f0f0;">
        <h2>Provide Feedback</h2>
        <label for="rating">Rating:</label>
        <select v-model="rating" id="rating" style="margin-bottom: 10px;">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
        </select>
        <textarea v-model="feedbackText" placeholder="Enter your feedback" style="width: 100%; margin-bottom: 10px;"></textarea>
        <button @click="submitFeedback" style="padding: 5px;">Submit</button>
        <button @click="closeFeedbackDialog" style="padding: 5px;">Cancel</button>
    </dialog>
</div>
    `,

    data() {
        return {
            is_waiting: false,
            sections: [],
            books: [],
            filteredSections: [],
            sectionSearch: '',
            bookSearch: '',
            feedBackData: {
                book_id: null,
            },
            feedbackText: '',
            rating: 1,
            token: localStorage.getItem('auth-token'),
        }
    },
    methods: {
        async downlodResource() {
            this.isWaiting = true
            const res = await fetch('/download-csv')
            const data = await res.json()
            if (res.ok) {
                const taskId = data['task-id']
                const intv = setInterval(async () => {
                    const csv_res = await fetch(`/get-csv/${taskId}`)
                    if (csv_res.ok) {
                        this.isWaiting = false
                        clearInterval(intv)
                        window.location.href = `/get-csv/${taskId}`
                    }
                }, 1000)
            }
        },

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
                this.filteredSections = data;
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
        async issueBook(bookId) {
            const res = await fetch(`/issue-book/${bookId}`, {
                method: 'POST',
                headers: {
                    'Authentication-Token': this.token,
                }
            });

            const data = await res.json();
            if (res.ok) {
                await this.getBooks();
            } else {
                console.error(data.message);
            }
        },
        filterSections() {
            this.filteredSections = this.sections.filter(section =>
                section.name.toLowerCase().includes(this.sectionSearch.toLowerCase())
            );
        },
        filteredBooks(sectionId) {
            return this.books.filter(book =>
                book.section_id === sectionId &&
                book.name.toLowerCase().includes(this.bookSearch.toLowerCase())
            );
        },
        openFeedbackDialog(book) {
            this.$refs.feedbackDialog.showModal();
            this.feedBackData.book_id = book.id;
        },
        closeFeedbackDialog() {
            this.$refs.feedbackDialog.close();
            this.rating = 1;
            this.feedbackText = '';
        },
        async submitFeedback() {
            const feedbackData = {
                book_id: this.feedBackData.book_id,
                text: this.feedbackText,
                rating: this.rating
            };

            fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authentication-Token': this.token,
                },
                body: JSON.stringify(feedbackData)
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to submit feedback');
                    }
                    this.feedbackText = '';
                    this.rating = 1;
                    this.closeFeedbackDialog();
                    console.log('Feedback submitted successfully');
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    },

    mounted() {
        this.getSections();
        this.getBooks();
    }
}