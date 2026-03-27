// Firebase configuration (You need to update this with your actual config from Firebase Console)
// 1. Go to Firebase Console -> Project Settings -> General
// 2. Scroll down to "Your apps" and copy the firebaseConfig object
const firebaseConfig = {
    apiKey: "AIzaSyD8MkYqraaK3nLZdOk8-fP8bdFkxUk6I2A",
    authDomain: "my-app-login-bb197.firebaseapp.com",
    projectId: "my-app-login-bb197",
    storageBucket: "my-app-login-bb197.firebasestorage.app",
    messagingSenderId: "522885122",
    appId: "1:522885122:web:041c7fbb9f12f01702af1b",
    measurementId: "G-7PWFHCH51X"
};

// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// Get DOM Elements
const loginForm = document.getElementById('login-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const googleLoginBtn = document.getElementById('google-login-btn');
const loginBtn = document.getElementById('login-btn');

// 1. Login with Email and Password
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value;
    const password = passwordInput.value;
    
    // Change button text to show loading
    const originalText = loginBtn.innerHTML;
    loginBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Logging in...</span>';
    loginBtn.disabled = true;

    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        console.log("Logged in user:", user);
        alert("เข้าสู่ระบบด้วยอีเมลสำเร็จ!");
        
        // Redirect to dashboard
        window.location.href = "/";
    } catch (error) {
        console.error("Login Error:", error.code, error.message);
        
        // Match error codes
        let errorMessage = "เกิดข้อผิดพลาดในการเข้าสู่ระบบ\nรหัสข้อผิดพลาด: " + error.code + "\n" + error.message;
        if (error.code === 'auth/invalid-credential' || error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
            errorMessage = "อีเมลหรือรหัสผ่านไม่ถูกต้อง";
        }
        
        alert(errorMessage);
    } finally {
        // Reset button state
        loginBtn.innerHTML = originalText;
        loginBtn.disabled = false;
    }
});

// 2. Login with Google
googleLoginBtn.addEventListener('click', async () => {
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        console.log("Google user:", user);
        alert(`เข้าสู่ระบบด้วย Google สำเร็จ!\nยินดีต้อนรับคุณ ${user.displayName}`);
        
        // Redirect to dashboard
        window.location.href = "/";
    } catch (error) {
        console.error("Google Login Error:", error.code, error.message);
        alert("เกิดข้อผิดพลาดในการเข้าสู่ระบบด้วย Google");
    }
});
