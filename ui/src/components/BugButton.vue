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
v-dialog(v-model='showDialog', :persistent="true", max-width='400')
  v-btn(, v-if="type === 'inline'"slot='activator', color="error", @click="openDialog") Report a bug?
  v-btn.fab( v-else,slot='activator', color="error", @click="openDialog", fab, fixed, right)
    v-icon bug_report
  v-card
    v-card-title.headline Report bugs
    v-card-text
      .mx-4: v-text-field(label="Any feedback to the team?", textarea, v-model="text")
    v-card-actions
      v-spacer
      v-btn(@click.native='showDialog = false') Cancel
      v-btn(@click.native='sendFeedback', color="primary") send
</template>


<script>
const axios = require("axios");
const firebase = require("firebase");
require("firebase/firestore");

import {BACKEND_URL} from '../../project.config.js';

export default {
  props: ['type'],
  data(){
    return {
      showDialog: false,
      text: '',
    }
  },
  methods: {
    sendFeedback() {
      axios.get(BACKEND_URL + '/config').then((response) => {
        const config = JSON.stringify(response.data);
        firebase.firestore().collection('known_issues').doc('user_input').set({
          title: this.text,
          timestamp: new Date().getTime(),
          config,
        });
      });
    },
  },
};
</script>

<style scoped>
div {
  display: inline;
}
.fab {
  bottom: 20px;
}
</style>
