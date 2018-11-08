/*
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
*/

/**
 * @fileoverview The entry file for webpack. Sets up Vue (including Vuetify and
 * Vue Router), Firebase and bootstrap the vue app. 
 */

// Required to run the app.
export const BACKEND_URL = ;  // e.g. http://192.168.1.1:8080 or http://localhost:8000
export const FIREBASE_CONFIG = ;  // The firebase config object. https://firebase.google.com/docs/web/setup
export const HAS_BADGE_READER = ;  // A boolean value. If false, we show a button to start.

// Optional - for the calendar feature.
export const CLIENT_ID = ;  // Google Cloud OAuth client id
export const API_KEY = ;  // Google Cloud project API key
export const CALENDAR_ID = ;   // Calendar ID. (You can find it in Google Calendar settings.)
