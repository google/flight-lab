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
li.py-2
  header
    p.time.ma-0 {{feedback.time}}
    v-btn(v-if="feedback.isArchived", @click="unArchive(feedback)", small, flat, color="warning") un-archive
    v-btn(v-else, @click="archive(feedback)", small, flat, color="warning") archive
  p.mb-1 {{feedback.text}}
</template>


<script>
const firebase = require("firebase");
require("firebase/firestore");

export default {
  props: ['feedback'],
  methods: {
    archive(feedback) {
      feedback.isArchived = true;
      this.saveFeedback(feedback);
    },
    unArchive(feedback) {
      feedback.isArchived = false;
      this.saveFeedback(feedback);
    },
    saveFeedback(feedback) {
      firebase.firestore().collection('feedbacks').doc(feedback.id).set({
        isArchived: feedback.isArchived
      }, {merge: true});
    },
  },
};
</script>


<style scoped>
li {
  list-style: none;
  border-bottom: 1px solid #aaa;
}
header {
  display: flex;
  align-items: center;
}
.time{
  opacity: .8;
  font-size: .9em;
  flex: 1;
}
</style>
