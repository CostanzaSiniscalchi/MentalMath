let currentStep = 0;

function renderStep(step) {
  const stepData = tutorialSteps[step];

  document.getElementById("instruction-text").innerText = stepData.text;
  document.getElementById("diagram-img").src = imgBaseUrl + stepData.img;
  document.getElementById("next-btn").innerText = stepData.button;

  const youTry = document.getElementById("you-try-interaction");

  if (
    stepData.text.includes("Now you try") &&
    stepData.img === "you_try.png"
  ) {
    youTry.style.display = "block";
    setupDragAndDrop();
  } else {
    youTry.style.display = "none";
  }
}



document.addEventListener("DOMContentLoaded", () => {
  renderStep(currentStep);

  document.getElementById("next-btn").addEventListener("click", () => {
    currentStep++;
    if (currentStep < tutorialSteps.length) {
      renderStep(currentStep);
    } else {
      window.location.href = `/practice/${unitId}/easy`;
    }
  });
});

