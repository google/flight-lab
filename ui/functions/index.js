/**
 * @fileoverview Firebase cloud functions.
 */

const functions = require('firebase-functions');
const nodemailer = require('nodemailer');
const admin = require('firebase-admin');
const CONTACT_EMAIL = <YOUE_EMAIL_HERE>;

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
        user: 'gflightsim.email@gmail.com',
        pass: password,
      },
    });

    const mailOptions = {
      to: [CONTACT_EMAIL],
      subject: `[FligheLab] New ${subject} received`,
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
