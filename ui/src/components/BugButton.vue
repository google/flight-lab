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
div
  v-btn(v-if="type === 'inline'", color="error", @click.native="sendFeedback") Report a bug?
  v-btn.fab(v-else, color="error", @click.native="sendFeedback", fab, fixed, right)
    v-icon bug_report

</template>


<script>
const axios = require("axios");

import {BACKEND_URL} from '../../project.config.js';

export default {
  props: ['type'],
  methods: {
    sendFeedback() {
      axios.get(BACKEND_URL + '/config').then((response) => {
        const configData = JSON.stringify(response.data);
        
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
