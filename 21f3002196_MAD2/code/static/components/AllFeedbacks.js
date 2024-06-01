export default {
  template: `
    <div>
    <h1>All Feedbacks</h1>
    <ul>
    <li v-for="(feedback, index) in feedbacks" :key="index" style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; background-color: #f0f0f0;">
        <h2>Book Name: {{ feedback.book_name }}</h2>
        <p>User: {{ feedback.user_name }}</p>
        <p>Feedback: {{ feedback.text }}</p>
        <p>Rating: {{ feedback.rating }}</p>
      </li>
    </ul>
  </div>
    `,
  data() {
    return {
      feedbacks: [],
      token: localStorage.getItem('auth-token'),
    }
  },
  methods: {
    async fetchFeedbacks() {
      try {
        const response = await fetch('/librarian/feedbacks', {
          method: 'GET',
          headers: {
            'Authentication-Token': this.token,
          }
        });
        if (!response.ok) {
          throw new Error('Failed to fetch feedbacks');
        }
        const data = await response.json();
        this.feedbacks = data;
      } catch (error) {
        console.error('Error:', error);
      }
    }
  },
  mounted() {
    this.fetchFeedbacks();
  }
}