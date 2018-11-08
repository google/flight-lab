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
ul
  li(v-for="issue in issues") {{issue.title}}
</template>


<script>
const firebase = require("firebase");
require("firebase/firestore");

export default {
  data(){
    return {
      issues: [],
    }
  },
  created(){
    firebase.firestore().collection('known_issues').get()
      .then(docs => {
        const temp = [];
        // Put the user_input entry to the first.
        docs.forEach(doc => {
          temp.push({
            title: doc.data().title,
            timestamp: doc.data().timestamp,
            isUserInput: doc.id === 'user_input',
          })
        });
        this.issues = temp.sort((a) => {
          if (a.isUserInput) return -1;
          else return 1;
        }).filter(a => {
          return a.title;
        });
      });
  },
};
</script>
