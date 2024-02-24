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
<<<<<<< HEAD
}
=======
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

// shaer button
    // Initialize tooltip for the share link
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
>>>>>>> release/2
