document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function(event) {
            const fileInput = document.querySelector("input[type='file']");
            if (!fileInput.files.length) {
                alert("Please select a file.");
                event.preventDefault();
            } else if (!fileInput.files[0].name.match(/\.(pdf|docx)$/i)) {
                alert("Please upload a PDF or DOCX file.");
                event.preventDefault();
            }
        });
    }
});