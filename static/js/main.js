document.addEventListener('DOMContentLoaded', function () {
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const submitButton = document.getElementById('submitButton');
    const pdfFileInput = document.getElementById('pdfFile');
    const fileNameDisplay = document.getElementById('fileName');
    const progressBar = document.getElementById('progressBar');
    const progressBarInner = progressBar.querySelector('.progress-bar');
    const recordButton = document.getElementById('recordButton');

    let mediaRecorder;
    let audioChunks = [];

    // Function to add message to chat
    function addMessage(text, isUser = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        const icon = document.createElement('i');
        icon.className = `message-icon bi ${isUser ? 'bi-person' : 'bi-robot'}`;
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = text;
        messageDiv.appendChild(icon);
        messageDiv.appendChild(content);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Function to add skeleton loader
    function addSkeletonLoader(isUser = true) {
        const skeletonDiv = document.createElement('div');
        skeletonDiv.className = `skeleton-loader ${isUser ? 'user-message' : 'assistant-message'}`;
        const icon = document.createElement('i');
        icon.className = `message-icon bi ${isUser ? 'bi-person' : 'bi-robot'}`;
        const content = document.createElement('div');
        content.className = 'message-content placeholder-glow';
        content.innerHTML = `
            <span class="placeholder col-8"></span>
        `;
        skeletonDiv.appendChild(icon);
        skeletonDiv.appendChild(content);
        chatContainer.appendChild(skeletonDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return skeletonDiv;
    }

    // Function to translate text
    async function translateText(text, sourceLang, targetLang) {
        console.log("Starting translation...");
        console.log("Input text:", text);
        console.log("Source language:", sourceLang);
        console.log("Target language:", targetLang);

        try {
            console.log("Sending request to /translate endpoint...");
            const response = await fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    sourceLang: sourceLang,
                    targetLang: targetLang
                })
            });

            console.log("Response received. Parsing JSON...");
            const data = await response.json();

            if (!response.ok) {
                console.error("Server returned an error:", data.error);
                throw new Error(data.error || "Failed to fetch translation");
            }

            console.log("Translation successful. Translated text:", data.translation);
            return data.translation;
        } catch (error) {
            console.error('Translation error:', error);
            alert('Translation failed: ' + error.message);
            throw error; // Re-throw the error if needed
        }
    }

    // Handle PDF file upload and translation
    pdfFileInput.addEventListener('change', async function () {
        const file = pdfFileInput.files[0];
        if (!file) return;

        // Show file name and progress bar
        fileNameDisplay.textContent = file.name;
        progressBar.style.display = 'block';
        progressBarInner.style.width = '0%';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload-pdf', {
                method: 'POST',
                body: formData,
                onUploadProgress: (event) => {
                    const progress = Math.round((event.loaded / event.total) * 100);
                    progressBarInner.style.width = `${progress}%`;
                }
            });
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Split text into lines and translate
            const lines = data.text.split('\n');
            const sourceLang = document.getElementById('sourceLang').value;
            const targetLang = document.getElementById('targetLang').value;

            for (const line of lines) {
                if (line.trim()) {
                    addMessage(line, true);
                    const skeleton = addSkeletonLoader(false);
                    const translation = await translateText(line, sourceLang, targetLang);
                    skeleton.remove();
                    addMessage(translation, false);
                }
            }
        } catch (error) {
            console.error('PDF processing error:', error);
            alert('PDF processing failed: ' + error.message);
        } finally {
            progressBar.style.display = 'none';
        }
    });

    // Handle send message
    async function handleSendMessage() {
        const text = messageInput.value.trim();
        if (text) {
            const sourceLang = document.getElementById('sourceLang').value;
            const targetLang = document.getElementById('targetLang').value;

            addMessage(text, true);
            messageInput.value = '';

            const skeleton = addSkeletonLoader(false);
            const translation = await translateText(text, sourceLang, targetLang);
            skeleton.remove();
            if (translation) {
                addMessage(translation, false);
            }
        }
    }

    submitButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });

    // Handle recording
    recordButton.addEventListener('click', async function () {
        if (!mediaRecorder) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('file', audioBlob, 'recording.wav');

                    try {
                        const response = await fetch('/upload-audio', {
                            method: 'POST',
                            body: formData
                        });
                        const data = await response.json();

                        if (data.error) {
                            throw new Error(data.error);
                        }

                        const sourceLang = document.getElementById('sourceLang').value;
                        const targetLang = document.getElementById('targetLang').value;

                        addMessage(data.text, true);
                        const skeleton = addSkeletonLoader(false);
                        const translation = await translateText(data.text, sourceLang, targetLang);
                        skeleton.remove();
                        addMessage(translation, false);
                    } catch (error) {
                        console.error('Audio processing error:', error);
                        alert('Audio processing failed: ' + error.message);
                    } finally {
                        audioChunks = [];
                    }
                };
                mediaRecorder.start();
                recordButton.innerHTML = '<i class="bi bi-stop"></i>';
            } catch (error) {
                console.error('Error accessing microphone:', error);
                alert('Error accessing microphone: ' + error.message);
            }
        } else {
            mediaRecorder.stop();
            mediaRecorder = null;
            recordButton.innerHTML = '<i class="bi bi-mic"></i>';
        }
    });
});