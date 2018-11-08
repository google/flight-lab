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
  h1.title
    img.logo(src="../assets/flightlablogo.png")
    | Flight Lab

  calendar
  v-card.py-4.mx-3.my-4
    v-dialog(v-model='showDialog', :persistent="true", max-width='400')
      v-btn(slot='activator', color="primary", :disabled="buttonStates[currentState].primaryButtonDisabled") {{buttonStates[currentState].primaryButtonText}}
      v-card
        v-card-title.headline {{currentState === 'off' ? 'Pre' : 'Post'}}-flight checklist
        v-card-text
          preflight.markdown.markdown-table(v-if="currentState === 'off'")
          postflight.markdown.markdown-table(v-else)
        v-card-actions
          v-spacer
          v-btn(@click.native='showDialog = false') Cancel
          v-btn(@click.native='turnOnOff', color="primary") Everything is good
    v-btn(color="warning", @click="restart", :disabled="buttonStates[currentState].restartButtonDisabled") restart software
    p.msg {{msg}}
  v-card.mx-3.my-4
    v-tabs(v-model='tab', centered)
      v-tab status
      v-tab simulator
      v-tab issues
    v-tabs-items(v-model='tab')
      v-tab-item: status(@updateOverallState="updateOverallState")
      v-tab-item: simulator.markdown
      v-tab-item
        h3.mt-3 Known issues
        known-issues.px-4.pb-4.ml-4
        h3.mt-3 Troubleshooting
        troubleshooting.markdown
  bug-button

</template>


<script>
const axios = require("axios");
const firebase = require("firebase");
require("firebase/firestore");

import Preflight from '../../docs/preflight.md'
import Postflight from '../../docs/postflight.md'
import Simulator from '../../docs/simulator.md'
import Troubleshooting from '../../docs/troubleshooting.md'
import KnownIssues from '../components/KnownIssues.vue'
import Status from '../components/Status.vue'
import BugButton from '../components/BugButton.vue'
import Calendar from '../components/Calendar.vue'

import {BACKEND_URL} from '../../project.config.js';
const TIMEOUT_STATE = -1;

export default {
  components: {Simulator, Troubleshooting, Status, BugButton, Calendar, KnownIssues, Preflight, Postflight},
  data(){
    return {
      currentState: 'off',
      tab: undefined,
      msg: '',
      showDialog: false,
      buttonStates: {
        off: {  // system state is OFF
          primaryButtonText: 'Turn everything on',
          primaryButtonDisabled: false,
          restartButtonDisabled: true,
        },
        turningOn: {  // right after clicking "turn on"
          primaryButtonText: 'Turning on',
          primaryButtonDisabled: true,
          restartButtonDisabled: true,
        },
        transient: {  // system state is TRANSIENT
          primaryButtonText: 'Working...',
          primaryButtonDisabled: true,
          restartButtonDisabled: false,
        },
        on: {  // system state is ON
          primaryButtonText: 'Turn everything off',
          primaryButtonDisabled: false,
          restartButtonDisabled: false,
        },
        turningOff: {  // right after clicking "turn on"
          primaryButtonText: 'Turning off',
          primaryButtonDisabled: false,
          restartButtonDisabled: true,
        },
        timeout: {  // system state is timeout
          primaryButtonText: 'Turn off',
          primaryButtonDisabled: false,
          restartButtonDisabled: false,
        },
        error: {  // TRANSIENT timeout, or other errors
          primaryButtonText: 'Turn everything off',
          primaryButtonDisabled: false,
          restartButtonDisabled: false,
        },
      },
    };
  },
  methods: {
    turnOnOff(){
      this.showDialog = false;
      if (this.currentState === 'off') {
        this.turnOn();
      }
      else {
        this.turnOff();
      }
    },
    turnOn() {
      this.log('Turning on...');
      this.currentState = 'turningOn';

      axios.get(BACKEND_URL + '/system/on')
        .then((response) => {/* do nothing, waiting for status */})
        .catch((err) => {
          console.error(err)
          this.currentState = 'error';
          this.log('Turning on failed', true);
        });
    },
    turnOff() {
      this.log('Turning off...');
      this.currentState = 'turningOff';

      axios.get(BACKEND_URL + '/system/off')
        .then((response) => {
          if (this.currentState !== 'error') {
            this.$router.push('/feedback');
          }
        })
        .catch((err) => {
          console.error(err)
          this.currentState = 'error';
          this.log('Turning off failed', true);
        });
    },
    restart(){
      this.log('Restarting software');

      axios.get(BACKEND_URL + '/system/restart')
        .then((response) => {/* do nothing, waiting for status */})
        .catch((err) => {
          console.error(err)
          this.log('Restarting failed', true);
        });
    },
    updateOverallState(data){
      switch(data.state) {
        case  proto.flightlab.System.State.ON:
          this.currentState = 'on';
          this.msg = 'System on';
          break
        case  proto.flightlab.System.State.OFF:
          this.currentState = 'off';
          this.msg = 'System off';
          break;
        case  proto.flightlab.System.State.TRANSIENT:
          this.currentState = 'transient';
          this.msg = 'Progress: ' + data.progress;
          break;
        case TIMEOUT_STATE:
          this.currentState = 'timeout';
          this.msg = 'Timeout. Progress: ' + data.progress;
          break;
        default:
          this.currentState = 'error';
          this.msg = 'Error! Try restart.';
          break;
      }
    },
    log(action, isError=false) {
      console.info(action);
      this.msg = action;
      const timestamp = new Date().getTime();
      // TODO: add user
      firebase.firestore().collection('logs').add({timestamp, action, isError});
    },
  },
};
</script>


<style scoped>
.msg {
  margin: 0;
}
</style>
