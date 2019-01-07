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
  v-card.py-4.mx-3.my-4
    h1.title.mb-4 Thank you for using Flight lab!
    p Rate your experience today
    .ratings: img(v-for="index in 5", :src="getIcon(index)", @click="chooseRating(index)", @mouseenter="hoverStar(index)", @mouseleave="cancelHover")
    .mx-4: v-text-field(label="Any feedback to the team?", textarea, v-model="feedbackText", @input="resetTimer")
    .mx-4: v-text-field(label="Any issue with the system? (visible to following users)", textarea, v-model="issueText", @input="resetTimer")
    br
    v-btn.primary(@click="submit") submit
    v-btn(to="/") Skip
    p(v-if="!chosenRating && submitClicked") Please choose a rating :)
</template>


<script>
const firebase = require("firebase");
require("firebase/firestore");

const icon = {
  color: 'https://www.gstatic.com/images/icons/material/system/2x/star_googyellow500_24dp.png',
  grey: 'https://www.gstatic.com/images/icons/material/system/2x/star_grey600_24dp.png',
}

export default {
  data(){
    return {
      state: undefined,
      hoverRating: undefined,
      chosenRating: undefined,
      feedbackText: '',
      issueText: '',
      timer: undefined,
      submitClicked: false,
    }
  },
  created() {
    this.resetTimer();
  },
  methods: {
    submit() {
      // Show 'Please choose a rating :)' the message
      if (!this.chosenRating) {
        this.submitClicked = true;
        return;
      } else {
        this.submitClicked = false;
      }

      // Save the rating and feedback
      firebase.firestore().collection('feedbacks').add({
        rating: this.chosenRating,
        text: this.feedbackText,
        timestamp: new Date().getTime(),
      });

      // Save the issue.
      if (this.issueText) {
        this.addKnownIssue();
      } else {
        this.clearKnownIssue();
      }

      this.$router.push('/');
    },
    addKnownIssue() {
      firebase.firestore().collection('known_issues').doc('user_input').set({
        title: this.issueText,
        timestamp: new Date().getTime(),
      });
    },
    clearKnownIssue() {
      firebase.firestore().collection('known_issues').doc('user_input').set({
        title: '',
        timestamp: new Date().getTime(),
      });
    },
    getIcon(index) {
      if (this.hoverRating) {
        if(index <= this.hoverRating) return icon.color;
        else return icon.grey;
      }
      else {
        if(index <= this.chosenRating) return icon.color;
        else return icon.grey;
      }
    },
    chooseRating(index) {
      this.chosenRating = index;
      this.resetTimer();
    },
    hoverStar(index) {
      this.hoverRating = index;
      this.resetTimer();
    },
    cancelHover(){
      this.hoverRating = undefined;
      this.resetTimer();
    },
    resetTimer() {
      clearTimeout(this.timer);
      this.timer = setTimeout(() => {
        this.$router.push('/');
      }, 5 * 60 * 1000);
    }
  },
};
</script>


<style lang="postcss" scoped>
p {
  margin-top: 2em;
  margin-bottom: 0;
}

.ratings > img {
  cursor: pointer;
  height: 40px;
}
</style>
