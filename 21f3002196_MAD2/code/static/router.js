import Home from "./components/Home.js";
import Login from "./components/login.js";
import Users from "./components/Users.js";
import Sectionform from "./components/Sectionform.js";
import Bookform from "./components/Bookform.js";
import IssuedBooks from "./components/IssuedBooks.js";
import RegisterUser from "./components/SignUpUser.js";
import LibrianIssuedBooks from "./components/LibrianIssuedBooks.js";
import AllFeedbacks from "./components/AllFeedbacks.js";

const routes = [
    { path: '/', component: Home },
    { path: '/login', component: Login, name: 'Login' },
    { path: '/users', component: Users },
    { path: '/createsection', component: Sectionform },
    { path: '/createbook', component: Bookform },
    {path: '/issuedBooks', component: IssuedBooks},
    {path: '/register', component: RegisterUser, name: 'Register'},
    {path: '/librarianIssuedBooks', component: LibrianIssuedBooks},
    {path: '/allFeedbacks', component: AllFeedbacks}
]

export default new VueRouter({ routes, })