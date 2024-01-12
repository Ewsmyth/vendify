const usernameInput = document.getElementById('usernameInput');
const submitButtonUsername = document.getElementById('submitBtnUsername');

usernameInput.addEventListener('input', () => {
  if (usernameInput.value.trim() !== '') {
    submitButtonUsername.style.display = 'block'; // Show the submit button
  } else {
    submitButtonUsername.style.display = 'none'; // Hide the submit button
  }
});

// Get references to the input fields and submit button for password change
const currentPasswordInput = document.getElementById('current_password');
const newPasswordInput = document.getElementById('new_password');
const confirmNewPasswordInput = document.getElementById('confirm_new_password');
const submitButtonPassword = document.getElementById('submitBtnPassword');

// Function to check if all fields are filled for password change
function checkPasswordInputs() {
  const currentPasswordValue = currentPasswordInput.value.trim();
  const newPasswordValue = newPasswordInput.value.trim();
  const confirmNewPasswordValue = confirmNewPasswordInput.value.trim();

  if (
    currentPasswordValue !== '' &&
    newPasswordValue !== '' &&
    confirmNewPasswordValue !== ''
  ) {
    submitButtonPassword.style.display = 'block'; // Show the submit button
    submitButtonPassword.disabled = false; // Enable the submit button
  } else {
    submitButtonPassword.style.display = 'none'; // Hide the submit button
    submitButtonPassword.disabled = true; // Disable the submit button
  }
}

// Add event listeners to input fields for password change
currentPasswordInput.addEventListener('input', checkPasswordInputs);
newPasswordInput.addEventListener('input', checkPasswordInputs);
confirmNewPasswordInput.addEventListener('input', checkPasswordInputs);

// Deactivate account confirmation logic
const deactivateButton = document.getElementById('deactivateBtn');
const deactivateForm = document.getElementById('deactivateForm');

deactivateButton.addEventListener('click', function(event) {
  event.preventDefault(); // Prevents the default form submission behavior

  const confirmation = confirm("Are you sure you want to deactivate your account?");

  if (confirmation) {
    // If user confirms, submit the form
    deactivateForm.submit();
  } else {
    // If user cancels, do nothing or provide additional feedback
    console.log("Deactivation canceled!");
    // You can add more logic here if needed, such as showing a message to the user
  }
});
