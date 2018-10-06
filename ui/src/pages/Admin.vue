<!-- 
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
 -->

<template lang="pug">
main
  h1 Flight Lab admin
  router-link(to="/") Back to home

  v-card.mx-3.my-4
    v-tabs(v-model='tab', centered)
      v-tab devices
      v-tab feedbacks
      v-tab logs
    v-tabs-items(v-model='tab')
      v-tab-item: status(@updateOverallState="updateOverallState")
      v-tab-item
        p.mt-3 Overall rating: 
          b.info--text {{avgRating}}
        ul.px-4
          feedback-list(v-for="feedback in feedbacks", v-if="!feedback.isArchived", :feedback="feedback")
        v-expansion-panel
          v-expansion-panel-content
            h3(slot='header') Archived feedbacks
            ul.px-4
              feedback-list(v-for="feedback in feedbacks", v-if="feedback.isArchived", :feedback="feedback")
      v-tab-item
        table.mt-3
          thead: tr
            th Time
            th User
            th Action
          tbody
            template(v-for="log in logs")
              tr: td(colspan="3"): b {{log.date}}
              tr(v-for="event in log.events", :class="{'error--text': event.isError}")
                td {{event.time}}
                td {{event.user}}
                td {{event.action}}

</template>


<script>
const firebase = require("firebase");
require("firebase/firestore");

import Status from '../components/Status.vue'
import FeedbackList from '../components/AdminFeedbackList.vue'

export default {
  components: {Status, FeedbackList},
  data(){
    return {
      tab: undefined,
      feedbacks: [],
      avgRating: undefined,
      logs: [],
    }
  },
  created(){
    this.loadFeedbacks();
    this.loadLogs();
  },
  methods: {
    loadFeedbacks(){
      let ratingCount = 0;
      let ratingSum = 0;
      firebase.firestore().collection('feedbacks').orderBy('timestamp', 'desc').get().then(docs => {
        docs.forEach(doc => {
          const data = doc.data();
          data.id = doc.id;
          data.time = new Date(data.timestamp).toLocaleString();
          if (data.text) {
            this.feedbacks.push(data)
          }

          ratingSum += data.rating;
          ratingCount ++;
        });
        this.avgRating = (ratingSum / ratingCount).toPrecision(2);
      });
    },
    loadLogs(){
      let ratingCount = 0;
      let ratingSum = 0;
      firebase.firestore().collection('logs').orderBy('timestamp', 'desc').get().then(docs => {
        let lastDate;
        docs.forEach(doc => {
          const data = doc.data();
          const date = new Date(data.timestamp).toLocaleDateString();
          const time = new Date(data.timestamp).toLocaleTimeString();
          data.time = time;

          // Build an event tree. Array of each day with an events array.
          if (date !== lastDate) {
            lastDate = date;
            this.logs.push({
              date,
              events: [data]
            })
          }
          else {
            this.logs[this.logs.length - 1].events.push(data);
          }
        });
      });
    },
    updateOverallState(){
      // do nothing now
    },
  },
};
</script>


<style scoped>

table {
  width: 100%;
  padding: 0;
  font-weight: 400;
}
tr {
  background: transparent;
}
td, th {
  padding: 3px;
}

</style>
