import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

// Firebase configuration
// TODO: Replace with actual Firebase web app config from Firebase Console
// Go to: https://console.firebase.google.com/project/aim-cdac/settings/general
// Add a web app and copy the config here
const firebaseConfig = {
    apiKey: "AIzaSyAZ-GhL_Lw-DWHH2yyoyzwixt3kp9B767I",
    authDomain: "aim-cdac.firebaseapp.com",
    projectId: "aim-cdac",
    storageBucket: "aim-cdac.firebasestorage.app",
    messagingSenderId: "567512428101",
    appId: "1:567512428101:web:f44a5b2bfe31968c89fd2c",
    measurementId: "G-CW2NQ2YVGG"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app; 