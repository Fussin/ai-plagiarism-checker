document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Plagiarism Checker frontend initialized.');

    // API Base URL
    const API_BASE_URL = 'http://127.0.0.1:8000';

    // --- DOM Elements ---
    // Auth
    const signupEmailInput = document.getElementById('signup-email');
    const signupPasswordInput = document.getElementById('signup-password');
    const signupButton = document.getElementById('signup-button');
    const loginEmailInput = document.getElementById('login-email');
    const loginPasswordInput = document.getElementById('login-password');
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');
    const userInfoDiv = document.getElementById('user-info');
    const userEmailDisplay = document.getElementById('user-email-display');
    const authSectionDiv = document.getElementById('auth-section');

    // Checker Sections
    const checkerSectionDiv = document.getElementById('checker-section');

    // Text Checker
    const textInput = document.getElementById('text-input');
    const checkTextButton = document.getElementById('check-text-button');

    // Text File Checker
    const textFileInput = document.getElementById('text-file-input');
    const checkTextFileButton = document.getElementById('check-text-file-button');

    // Image File Checker
    const imageFileInput = document.getElementById('image-file-input');
    const checkImageFileButton = document.getElementById('check-image-file-button');

    // Video File Checker
    const videoFileInput = document.getElementById('video-file-input');
    const checkVideoFileButton = document.getElementById('check-video-file-button');

    // Results
    const reportOutputDiv = document.getElementById('report-output');

    let authToken = localStorage.getItem('authToken');

    // --- UI Update Functions ---
    function updateAuthUI() {
        if (authToken) {
            authSectionDiv.querySelectorAll('#signup-form, #login-form').forEach(el => el.style.display = 'none');
            userInfoDiv.style.display = 'block';
            checkerSectionDiv.style.display = 'block';
            reportOutputDiv.innerHTML = '<p>Ready to check content.</p>';
        } else {
            authSectionDiv.querySelectorAll('#signup-form, #login-form').forEach(el => el.style.display = 'block');
            userInfoDiv.style.display = 'none';
            userEmailDisplay.textContent = '';
            checkerSectionDiv.style.display = 'none';
            reportOutputDiv.innerHTML = '<p>Please log in to use the checker.</p>';
        }
    }

    // --- API Helper ---
    async function fetchWithAuth(url, options = {}) {
        const headers = { ...options.headers };
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
        }

        const response = await fetch(url, { ...options, headers });

        if (response.status === 401) {
            localStorage.removeItem('authToken');
            authToken = null;
            updateAuthUI();
            alert("Session expired or invalid. Please login again.");
            throw new Error("Unauthorized");
        }
        return response;
    }

    async function fetchUserDetails() {
        if (!authToken) return;
        try {
            const response = await fetchWithAuth(`${API_BASE_URL}/auth/users/me`);
            if (response.ok) {
                const userData = await response.json();
                userEmailDisplay.textContent = userData.email;
            } else {
                console.error("Failed to fetch user details. Status:", response.status);
                localStorage.removeItem('authToken');
                authToken = null;
                updateAuthUI();
            }
        } catch (error) {
            console.error("Error fetching user details:", error);
            if (error.message !== "Unauthorized") {
                alert("Could not fetch user details. You might be logged out.");
            }
        }
    }

    // --- Event Listeners (Auth) ---
    if (signupButton) {
        signupButton.addEventListener('click', async () => {
            const email = signupEmailInput.value;
            const password = signupPasswordInput.value;
            if (!email || !password) { alert("Please enter both email and password for signup."); return; }
            try {
                const response = await fetch(`${API_BASE_URL}/auth/signup`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await response.json();
                if (response.ok) {
                    authToken = data.access_token;
                    localStorage.setItem('authToken', authToken);
                    alert('Signup successful! You are now logged in.');
                    updateAuthUI();
                    fetchUserDetails();
                } else { alert(`Signup failed: ${data.detail || 'Unknown error'}`); }
            } catch (error) { console.error('Signup error:', error); alert('Signup request failed.'); }
        });
    }

    if (loginButton) {
        loginButton.addEventListener('click', async () => {
            const email = loginEmailInput.value;
            const password = loginPasswordInput.value;
            if (!email || !password) { alert("Please enter both email and password for login."); return; }
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);
            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData.toString()
                });
                const data = await response.json();
                if (response.ok) {
                    authToken = data.access_token;
                    localStorage.setItem('authToken', authToken);
                    alert('Login successful!');
                    updateAuthUI();
                    fetchUserDetails();
                } else { alert(`Login failed: ${data.detail || 'Unknown error'}`); }
            } catch (error) { console.error('Login error:', error); alert('Login request failed.'); }
        });
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            localStorage.removeItem('authToken');
            authToken = null;
            alert('Logged out.');
            updateAuthUI();
        });
    }

    // --- Generic File Check Function ---
    async function handleFileCheck(fileInputElement, endpoint, checkTypeMessage) {
        if (!authToken) { alert(`Please login to check ${checkTypeMessage} files.`); return; }
        const file = fileInputElement.files[0];
        if (!file) { alert(`Please select a ${checkTypeMessage} file to check.`); return; }

        reportOutputDiv.innerHTML = `<p><i>Uploading and checking ${checkTypeMessage} file...</i></p>`;
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetchWithAuth(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (response.ok) { displayReport(result); }
            else { reportOutputDiv.innerHTML = `<p class="error">Error: ${result.detail || `Failed to check ${checkTypeMessage} file.`}</p>`; }
        } catch (error) {
            console.error(`${checkTypeMessage} file check error:`, error);
            if (error.message !== "Unauthorized") { reportOutputDiv.innerHTML = `<p class="error">Request failed: ${error.message}</p>`; }
        }
    }

    // --- Checker Event Listeners ---
    if (checkTextButton) {
        checkTextButton.addEventListener('click', async () => {
            if (!authToken) { alert("Please login to check content."); return; }
            const text = textInput.value;
            if (!text.trim()) { alert("Please enter some text to check."); return; }
            reportOutputDiv.innerHTML = '<p><i>Checking text...</i></p>';
            try {
                const response = await fetchWithAuth(`${API_BASE_URL}/check/text`, {
                    method: 'POST',
                    body: JSON.stringify({ text })
                });
                const result = await response.json();
                if (response.ok) { displayReport(result); }
                else { reportOutputDiv.innerHTML = `<p class="error">Error: ${result.detail || 'Failed to check text.'}</p>`; }
            } catch (error) {
                console.error('Text check error:', error);
                if (error.message !== "Unauthorized") { reportOutputDiv.innerHTML = `<p class="error">Request failed: ${error.message}</p>`; }
            }
        });
    }

    if (checkTextFileButton) {
        checkTextFileButton.addEventListener('click', () => handleFileCheck(textFileInput, '/check/file', 'text'));
    }

    if (checkImageFileButton) {
        checkImageFileButton.addEventListener('click', () => handleFileCheck(imageFileInput, '/check/image', 'image'));
    }

    if (checkVideoFileButton) {
        checkVideoFileButton.addEventListener('click', () => handleFileCheck(videoFileInput, '/check/video', 'video'));
    }

    // --- Display Report Function ---
    function displayReport(result) {
        let html = `<h3>Plagiarism Report</h3>`;
        html += `<p><strong>Originality Score:</strong> ${(result.originality_score * 100).toFixed(2)}%</p>`;

        if (result.matched_sources && result.matched_sources.length > 0) {
            html += `<h4>Details & Matched Sources:</h4><ul>`;
            result.matched_sources.forEach(source => {
                const cleanSource = String(source).replace(/</g, "&lt;").replace(/>/g, "&gt;");
                html += `<li>${cleanSource}</li>`;
            });
            html += `</ul>`;
        } else {
            html += `<p>No specific matches found based on current checks.</p>`;
        }

        if (result.rewrite_suggestions && result.rewrite_suggestions.length > 0) {
            html += `<h4>Rewrite Suggestions:</h4><ul>`;
            result.rewrite_suggestions.forEach(suggestion => {
                const cleanSuggestion = String(suggestion).replace(/</g, "&lt;").replace(/>/g, "&gt;");
                html += `<li>${cleanSuggestion}</li>`;
            });
            html += `</ul>`;
        }
        reportOutputDiv.innerHTML = html;
    }

    // --- Initial Page Load Setup ---
    updateAuthUI();
    if (authToken) {
        fetchUserDetails();
    }
});
