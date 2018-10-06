# flight_lab_control

This is the user facing app for the flight simulator. It controls the system and
shows basic status information.

## Overall tech stack
- vue.js: main framework
- Firebase Firestore: the database
- Vuetify: material design library for vue.js

## Project setup

1. Set up Firebase project.
  1. Create a [Firebase](console.firebase.google.com) project.
  1. Enable Database -> Firestore.
  1. From Firebase console page: Add app -> Web. Copy the config object into `project.config.js`.
1. Set up Calendar access.
  1. Open [Google Cloud](https://console.cloud.google.com/) and open the project you created in Firebase.
  1. APIs & Services -> API library. Enable the Google Calendar API.
  1. APIs & Services -> Credentials. Create an API key and an OAuth client ID (Web client).
  1. Copy the API key and the ClientId to `project.config.js`.
  1. Update `CALENDAR_ID` in `project.config.js`.
1. Set up bug reporting.
  1. Update the TO_EMAIL and FROM_EMAIL in `/functions/index.js`.
1. Update the `BACKEND_URL` in `project.config.js`.

## App Development

``` bash
# install dependencies
npm install

# run locally
npm start
```

## Deployment the notification cloud function

1. Init the app using firebase CLI.
1. Update the CONTACT_EMAIL in `/functions/index.js`.
1. Build the bundle by `npm run build`.
1. Deploy the cloud function by `firebase deploy --only functions`.
1. Optionally, you can deploy the app, and visit yourdomain.com/docs to view the checklists.

## Database(Firestore) structure

- `known_issues`: A list of issues. Each document has one field - `title`. There's a special document `user_input`, which gets updated by the user.
- `feedbacks`: A list of feedbacks. Each document has four fields - `rating`, `text`, `timestamp`, `isArchived`.
- `logs`: A list of logs. Each document has three fields - `action`, `isError`, `timestamp`.
