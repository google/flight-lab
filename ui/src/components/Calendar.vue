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
.calendar
  template(v-if="!isError")
    p(v-if="current") Current reservation: {{current.person}}, <b class="warning--text">{{current.remaining}}</b> remaining.
    p(v-if="next") Next reservation: {{next.person}} starts in <b class="warning--text">{{next.remaining}}</b>.
    p(v-else) (No upcoming reservation today.)
  p(v-else) Cannot get Calendar info. See console. Try force refresh.
</template>


<script>
import moment from 'moment'
import {CLIENT_ID, API_KEY, CALENDAR_ID} from '../../project.config.js';
const DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"];
const SCOPES = "https://www.googleapis.com/auth/calendar.readonly";

export default {
  data() {
    return {
      current: undefined,
      next: undefined,
      events: [],
      isError: false,
    }
  },
  created() {
    this.initGapi();
    this.calendarInterval = setInterval(() => {this.fetchCalendar()}, 10 * 60 * 1000);  // 10 min
    this.displayInterval = setInterval(() => {this.displayTime()}, 60 * 1000);  // 1 min
  },
  beforeDestroy() {
    clearInterval(this.calendarInterval);
    clearInterval(this.displayInterval);
  },
  methods: {
    initGapi() {
      const initClient = () => {
        gapi.client.init({
          apiKey: API_KEY,
          clientId: CLIENT_ID,
          discoveryDocs: DISCOVERY_DOCS,
          scope: SCOPES
        }).then(function () {
          gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);
          updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
        }, (error) => {
          this.isError = true;
          console.error(error);
        });
      }

      const updateSigninStatus = (isSignedIn) => {
        if (isSignedIn) this.fetchCalendar();
        else gapi.auth2.getAuthInstance().signIn().catch(error => {
          this.isError = true;
          console.error(error);
        });
      }

      gapi.load('client:auth2', initClient);
    },
    fetchCalendar(){
      gapi.client.calendar.events.list({
        'calendarId': CALENDAR_ID,
        'timeMin': moment().toISOString(),
        'showDeleted': false,
        'singleEvents': true,
        'maxResults': 10,
        'orderBy': 'startTime'
      }).then((response) => {
        this.events = response.result.items
        this.displayTime();
      }, (error) => {
        this.isError = true;
        console.error(error);
      });
    },
    displayTime() {
      if (!this.events || !this.events.length) {
        this.next = undefined;
        this.current = undefined;
      }
      else {
        const now = moment();
        for (let i = 0; i < this.events.length; i ++) {
          if (moment(this.events[i].start.dateTime || this.events[i].start.date).diff(now) < 0 &&
              moment(this.events[i].end.dateTime || this.events[i].end.date).diff(now) > 0) {
            // event[i] is happening
            this.current = this.getEventEntry(this.events[i], 'end');
            this.next = this.getEventEntry(this.events[i + 1], 'start');
            break;
          }
          else if (moment(this.events[i].start.dateTime || this.events[i].start.date).diff(now) > 0) {
            // evnet[i] is in the future. since the loop is not broken, we don't have any events before this.
            this.current = undefined;
            this.next = this.getEventEntry(this.events[i], 'start');
            break;
          }
        }
      }
    },
    getEventEntry(event, type) {
      if (!event || !event[type]) return;
      const remaining = this.calTime(event[type].dateTime || event[type].date);
      if (!remaining) return undefined;
      else {
        const person = event.creator || {};
        let personString;
        if (person.displayName && person.email) personString = `${person.displayName} (${person.email.replace('google.com', '')})`;
        else if (person.displayName) personString = person.displayName;
        else if (person.email) personString = person.email.replace('google.com', '');
        else personString = '(Privete)';
        return {
          person: personString,
          remaining,
        }
      }
    },
    calTime(untilTimeString) {
      const untilTime = moment(untilTimeString);
      const now = moment();
      const minutes = untilTime.diff(now, 'minutes');
      if (untilTime.date() !== now.date()) return undefined;

      if (minutes > 60) {
        return `${Math.floor(minutes / 60)} h ${minutes % 60} min`;
      }
      else {
        return `${minutes} min`;
      }
    },
  },
};
</script>

<style scoped>
.calendar {
  padding: 1em;
}

p {
  margin: 0;
}
</style>
