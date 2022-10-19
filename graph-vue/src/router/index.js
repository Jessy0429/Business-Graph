import Vue from 'vue'
import Router from 'vue-router'
import MainPage from "@/components/MainPage";
import RelationshipPage from "@/components/RelationshipPage";
import RelatedPartiesPage from "@/components/RelatedPartiesPage";
import ShareholdingPage from "@/components/ShareholdingPage";
import StockholderPage from "@/components/StockholderPage";

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
                {path: 'shareholding', name: 'shareholding', component: ShareholdingPage},
                {path: 'stockholder', name: 'stockholder', component: StockholderPage},
            ]
        }
    ]
})