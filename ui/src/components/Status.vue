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
  p.error--text(v-if="isError"): b Unknown
  div(:class="{'-fade': isError}", v-if="isReady")
    h3 SkyView
    table
      thead: tr
        th
        th Left
        th Center
        th Right
      tbody
        tr
          td Projectors
          td: status-text(:item="skyView.left.projector")
          td: status-text(:item="skyView.center.projector")
          td: status-text(:item="skyView.right.projector")
        tr
          td Simulators
          td: status-text(:item="skyView.left.simulator")
          td: status-text(:item="skyView.center.simulator")
          td: status-text(:item="skyView.right.simulator")

    h3 Machines
    table: tbody
      template(v-for="(components, title) in others")
        tr(v-for="(component, index) in components")
          td(v-if="index === 0", :rowspan="components.length") {{title}}
          td {{component.displayName}}
          td: status-text(:item="component")

</template>

<script>
const axios = require("axios");
const firebase = require("firebase");
require("firebase/firestore");

import {BACKEND_URL} from '../../project.config.js';
import StatusText from './StatusText.vue';
const TIMEOUT = 60 * 1000; // 1m

export default {
  components: {StatusText},
  data() {
    return {
      isReady: false,
      isError: false,
      overallState: undefined,  // used to track change
      skyView: {},  // format: {[direction]: {projector: {status, description}, simulator: {status, description}}
      others: {},  // format: {[machine]:{displayName, status, description}}
      progress: 0,
    }
  },
  created() {
    this.getStatus();
    this.interval = setInterval(() => {this.getStatus()}, 1000);
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
  methods: {
    getStatus(){
      axios.get(BACKEND_URL + '/config').then((response) => {
        this.isError = false;
        const data = response.data;
        this.progress = this.countProgress(data.machines);
        this.updateOverallState(data.state, this.progress);
        this.updateEachDevice(data.machines);
        this.isReady = true;
      })
      .catch((err) => {
        console.error(err);
        this.isError = true;
      });
    },
    updateOverallState(state, progress){
      // If the overallState is undefined, then it's the first load
      if (!this.overallState) {
        this.overallState = state;
        this.$emit('updateOverallState', {state, progress: this.progress, isInit: true});
      }

      // When the state changed from non-X to X, we say the X action just
      // finished, and update the parent.
      else if (this.overallState !== 'OFF' && state === 'OFF') {
        this.$emit('updateOverallState', {state});
        this.log('Turned off successfully');
        this.overallState = state;
        this.setTransientTimer(false);
      }
      else if (this.overallState !== 'ON' && state === 'ON') {
        this.$emit('updateOverallState', {state});
        this.log('Turned on successfully');
        this.overallState = state;
        this.setTransientTimer(false);
      }
      // We keep send if the state is TRANSIENT, unless it's TIMEOUT
      // TIMEOUT is a state for frontend only, it's created in setTransientTimer
      else if (this.overallState !== 'TIMEOUT' && state === 'TRANSIENT') {
        this.$emit('updateOverallState', {state, progress});
        this.overallState = state;
        this.setTransientTimer(true);
      }
      else if (this.overallState === state) {/* Do nothing */}
      else if (this.overallState === 'TIMEOUT' && state === 'TRANSIENT') {/* Do nothing */}
      else {
        this.isError = true;
        this.$emit('updateOverallState', {state});
        this.log('Abnormal state' + state);
        this.overallState = state;
      }
    },
    countProgress(machines) {
      let total = 0;
      let finished = 0;
      machines.forEach((machine) => {
        machine.components.forEach((component) => {
          if (component.status) total ++;
          if (component.status === 'ON') finished ++;
        })
      });
      return Math.round(finished / total * 100) + '%';
    },
    setTransientTimer(isStarting) {
      // This is a function for controlling a timer, which tracks if the
      // TRANSIENT state stay for longer than 1 min.
      
      // isStarting == false means the system is ON or OFF now. Stop the timeout timer
      if (!isStarting) {
        clearTimeout(this.transientTimer);
        this.transientTimer = undefined;
      }
      // If isStarting (i.e. the state if TRANSIENT) and we don't have a timer,
      // then we start a timer.
      else if (!this.transientTimer) {
        this.transientTimer = setTimeout(() => {
          this.overallState = 'TIMEOUT'
          this.$emit('updateOverallState', {state: 'TIMEOUT', progress: this.progress});
        }, TIMEOUT);
      }
    },
    updateEachDevice(machines) {
      machines.forEach(machine => {
        switch (machine.name) {
          case 'SkyView - Left':
          case 'SkyView - Center':
          case 'SkyView - Right':
            let direction;
            if (machine.name.indexOf('Left') !== -1) direction = 'left';
            if (machine.name.indexOf('Center') !== -1) direction = 'center';
            if (machine.name.indexOf('Right') !== -1) direction = 'right';

            const skyViewStatusOneDirection = {
              projector: machine.components.filter(component => component.displayName === 'Projector')[0],
              simulator: machine.components.filter(component => component.displayName === 'Simulator')[0],
            };
            this.$set(this.skyView, direction, skyViewStatusOneDirection);
            break;
          case 'Avionics Controller':
          case 'Cockpit':
          case 'Instructor Console':
            // format: {displayName, status, description}
            this.$set(this.others, machine.name, machine.components.filter(component => component.displayName));
            break;
        }
      });
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
h3 {
  margin-top: 20px;
}

table {
  transition: opacity .5s ease;
  width: 100%;
  padding: 0 20px 20px;
  font-weight: 500;
}
tr {
  background: #222;
}
td {
  text-transform: capitalize;
}
td, th {
  padding: 6px;
}


.-fade {
  opacity: .4;
}
</style>
