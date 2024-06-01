export default {
    template: `<div>
    <input type="text" placeholder="name" v-model="resource.name"/>
    <input type="text" placeholder="content" v-model="resource.content" />
    <input type="text" placeholder="author" v-model="resource.author" />
    <input type="number" placeholder="quantity" v-model="resource.quantity" />
    <label for="section">Section</label>
    <select v-model="resource.section_id">
        <option v-for="book in sections" :value="book.id">{{ book.name }}</option>
    </select>
    <button @click="createBook"> Create Book</button>
    </div>`,

    data() {
        return {
            sections: [],
            resource: {
                name: null,
                content: null,
                section_id: null,
                author: null,
                quantity: null,
            },
            token: localStorage.getItem('auth-token'),
        }
    },
    created() {
        this.getSections()
        console.log(this.sections)
    },
    methods: {
        async createBook() {
            console.log(this.resource.name, this.resource.description, this.resource.section_id)
            const res = await fetch('/api/book', {
                method: 'POST',
                headers: {
                    'Authentication-Token': this.token,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.resource),
            })

            const data = await res.json()
            if (res.ok) {
                alert(data.message)
                this.$router.push('/home')
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
            }
        },
    },
}