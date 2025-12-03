
// -------------------------------
// MAIN.JS FOR RAILWAY RESERVATION SYSTEM
// -------------------------------

// Wait for DOM to load
document.addEventListener("DOMContentLoaded", function () {

    // -------------------------------
    // 1. LOGIN FORM VALIDATION
    // -------------------------------
    const loginForm = document.querySelector("#login-form");

    if (loginForm) {
        loginForm.addEventListener("submit", function (e) {
            const email = document.querySelector("#email").value.trim();
            const password = document.querySelector("#password").value.trim();

            if (email === "" || password === "") {
                showAlert("Please fill all fields", "error");
                e.preventDefault();
            }
        });
    }

    // -------------------------------
    // 2. REGISTER FORM VALIDATION
    // -------------------------------
    const registerForm = document.querySelector("#register-form");

    if (registerForm) {
        registerForm.addEventListener("submit", function (e) {
            const pass = document.querySelector("#password").value.trim();
            const cpass = document.querySelector("#confirm_password").value.trim();
            const phone = document.querySelector("#phone").value.trim();

            // Phone number validation (basic)
            if (phone.length !== 10 || isNaN(phone)) {
                showAlert("Invalid phone number!", "error");
                e.preventDefault();
                return;
            }

            // Password match check
            if (pass !== cpass) {
                showAlert("Passwords do not match!", "error");
                e.preventDefault();
            }
        });

        // Live password matching indicator
        const password = document.querySelector("#password");
        const confirm_password = document.querySelector("#confirm_password");

        if (password && confirm_password) {
            confirm_password.addEventListener("input", () => {
                if (password.value !== confirm_password.value) {
                    confirm_password.style.border = "2px solid red";
                } else {
                    confirm_password.style.border = "2px solid green";
                }
            });
        }
    }

    // -------------------------------
    // 3. TRAIN SEARCH BUTTON HANDLER
    // -------------------------------
    const searchBtn = document.querySelector("#search-btn");

    if (searchBtn) {
        searchBtn.addEventListener("click", function () {
            const src = document.querySelector("#source").value;
            const dest = document.querySelector("#destination").value;
            const date = document.querySelector("#date").value;

            if (!src  !dest  !date) {
                showAlert("Please fill all fields to search train!", "error");
                return;
            }

            // Optional: animate loading
            searchBtn.innerText = "Searching...";
            setTimeout(() => {
                searchBtn.innerText = "Search";
            }, 1000);
        });
    }

    // -------------------------------
    // 4. SEAT CLASS SELECTOR LOGIC
    // -------------------------------
    const classSelect = document.querySelector("#class-select");

    if (classSelect) {
        classSelect.addEventListener("change", function () {
            const selected = classSelect.value;
            console.log("Selected class:", selected);
        });
    }

    // -------------------------------
    // 5. AI CHAT WIDGET (Optional)
    // -------------------------------
    const chatToggle = document.querySelector("#ai-chat-toggle");
    const chatBox = document.querySelector("#ai-chat-box");

    if (chatToggle && chatBox) {
        chatToggle.addEventListener("click", () => {
            chatBox.classList.toggle("active");
        });

        const aiSendBtn = document.querySelector("#ai-send-btn");
        const aiInput = document.querySelector("#ai-input");
        const aiMessages = document.querySelector("#ai-messages");

Anushka Tiwari, [02-12-2025 18:40]
if (aiSendBtn && aiInput) {
            aiSendBtn.addEventListener("click", () => {
                const msg = aiInput.value.trim();
                if (!msg) return;
                
                aiMessages.innerHTML += <div class="user-msg">${msg}</div>;
                aiInput.value = "";

                // Placeholder response
                setTimeout(() => {
                    aiMessages.innerHTML += <div class="bot-msg">AI Assistant: I'm processing your request...</div>;
                }, 500);
            });
        }
    }

});


// -------------------------------
// GLOBAL HELPER FUNCTIONS
// -------------------------------

// Fancy alert message
function showAlert(message, type = "success") {
    const alertBox = document.createElement("div");
    alertBox.className = custom-alert ${type};
    alertBox.innerText = message;

    document.body.appendChild(alertBox);

    setTimeout(() => {
        alertBox.style.opacity = "0";
    }, 2000);

    setTimeout(() => {
        alertBox.remove();
    }, 3000);
}