// Firebase Authentication Module
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const app = initializeApp(window.firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

export async function googleSignIn() {
    console.log("Google Sign-In button clicked");
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        const idToken = await user.getIdToken();
        
        // Send idToken to backend to create a session
        const response = await fetch('/api/auth/firebase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idToken })
        });
        
        if (response.ok) {
            window.location.href = '/dashboard.html';
        } else {
            console.error('Backend authentication failed');
            alert('Sign-in failed. Please try again.');
        }
    } catch (error) {
        console.error('Google Sign-In Error:', error);
        alert('Google Sign-In Error: ' + error.message);
    }
}

window.firebaseAuth = { googleSignIn, signOut: () => signOut(auth) };
