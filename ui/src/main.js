/*
Copyright 2018 Flight Lab authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/**
 * @fileoverview The entry file for webpack. Sets up Vue (including Vuetify and
 * Vue Router), Firebase and bootstrap the vue app. 
 */

// Import libraries
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuetify from 'vuetify'
import './vuetify.min.css' 
import firebase from 'firebase'

// App files
import Home from './pages/Home.vue'
import User from './pages/User.vue'
import Feedback from './pages/Feedback.vue'
import Admin from './pages/Admin.vue'
import Docs from './pages/Docs.vue'
import './_base.postcss'

import {FIREBASE_CONFIG} from '../project.config.js';

// Set the router
Vue.use(VueRouter)
const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/', component: Home },
    { path: '/user', component: User },
    { path: '/feedback', component: Feedback },
    { path: '/admin', component: Admin },
    { path: '/docs', component: Docs },
    { path: '/docs/:name', component: Docs },
    { path: '/(.*)', redirect: '/' },
  ],
})

// Vuetify material
Vue.use(Vuetify)

// Init firebase
firebase.initializeApp(FIREBASE_CONFIG);
// A quick fix for an firestore update. https://firebase.google.com/support/release-notes/js#cloud-firestore_9
firebase.firestore().settings({timestampsInSnapshots: true});

// Start app
new Vue({
  el: '#app',
  template: '<v-app dark><router-view></router-view></v-app>',
  router,
});
