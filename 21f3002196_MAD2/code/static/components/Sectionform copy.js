export default {
    template: `<div>
    <input type="text" placeholder="name" v-model="resource.name"/>
    <input type="text" placeholder="description" v-model="resource.description" />
    <button @click="createSection"> Create Section</button>
    </div>`,

    data() {
        return {
            resource: {
                name: null,
                description: null,
            },
            token: localStorage.getItem('auth-token'),
        }
    },

    methods: {
        async createSection() {
            const res = await fetch('/api/section', {
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
            }
        },
    },
}