// Import Firebase libraries and use exact config from your web app
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyD8MkYqraaK3nLZdOk8-fP8bdFkxUk6I2A",
    authDomain: "my-app-login-bb197.firebaseapp.com",
    projectId: "my-app-login-bb197",
    storageBucket: "my-app-login-bb197.firebasestorage.app",
    messagingSenderId: "522885122",
    appId: "1:522885122:web:041c7fbb9f12f01702af1b",
    measurementId: "G-7PWFHCH51X"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const registerForm = document.getElementById('register-form');
const emailInput = document.getElementById('reg-email');
const passwordInput = document.getElementById('reg-password');
const registerBtn = document.getElementById('register-btn');

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value;
    const password = passwordInput.value;
    
    // UI Update
    const originalText = registerBtn.innerHTML;
    registerBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Creating account...</span>';
    registerBtn.disabled = true;

    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        alert("สมัครสมาชิกสำเร็จ! กำลังพาท่านเข้าสู่ระบบ...");
        window.location.href = "/";
    } catch (error) {
        console.error("Register Error:", error.code, error.message);
        let errorMessage = "เกิดข้อผิดพลาดในการสมัครสมาชิก\nรหัสข้อผิดพลาด: " + error.code + "\n" + error.message;
        if (error.code === 'auth/email-already-in-use') {
            errorMessage = "อีเมลนี้มีผู้ใช้งานแล้ว";
        } else if (error.code === 'auth/weak-password') {
            errorMessage = "รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร";
        }
        alert(errorMessage);
    } finally {
        registerBtn.innerHTML = originalText;
        registerBtn.disabled = false;
    }
});
