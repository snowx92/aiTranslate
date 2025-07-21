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
        
        // Add TTS (speak) button for assistant messages
        if (!isUser && text.trim()) {
            const speakButton = document.createElement('button');
            speakButton.className = 'speak-button btn btn-sm btn-outline-primary ms-2';
            speakButton.innerHTML = '<i class="bi bi-volume-up"></i>';
            speakButton.title = 'Listen to translation';
            speakButton.addEventListener('click', () => playTextToSpeech(text, speakButton));
            messageDiv.appendChild(speakButton);
        }
        
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

    pdfFileInput.addEventListener('change', async function () {
        const file = pdfFileInput.files[0];
        if (!file) return;
    
        fileNameDisplay.textContent = file.name;
        progressBar.style.display = 'block';
        progressBarInner.style.width = '0%';
    
        const formData = new FormData();
        formData.append('file', file);
    
        try {
            const response = await fetch('/upload-pdf', {
                method: 'POST',
                body: formData,
            });
    
            const data = await response.json();
            console.log(data)
            if (data.error) {
                throw new Error(data.error);
            }
    
            // ✅ Ensure 'text' exists before splitting
            if (!data.text) {
                console.log('No text extracted from PDF');
            }
    
            const lines = data.sentences; // Use the array directly
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
                        
                        // Better error messages for common issues
                        let errorMessage = error.message;
                        if (errorMessage.includes('Rate limit exceeded') || errorMessage.includes('429')) {
                            errorMessage = 'OpenAI API rate limit reached. Please wait a few minutes and try again. Consider upgrading your OpenAI plan for higher limits.';
                        } else if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
                            errorMessage = 'OpenAI API key issue. Please check your API key configuration.';
                        } else if (errorMessage.includes('network') || errorMessage.includes('timeout')) {
                            errorMessage = 'Network error. Please check your internet connection and try again.';
                        }
                        
                        alert('Audio processing failed: ' + errorMessage);
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


// Function to get chat messages
function getChatMessages() {
    const messages = document.querySelectorAll('.message');
    const chatData = [];

    let lastUserMessage = '';

    messages.forEach((msg) => {
        if (msg.classList.contains('user-message')) {
            lastUserMessage = msg.querySelector('.message-content').textContent;
        } else if (msg.classList.contains('assistant-message')) {
            const translatedText = msg.querySelector('.message-content').textContent;
            chatData.push([lastUserMessage, translatedText]);
            lastUserMessage = '';
        }
    });

    return chatData;
}

// Function to get chat messages for backend export (PDF/server-side exports)
function getChatMessagesForExport() {
    const messages = document.querySelectorAll('.message');
    const chatData = [];
    const sourceLang = document.getElementById('sourceLang').value;
    const targetLang = document.getElementById('targetLang').value;

    let lastUserMessage = '';

    messages.forEach((msg) => {
        if (msg.classList.contains('user-message')) {
            lastUserMessage = msg.querySelector('.message-content').textContent;
        } else if (msg.classList.contains('assistant-message')) {
            const translatedText = msg.querySelector('.message-content').textContent;
            chatData.push({
                original: lastUserMessage,
                translated: translatedText,
                source_lang: sourceLang,
                target_lang: targetLang
            });
            lastUserMessage = '';
        }
    });

    return chatData;
}
// Event listeners
// Function to export to Excel
function exportToExcel(chatData) {
    const ws = XLSX.utils.json_to_sheet(chatData.map(row => ({
        'Original Text': row[0],
        'Translated Text': row[1]
    })));

    // Set column widths
    const maxWidths = chatData.reduce((acc, row) => ({
        A: Math.max(acc.A, row[0].length),
        B: Math.max(acc.B, row[1].length)
    }), { A: 15, B: 15 });

    ws['!cols'] = [
        { wch: maxWidths.A },
        { wch: maxWidths.B }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Chat Export");
    XLSX.writeFile(wb, "translated_chat.xlsx");
}

// Function to export to Word with table
async function exportToWordTable(chatData) {
    const { Document, Packer, Paragraph, Table, TableRow, TableCell, AlignmentType, WidthType, TableBorders, BorderStyle } = window.docx;

    const doc = new Document({
        sections: [{
            properties: {},
            children: [
                new Table({
                    width: {
                        size: 9000,
                        type: WidthType.DXA,
                    },
                    borders: {
                        top: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
                        bottom: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
                        left: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
                        right: { style: BorderStyle.SINGLE, size: 1, color: "000000" },
                    },
                    rows: [
                        new TableRow({
                            tableHeader: true,
                            children: [
                                new TableCell({
                                    width: {
                                        size: 4500,
                                        type: WidthType.DXA,
                                    },
                                    shading: {
                                        fill: "D7E4BC",
                                    },
                                    children: [new Paragraph({ 
                                        text: "Original Text",
                                        alignment: AlignmentType.CENTER,
                                    })],
                                }),
                                new TableCell({
                                    width: {
                                        size: 4500,
                                        type: WidthType.DXA,
                                    },
                                    shading: {
                                        fill: "D7E4BC",
                                    },
                                    children: [new Paragraph({ 
                                        text: "Translated Text",
                                        alignment: AlignmentType.CENTER,
                                    })],
                                }),
                            ],
                        }),
                        ...chatData.map(row => 
                            new TableRow({
                                children: [
                                    new TableCell({
                                        width: {
                                            size: 4500,
                                            type: WidthType.DXA,
                                        },
                                        children: [new Paragraph({ 
                                            text: row[0],
                                            alignment: AlignmentType.LEFT,
                                        })],
                                    }),
                                    new TableCell({
                                        width: {
                                            size: 4500,
                                            type: WidthType.DXA,
                                        },
                                        children: [new Paragraph({ 
                                            text: row[1],
                                            alignment: AlignmentType.RIGHT,
                                            bidirectional: true,
                                        })],
                                    }),
                                ],
                            })
                        ),
                    ],
                }),
            ],
        }],
    });

    const blob = await Packer.toBlob(doc);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'translated_chat_table.docx';
    link.click();
    URL.revokeObjectURL(url);
}

// Function to export to Word text only
async function exportToWordText(chatData) {
    const doc = new docx.Document({
        sections: [{
            properties: {},
            children: chatData.map(row => [
                new docx.Paragraph({
                    children: [
                        new docx.TextRun({
                            text: row[1],
                            bold: true,
                            bidirectional: true,
                        }),
                    ],
                    alignment: docx.AlignmentType.RIGHT,
                }),
                new docx.Paragraph({}),
            ]).flat(),
        }],
    });

    const blob = await docx.Packer.toBlob(doc);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'translated_chat_text.docx';
    link.click();
    URL.revokeObjectURL(url);
}
pdfMake.fonts = {
    Amiri: {
        normal: 'Amiri-Regular.ttf',
        bold: 'Amiri-Bold.ttf',
    }
};


document.querySelectorAll('.export-option').forEach(item => {
    item.addEventListener('click', async function() {
        const fileType = this.getAttribute('data-type');

        if (fileType === 'pdf-table' || fileType === 'pdf-text') {
            fetchAndExportPDF(fileType);
        } else {
            const chatData = getChatMessages();
            
            if (chatData.length === 0) {
                alert("No messages to export.");
                return;
            }

            switch(fileType) {
                case 'excel':
                    exportToExcel(chatData);
                    break;
                case 'word-table':
                    exportToWordTable(chatData);
                    break;
                case 'word-text':
                    exportToWordText(chatData);
                    break;
                default:
                    console.error('Unknown export type:', fileType);
            }
        }
    });
});

// Function to fetch data from Flask and export as PDF
async function fetchAndExportPDF(fileType) {
    const apiUrl = fileType === 'pdf-table' ? '/export/pdf_table' : '/export/pdf_text';

    try {
        // Use the correct data format for backend export
        const chatData = getChatMessagesForExport();
        
        if (chatData.length === 0) {
            alert("No messages to export.");
            return;
        }

        console.log("Sending chat data to backend:", chatData); // Debug log

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_data: chatData }) // Using the correct format
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.statusText}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileType === 'pdf-table' ? 'translated_chat_table.pdf' : 'translated_chat_text.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        console.log("PDF export successful!"); // Success log
    } catch (error) {
        console.error("Failed to export PDF:", error);
        alert("Error exporting PDF: " + error.message);
    }
}

// Text-to-Speech functionality
async function playTextToSpeech(text, button) {
    const originalIcon = button.innerHTML;
    
    try {
        // Show loading state
        button.innerHTML = '<i class="bi bi-arrow-clockwise spinner-border spinner-border-sm"></i>';
        button.disabled = true;
        
        const response = await fetch('/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                voice: 'alloy',  // You can make this configurable
                model: 'tts-1'
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'TTS request failed');
        }

        // Get audio blob
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Create and play audio
        const audio = new Audio(audioUrl);
        
        // Show playing state
        button.innerHTML = '<i class="bi bi-pause-fill"></i>';
        button.title = 'Audio playing...';
        
        audio.play();
        
        // Handle audio end
        audio.addEventListener('ended', () => {
            button.innerHTML = originalIcon;
            button.disabled = false;
            button.title = 'Listen to translation';
            URL.revokeObjectURL(audioUrl);
        });
        
        // Handle audio errors
        audio.addEventListener('error', () => {
            throw new Error('Failed to play audio');
        });
        
    } catch (error) {
        console.error('TTS error:', error);
        
        // Better error messages for TTS issues
        let errorMessage = error.message;
        if (errorMessage.includes('Rate limit exceeded') || errorMessage.includes('429')) {
            errorMessage = 'OpenAI TTS rate limit reached. Please wait a few minutes before using text-to-speech again.';
        } else if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
            errorMessage = 'OpenAI API key issue. Please check your configuration.';
        } else if (errorMessage.includes('network') || errorMessage.includes('timeout')) {
            errorMessage = 'Network error. Please check your connection and try again.';
        }
        
        alert('Text-to-speech failed: ' + errorMessage);
        
        // Reset button state
        button.innerHTML = originalIcon;
        button.disabled = false;
        button.title = 'Listen to translation';
    }
}