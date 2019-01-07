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
  v-btn.fab(slot='activator', color="error", fab, fixed, right)
    v-icon bug_report
  v-card
    v-card-title Report bugs
    .mx-4: v-text-field(label="Bug details", textarea, v-model="text")
    v-card-actions
      v-spacer
      v-btn(@click.native='showDialog = false') Cancel
      v-btn(@click.native='sendFeedback', color="primary", :disabled="states[buttonState].disabled") {{states[buttonState].text}}
</template>


<script>
const axios = require("axios");
const firebase = require("firebase");
require("firebase/firestore");

import {BACKEND_URL} from '../../project.config.js';

const STATES = {
  'idle': {
    disabled: false,
    text: 'send',
  },
  'sending': {
    disabled: true,
    text: 'sending',
  },
  'error': {
    disabled: false,
    text: 'Error. Retry.',
  },
}

export default {
  props: ['type'],
  data(){
    return {
      showDialog: false,
      text: '',
      buttonState: 'idle',
      states: STATES,
    }
  },
  methods: {
    sendFeedback() {
      this.buttonState = 'sending';
      axios.get(BACKEND_URL + '/config').then((response) => {
        return JSON.stringify(response.data);
      }).then((config) => {
        return firebase.firestore().collection('known_issues').doc('user_input').set({
          title: this.text,
          timestamp: new Date().getTime(),
          config,
        });
      }).then(() => {
        this.showDialog = false;
        this.buttonState = 'idle';
      }).catch(() => {
        this.buttonState = 'error';
      });
    },
  },
};
</script>

<style scoped>
.fab {
  bottom: 20px;
}
</style>
