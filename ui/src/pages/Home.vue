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
main.pb-5
  img.logo(src="../assets/flightlablogo.png")
  h1.mt-0.display-3 Flight Lab
  p.title.my-3 A simulation & learning experience at Google
  
  template(v-if="hasBadgeReader")
    p.headline.my-4.warning--text Swipe badge to start!
    v-dialog(v-model='showAuthorizedDialog', :persistent="true", max-width='400')
      v-card
        v-card-text
          p.title Flight Lab rules
          rules.markdown
          p.title.mt-4 Known issues
          known-issues.ml-4
        v-card-actions
          v-spacer
          v-btn(@click.native='showAuthorizedDialog = false') Cancel
          v-btn(color="primary", to='/user') Agree
    v-dialog(v-model='showUnauthorizedDialog', :persistent="true", max-width='400')
      v-card
        v-card-text
          p Unauthorized. Please contact the team to get access.
        v-card-actions
          v-spacer
          v-btn(@click.native='showUnauthorizedDialog = false') Close
  v-dialog(v-else, v-model='showAuthorizedDialog', :persistent="true", max-width='400')
    v-btn.my-3(large, slot='activator', color='primary') Let's fly!
    v-card
      v-card-text
        p.title Flight Lab rules
        rules.markdown
        p.title.mt-4 Known issues
        known-issues.ml-4
      v-card-actions
        v-spacer
        v-btn(@click.native='showAuthorizedDialog = false') Cancel
        v-btn(color="primary", to='/user') Agree
  p Powered by Google Flight Lab.
  bug-button
  .calendar-container
    calendar

</template>


<script>
import Rules from '../../docs/rules.md'
import BugButton from '../components/BugButton.vue'
import Calendar from '../components/Calendar.vue'
import KnownIssues from '../components/KnownIssues.vue'

import {BACKEND_URL, HAS_BADGE_READER} from '../../project.config.js';
const axios = require("axios");

export default {
  components: {Rules, BugButton, Calendar, KnownIssues},
  data(){
    return {
      showUnauthorizedDialog: false,
      showAuthorizedDialog: false,
      hasBadgeReader: HAS_BADGE_READER,
    }
  },
  created() {
    this.getBadgeStatus();
    this.interval = setInterval(() => {this.getBadgeStatus()}, 1000);
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
  methods: {
    getBadgeStatus(){
      axios.get(BACKEND_URL + '/config').then((response) => {
        const status = response.data.machines
            .find(machine => machine.name === 'Badge Reader').components
            .find(component => component.name === 'BadgeReader')
            .badger.status;
        this.badgeState = status;
        switch(status) {
          case 'AUTHORIZED':
            this.showAuthorizedDialog = true;
            this.showUnauthorizedDialog = false;
            break;
          case 'UNAUTHORIZED':
            this.showUnauthorizedDialog = true;
            this.showAuthorizedDialog = false;
            break;
          default:
            this.showAuthorizedDialog = false;
            this.showUnauthorizedDialog = false;
        }
      })
      .catch(console.error);
    },
  },
};
</script>


<style scoped>
.logo {
  height: 100px;
}

main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-image: linear-gradient(rgba(50,50,50,.8), rgba(50,50,50,.8)), url(../assets/bg.jpg);
  background-size: cover;
  background-position: 50% 50%;
  padding: 1em;
}

.calendar-container {
  position: fixed;
  top: 0;left: 0;right: 0;
}
</style>
