"""Translation page with camera capture and feedback functionality."""

import streamlit as st
import streamlit.components.v1 as components

# Get user_id from session state (default to an empty string if not found)
user_id = st.session_state.get("user_id", "")

html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Camera Capture with Enhanced Features</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
    }}
    .container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 20px;
    }}
    video {{
      width: 60%;
      max-width: 600px;
    }}
    button {{
      margin-top: 10px;
      padding: 10px;
      cursor: pointer;
    }}
    #predictionText {{
      margin-top: 20px;
      font-size: 1.2rem;
      font-weight: bold;
    }}
    #progressBarContainer {{
      width: 60%;
      height: 20px;
      background-color: #eee;
      margin: 10px 0;
      position: relative;
    }}
    #progressBar {{
      width: 0%;
      height: 100%;
      background-color: #4CAF50;
    }}
    #feedbackButtons {{
      margin-top: 20px;
    }}
    .feedbackButton {{
      margin: 0 10px;
      padding: 10px 20px;
      cursor: pointer;
    }}
    #feedbackMessage {{
      margin-top: 10px;
      font-size: 1rem;
      font-weight: bold;
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Inject user_id for use in JavaScript -->
    <script>
      const USER_ID = "{user_id}";
      console.log("Active user_id:", USER_ID);
    </script>

    <video id="video" autoplay playsinline></video>
    <div id="progressBarContainer">
      <div id="progressBar"></div>
    </div>
    <button id="captureBtn">Start Recording</button>
    <p id="predictionText"></p>
    <div id="feedbackButtons">
      <button class="feedbackButton" id="likeBtn" disabled>Like</button>
      <button class="feedbackButton" id="dislikeBtn" disabled>Dislike</button>
    </div>
    <p id="feedbackMessage" style="display: none;"></p>
  </div>

  <script>
    const video = document.getElementById("video");
    const captureBtn = document.getElementById("captureBtn");
    const predictionText = document.getElementById("predictionText");
    const progressBar = document.getElementById("progressBar");
    const likeBtn = document.getElementById("likeBtn");
    const dislikeBtn = document.getElementById("dislikeBtn");
    const feedbackMessage = document.getElementById("feedbackMessage");

    // Get user permission and attach webcam stream
    navigator.mediaDevices.getUserMedia({{ video: true }})
      .then(stream => {{
        video.srcObject = stream;
      }})
      .catch(err => console.error("Error accessing camera:", err));

    // Handle capture button click
    captureBtn.addEventListener("click", () => {{
      startCountdown(3);
      captureBtn.disabled = true;
    }});

    function startCountdown(seconds) {{
      let remaining = seconds;
      captureBtn.textContent = `Starting in ${{remaining}}s`;
      const interval = setInterval(() => {{
        remaining -= 1;
        captureBtn.textContent = remaining > 0 ? `Starting in ${{remaining}}s` : "Recording...";
        if (remaining <= 0) {{
          clearInterval(interval);
          startRecording();
        }}
      }}, 1000);
    }}

    function startRecording() {{
      const frames = [];
      const framesToCapture = 30;
      const intervalDelay = 100; // Capture every 100ms
      let frameCount = 0;

      const intervalID = setInterval(() => {{
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        frames.push(canvas.toDataURL("image/png"));
        frameCount++;
        updateProgressBar(frameCount, framesToCapture);

        if (frameCount >= framesToCapture) {{
          clearInterval(intervalID);
          sendFrames(frames);
        }}
      }}, intervalDelay);
    }}

    function updateProgressBar(current, total) {{
      const percentage = (current / total) * 100;
      progressBar.style.width = percentage + "%";
    }}

    function sendFrames(frames) {{
      // Pass user_id to the backend along with frames
      fetch("http://localhost/translate", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          frames: frames,
          user_id: USER_ID
        }})
      }})
      .then(response => response.json())
      .then(data => {{
        predictionText.textContent = `Prediction: ${{data.prediction}}`;
        likeBtn.disabled = false;
        dislikeBtn.disabled = false;

        likeBtn.addEventListener("click", () => {{
          sendFeedback(data.recording_id, 1); // Like (1)
        }});

        dislikeBtn.addEventListener("click", () => {{
          sendFeedback(data.recording_id, 0); // Dislike (0)
        }});
      }})
      .catch(error => {{
        console.error("Error sending frames:", error);
        predictionText.textContent = "Error sending frames.";
      }});
    }}

    function sendFeedback(recordingId, feedback) {{
      feedbackMessage.style.display = "block";
      feedbackMessage.style.color = "black";

      // Pass user_id to the backend along with feedback
      fetch("http://localhost/feedback", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          recording_id: recordingId,
          feedback: feedback,
          user_id: USER_ID
        }})
      }})
      .then(response => {{
        if (response.ok) {{
          feedbackMessage.textContent = "Thank you for your feedback!";
          feedbackMessage.style.color = "green";
        }} else {{
          feedbackMessage.textContent = "Failed to send feedback. Please try again.";
          feedbackMessage.style.color = "red";
        }}
        resetUI();
        setTimeout(() => {{
          feedbackMessage.textContent = "";
        }}, 2000);
      }})
      .catch(error => {{
        console.error("Error sending feedback:", error);
        feedbackMessage.textContent = "Error sending feedback. Please try again.";
        feedbackMessage.style.color = "red";
        resetUI();
        setTimeout(() => {{
          feedbackMessage.textContent = "";
        }}, 2000);
      }});
    }}

    function resetUI() {{
      likeBtn.disabled = true;
      dislikeBtn.disabled = true;
      progressBar.style.width = "0%";
      predictionText.textContent = "";
      captureBtn.textContent = "Start Recording";
      captureBtn.disabled = false;
    }}
  </script>
</body>
</html>
"""

# Use components.html to display your custom HTML/JS in Streamlit
components.html(html_code, height=700, scrolling=True)

st.write("---")
st.write("**Instructions**:")
st.write("1. Allow camera access (a prompt may appear).")
st.write("2. Click 'Start Recording'.")
st.write("3. Provide feedback on the prediction using the Like/Dislike buttons.")
