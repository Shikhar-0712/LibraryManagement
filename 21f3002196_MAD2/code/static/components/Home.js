import StudentHome from "./StudentHome.js"
import LibrarianHome from "./LibrarianHome.js"
import AdminHome from "./AdminHome.js"

export default {
    template: `<div> 
    <StudentHome v-if="userRole == 'user'" />
    <LibrarianHome v-if="userRole == 'librarian'" />
    <AdminHome v-if="userRole == 'admin'" />
    </div>`,
    data() {
        return {
            userRole: localStorage.getItem('role'),
        }
    },
    components: {
        StudentHome,
        LibrarianHome,
        AdminHome,
    }
}
