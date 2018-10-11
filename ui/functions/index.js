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


const functions = require('firebase-functions');
const nodemailer = require('nodemailer');
const admin = require('firebase-admin');
const TO_EMAIL = ;
const FROM_EMAIL = ;

admin.initializeApp(functions.config().firebase);

/**
 * Fetch the password from the database.
 * @return {!Promise} The firestore get promise.
 */
const fetchPassword = () => {
  return admin.firestore().collection('secret').doc('emailPassword').get().then(doc => {
    const data = doc.data();
    console.log('secret' + JSON.stringify(data));
    return data.password;
  });
}

/**
 * Create an nodemailer transport and send an email.
 * @param {string} feedback The text user entered in the UI.
 * @return {!Promise} The nodemainer send promise.
 */
const sendFeedbackEmail = (subject, feedback) => {
  return fetchPassword().then(password => {
    const mailTransport = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: FROM_EMAIL,
        pass: password,
      },
    });

    const mailOptions = {
      to: [TO_EMAIL],
      subject: `[FlightLab] New ${subject} received`,
      text: `${feedback}`,
    };

    return mailTransport.sendMail(mailOptions)
  })
}

/**
 * A firestore trigger which runs when new feedback is created.
 */
exports.sendNoticationForNewFeedback = functions.firestore.document('feedbacks/{id}').onCreate((snap) => {
  const value = snap.data();
  console.log(value)
  if (value.text) {
    return sendFeedbackEmail('feedback', value.text).then(() => {
      console.log('Email sent!')
    });
  }
  else {
    console.log('No text. Skipping email.')
    return Promise.resolve();
  }
});

exports.sendNoticationForNewIssue = functions.firestore.document('known_issues/user_input').onWrite((change) => {
  const value = change.after.data()
  console.log(value)
  if (value.title) {
    return sendFeedbackEmail('issue', value.title).then(() => {
      console.log('Email sent!')
    });
  }
  else {
    console.log('No text. Skipping email.')
    return Promise.resolve();
  }
});
