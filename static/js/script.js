// top button
var topButton = document.getElementById("top");

window.onscroll = function() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    topButton.style.display = "block";
  } else {
    topButton.style.display = "none";
  }
};

function topFunction() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}

// validate feedback form

function validateForm() {
  var nameInput = document.getElementById('inputName');
  var feedbackInput = document.getElementById('inputFeedback');
  var nameWarning = document.getElementById('nameWarning');
  var feedbackWarning = document.getElementById('feedbackWarning');
  var isValid = true;

  // Reset previous warnings
  nameWarning.textContent = '';
  feedbackWarning.textContent = '';

  // Check if Name is not entered
  if (nameInput.value.trim() === '') {
    nameWarning.textContent = 'Name is required.';
    isValid = false;
  }

  // Check if Feedback is not entered
  if (feedbackInput.value.trim() === '') {
    feedbackWarning.textContent = 'Feedback is required.';
    isValid = false;
  }

  return isValid;
}

// welcome mesage

document.addEventListener("DOMContentLoaded", function() {
  // Check if the welcome message has already been displayed
  if (!document.cookie.includes("visited=true") && !sessionStorage.getItem('welcomeMessageDisplayed')) {
      // Create the welcome message element
      var welcomeMessage = document.createElement('div');
      welcomeMessage.className = 'alert alert-info alert-dismissible fade show';
      welcomeMessage.innerHTML = '<b>Welcome to our beta release testing program! Please give us your feedback.</b><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';

      // Append the element to the container
      var container = document.getElementById('welcome-message-container');

      if (container) {
          container.appendChild(welcomeMessage);
      }

      // Set a cookie to track the user's visit
      document.cookie = "visited=true; max-age=604800"; // Expires in 1 week

      // Set a session storage flag to indicate that the welcome message has been displayed
      sessionStorage.setItem('welcomeMessageDisplayed', 'true');
  }
});
