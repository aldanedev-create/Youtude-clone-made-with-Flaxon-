// ============================================================
// Like Button Handler
// ============================================================
document.addEventListener('click', async function(e) {
    const likeBtn = e.target.closest('.like-btn');
    if (!likeBtn || likeBtn.disabled) return;

    const videoId = likeBtn.dataset.videoId;
    const likeCount = likeBtn.querySelector('.like-count');

    try {
        likeBtn.disabled = true;
        const response = await fetch(`/api/videos/${videoId}/like`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const data = await response.json();
            if (likeCount) likeCount.textContent = data.likes;
            likeBtn.classList.toggle('liked');
        } else if (response.status === 401) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error liking video:', error);
    } finally {
        likeBtn.disabled = false;
    }
});

// ============================================================
// Comment Submission Handler
// ============================================================
document.addEventListener('click', async function(e) {
    const commentBtn = e.target.closest('#comment-btn');
    if (!commentBtn || commentBtn.disabled) return;

    const videoId = commentBtn.dataset.videoId;
    const input = document.getElementById('comment-input');
    if (!input) return;

    const text = input.value.trim();
    if (!text) return;

    try {
        commentBtn.disabled = true;
        const response = await fetch(`/api/videos/${videoId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.comment) {
                const commentsList = document.querySelector('.comments-list');
                if (commentsList) {
                    const noComments = commentsList.querySelector('.no-comments');
                    if (noComments) noComments.remove();

                    // Safely construct DOM elements to prevent XSS attacks
                    const commentDiv = document.createElement('div');
                    commentDiv.className = 'comment';

                    const usernameElem = document.createElement('strong');
                    usernameElem.textContent = data.comment.username;

                    const dateElem = document.createElement('span');
                    dateElem.className = 'comment-date';
                    dateElem.textContent = ` ${data.comment.created_at}`;

                    const textElem = document.createElement('p');
                    textElem.textContent = data.comment.text;

                    commentDiv.appendChild(usernameElem);
                    commentDiv.appendChild(dateElem);
                    commentDiv.appendChild(textElem);

                    commentsList.prepend(commentDiv);
                    input.value = '';
                }
            }
        } else if (response.status === 401) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Error posting comment:', error);
    } finally {
        commentBtn.disabled = false;
    }
});

// ============================================================
// View Counter Initialization
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const videoPlayer = document.querySelector('video');
    if (videoPlayer) {
        const videoId = document.querySelector('.like-btn')?.dataset.videoId;
        if (videoId) {
            fetch(`/api/videos/${videoId}/view`, { method: 'POST' }).catch(err => {
                console.error('Error tracking view:', err);
            });
        }
    }
});

// ============================================================
// Upload Form Handler (with true XHR Upload Progress)
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    if (!uploadForm) return;

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(uploadForm);
        const progressContainer = document.getElementById('progress-container');
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const statusDiv = document.getElementById('upload-status');
        const submitBtn = uploadForm.querySelector('button[type="submit"]');

        if (progressContainer) progressContainer.style.display = 'flex';
        if (progressBar) progressBar.style.width = '0%';
        if (progressText) progressText.textContent = '0%';
        if (statusDiv) statusDiv.innerHTML = '';
        if (submitBtn) submitBtn.disabled = true;

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api/videos', true);

        // Upload Progress Listener
        xhr.upload.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                if (progressBar) progressBar.style.width = `${percent}%`;
                if (progressText) progressText.textContent = `${percent}%`;
            }
        };

        xhr.onload = function() {
            if (submitBtn) submitBtn.disabled = false;

            if (xhr.status === 401) {
                window.location.href = '/login';
                return;
            }

            try {
                const data = JSON.parse(xhr.responseText);
                if (xhr.status >= 200 && xhr.status < 300 && data.success) {
                    if (statusDiv) {
                        statusDiv.innerHTML = `
                            <div style="background: #065f46; color: #fff; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                ✅ Video uploaded successfully!
                                <br>
                                <a href="/watch/${data.video_id}" style="color: #6ee7b7; text-decoration: underline;">Watch now</a>
                            </div>
                        `;
                    }
                    if (progressBar) progressBar.style.width = '100%';
                    if (progressText) progressText.textContent = '100%';
                    uploadForm.reset();
                } else {
                    const errorMsg = data.error?.message || data.message || 'Upload failed. Please try again.';
                    if (statusDiv) {
                        statusDiv.innerHTML = `
                            <div style="background: #7f1d1d; color: #fff; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                ❌ ${errorMsg}
                            </div>
                        `;
                    }
                }
            } catch (e) {
                if (statusDiv) {
                    statusDiv.innerHTML = `
                        <div style="background: #7f1d1d; color: #fff; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            ❌ Server return invalid response.
                        </div>
                    `;
                }
            } finally {
                setTimeout(() => {
                    if (progressContainer) progressContainer.style.display = 'none';
                }, 3000);
            }
        };

        xhr.onerror = function() {
            if (submitBtn) submitBtn.disabled = false;
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div style="background: #7f1d1d; color: #fff; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        ❌ Network error during upload. Please check your connection.
                    </div>
                `;
            }
            if (progressContainer) progressContainer.style.display = 'none';
        };

        xhr.send(formData);
    });
});
