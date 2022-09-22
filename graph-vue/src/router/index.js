import Vue from 'vue'
import Router from 'vue-router'
import MainPage from "@/components/MainPage";
import RelationshipPage from "@/components/RelationshipPage";


Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'MainPage',
            component: MainPage,
            children:[
                {path: 'relationship', name: 'relationship', component: RelationshipPage}
            ]
        }
    ]
})