import Vue from 'vue'
import Router from 'vue-router'
import MainPage from "@/components/MainPage";
import RelationshipPage from "@/components/RelationshipPage";
import RelatedPartiesPage from "@/components/RelatedPartiesPage";
import ShareholdingPage from "@/components/ShareholdingPage";

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'MainPage',
            component: MainPage,
            children:[
                {path: 'relationship', name: 'relationship', component: RelationshipPage},
                {path: 'relatedparty', name: 'relatedparty', component: RelatedPartiesPage},
                {path: 'shareholding', name: 'shareholding', component: ShareholdingPage}
            ]
        }
    ]
})

const originalPush = Router.prototype.push
Router.prototype.push = function push(location) {
    return originalPush.call(this, location).catch(err => err)
}