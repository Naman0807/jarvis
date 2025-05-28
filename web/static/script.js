// JARVIS Configuration UI JavaScript

// Toggle password visibility
function togglePassword(elementId) {
	const input = document.getElementById(elementId);
	if (input.type === "password") {
		input.type = "text";
	} else {
		input.type = "password";
	}
}

// Update slider value display
function updateSliderValue(elementId, value) {
	document.getElementById(elementId).textContent = value;
}

// Add a new application entry
function addApp() {
	const container = document.getElementById("applications-container");
	const appEntries = container.querySelectorAll(".app-entry");
	const newIndex = appEntries.length + 1;

	const appDiv = document.createElement("div");
	appDiv.className = "app-entry";
	appDiv.innerHTML = `
        <input type="text" name="app_name_${newIndex}" placeholder="App Name">
        <input type="text" name="app_command_${newIndex}" placeholder="Command">
        <button type="button" class="remove-app" onclick="removeApp(this)">×</button>
    `;

	container.appendChild(appDiv);
}

// Remove application entry
function removeApp(button) {
	const appEntry = button.parentElement;
	appEntry.parentElement.removeChild(appEntry);
	renumberApps();
}

// Renumber app entries after removal
function renumberApps() {
	const container = document.getElementById("applications-container");
	const appEntries = container.querySelectorAll(".app-entry");

	appEntries.forEach((entry, index) => {
		const inputs = entry.querySelectorAll("input");
		inputs[0].name = `app_name_${index + 1}`;
		inputs[1].name = `app_command_${index + 1}`;
	});
}

// Test webcam functionality
function testWebcam() {
	const modal = document.getElementById("webcam-modal");
	const video = document.getElementById("webcam");
	const webcamIndex = document.getElementById("webcam_index").value;

	modal.style.display = "block";

	navigator.mediaDevices
		.getUserMedia({
			video: {
				deviceId: webcamIndex,
			},
		})
		.then((stream) => {
			video.srcObject = stream;
		})
		.catch((error) => {
			alert("Error accessing webcam: " + error.message);
		});
}

// Close webcam test modal
function closeWebcamTest() {
	const modal = document.getElementById("webcam-modal");
	const video = document.getElementById("webcam");

	if (video.srcObject) {
		const tracks = video.srcObject.getTracks();
		tracks.forEach((track) => track.stop());
		video.srcObject = null;
	}

	modal.style.display = "none";
}

// Test JARVIS functionality
function testJarvis() {
	fetch("/test_jarvis", {
		method: "POST",
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.success) {
				alert("JARVIS is working! You should hear a voice response.");
			} else {
				alert("Error testing JARVIS: " + data.error);
			}
		})
		.catch((error) => {
			alert("Error testing JARVIS: " + error);
		});
}

// Initialize on document load
document.addEventListener("DOMContentLoaded", function () {
	// Ensure all range sliders have their values displayed
	const rangeInputs = document.querySelectorAll('input[type="range"]');
	rangeInputs.forEach((input) => {
		const valueId = input.id + "_value";
		updateSliderValue(valueId, input.value);
	});

	// Close modal when clicking outside
	window.onclick = function (event) {
		const modal = document.getElementById("webcam-modal");
		if (event.target == modal) {
			closeWebcamTest();
		}
	};
});
