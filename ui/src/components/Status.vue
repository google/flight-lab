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
    template(v-for="(group, groupTitle) in machines")
      h3 {{groupTitle}}
      table: tbody
        template(v-for="machine in group")
          tr(v-for="(component, index) in machine.components")
            td(v-if="index === 0", :rowspan="machine.components.length", :title="machine.description") {{machine.displayName}}
            td(:title="component.description") {{component.displayName}}
            td: status-text(:status="component.status")

</template>

<script>
const firebase = require("firebase");
require("firebase/firestore");

import {STREAMING_URL} from '../../project.config.js';
import StatusText from './StatusText.vue';
const TIMEOUT_STATE = -1;
const TIMEOUT = 60 * 1000; // 1m
let STREAMING;

export default {
  components: {StatusText},
  data() {
    return {
      isReady: true,
      isError: false,
      overallState: undefined,  // used to track change
      machines: {},  // [groupName]: {displayName, description, components: [{displayName, description, status}]}
      countComponent: 0,
      countActive: 0,
    }
  },
  created() {
    this.startStreaming();
  },
  beforeDestroy() {
    STREAMING.cancel('data');
  },
  methods: {
    startStreaming() {
      console.info(proto);
      const service = new proto.flightlab.ControlServiceClient(STREAMING_URL);
      service.getConfig(new proto.google.protobuf.Empty(), {}, (err, response) => {
        this.parseConfig(response);
      });
      STREAMING = service.watchConfig(new proto.google.protobuf.Empty(), {});
      STREAMING.on('data', this.parseConfig);
    },
    parseConfig(config) {
      const temp = {};
      this.countComponent = 0;
      this.countActive = 0;
      config.getMachinesList().forEach((machine) => {
        const groupName = machine.getGroupname();
        temp[groupName] = temp[groupName] || [];
        temp[groupName].push({
          displayName: machine.getName(),
          description: machine.getDescription(),
          components: this.parseMachine(machine),
        });
      });
      this.machines = temp;
      // Parse system after machine, so that we have the counts for progress ready.
      this.parseSystem(config.getState());
    },
    parseMachine(machine) {
      return machine.getComponentsList()
      .filter(component => component.getDisplayName())
      .map(component => {
        const displayName = component.getDisplayName();
        const status = this.getStatus(component);
        // Update count for progress
        this.countComponent ++;
        if (status === proto.flightlab.Component.Status.ON) this.countActive ++;
        return {displayName, status};
      });
    },
    getStatus(component) {
      const getName = (allStatus, status) => {
        for (let name in allStatus) {
          if (allStatus[name] === status) return name;
        }
        return null;
      };
      switch(component.getKindCase()) {
        case proto.flightlab.Component.KindCase.APP:
          return getName(proto.flightlab.App.Status, component.getApp().getStatus());
        case proto.flightlab.Component.KindCase.BADGER:
          return getName(proto.flightlab.Badger.Status, component.getBadger().getStatus());
        case proto.flightlab.Component.KindCase.PROJECTOR:
          return getName(proto.flightlab.Projector.Status, component.getProjector().getStatus());
        case proto.flightlab.Component.KindCase.WINDOWS_APP:
          return getName(proto.flightlab.WindowsApp.Status, component.getWindowsApp().getStatus());
        default:
          return null;
      }
    },
    parseSystem(state){
      // If the overallState is undefined, then it's the first load
      if (!this.overallState) {
        this.overallState = state;
        this.$emit('updateOverallState', {state, progress: this.countActive / this.countComponent, isInit: true});
      }

      // When the state changed from non-X to X, we say the X action just
      // finished, and update the parent.
      else if (this.overallState !== proto.flightlab.System.State.OFF && state === proto.flightlab.System.State.OFF) {
        this.$emit('updateOverallState', {state});
        this.log('Turned off successfully');
        this.overallState = state;
        this.setTransientTimer(false);
      }
      else if (this.overallState !== proto.flightlab.System.State.ON && state === proto.flightlab.System.State.ON) {
        this.$emit('updateOverallState', {state});
        this.log('Turned on successfully');
        this.overallState = state;
        this.setTransientTimer(false);
      }
      // We keep send if the state is TRANSIENT, unless it's TIMEOUT
      // TIMEOUT is a state for frontend only, it's created in setTransientTimer
      else if (this.overallState !== TIMEOUT_STATE && state === proto.flightlab.System.State.TRANSIENT) {
        this.$emit('updateOverallState', {state, progress: this.countActive / this.countComponent});
        this.overallState = state;
        this.setTransientTimer(true);
      }
      else if (this.overallState === state) {/* Do nothing */}
      else if (this.overallState === TIMEOUT_STATE && state === proto.flightlab.System.State.TRANSIENT) {/* Do nothing */}
      else {
        this.isError = true;
        this.$emit('updateOverallState', {state});
        this.log('Abnormal state' + state);
        this.overallState = state;
      }
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
          this.overallState = TIMEOUT_STATE
          this.$emit('updateOverallState', {state: TIMEOUT_STATE, progress: this.countActive / this.countComponent});
        }, TIMEOUT);
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
