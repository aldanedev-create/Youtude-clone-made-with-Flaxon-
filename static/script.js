// Like button
document.addEventListener('click', async function(e) {
    const likeBtn = e.target.closest('.like-btn');
    if (likeBtn) {
        const videoId = likeBtn.dataset.videoId;
        const likeCount = likeBtn.querySelector('.like-count');

        try {
            const response = await fetch(`/api/videos/${videoId}/like`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                likeCount.textContent = data.likes;
                likeBtn.classList.toggle('liked');
            } else if (response.status === 401) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error liking video:', error);
        }
    }
});

// Comment button
document.addEventListener('click', async function(e) {
    const commentBtn = e.target.closest('#comment-btn');
    if (commentBtn) {
        const videoId = commentBtn.dataset.videoId;
        const input = document.getElementById('comment-input');
        const text = input.value.trim();

        if (!text) return;

        try {
            const response = await fetch(`/api/videos/${videoId}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.comment) {
                    const commentsList = document.querySelector('.comments-list');
                    const noComments = commentsList.querySelector('.no-comments');
                    if (noComments) noComments.remove();

                    const commentDiv = document.createElement('div');
                    commentDiv.className = 'comment';
                    commentDiv.innerHTML = `
                        <strong>${data.comment.username}</strong>
                        <span class="comment-date">${data.comment.created_at}</span>
                        <p>${data.comment.text}</p>
                    `;
                    commentsList.prepend(commentDiv);
                    input.value = '';
                }
            } else if (response.status === 401) {
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error posting comment:', error);
        }
    }
});

// View counter
document.addEventListener('DOMContentLoaded', function() {
    const videoPlayer = document.querySelector('video');
    if (videoPlayer) {
        const videoId = document.querySelector('.like-btn')?.dataset.videoId;
        if (videoId) {
            fetch(`/api/videos/${videoId}/view`, { method: 'POST' });
        }
    }
});

// Upload form
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(uploadForm);
            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress-bar');
            const progressText = document.getElementById('progress-text');
            const statusDiv = document.getElementById('upload-status');

            progressContainer.style.display = 'flex';
            progressBar.style.width = '0%';
            progressText.textContent = '0%';
            statusDiv.innerHTML = '';

            try {
                const response = await fetch('/api/videos', {
                    method: 'POST',
                    body: formData
                });

                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }

                const data = await response.json();

                if (data.success) {
                    statusDiv.innerHTML = `
                        <div style="background: #065f46; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            ✅ Video uploaded successfully!
                            <br>
                            <a href="/watch/${data.video_id}" style="color: #6ee7b7;">Watch now</a>
                        </div>
                    `;
                    progressBar.style.width = '100%';
                    progressText.textContent = '100%';
                    uploadForm.reset();
                } else {
                    statusDiv.innerHTML = `
                        <div style="background: #7f1d1d; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                            ❌ Upload failed. Please try again.
                        </div>
                    `;
                }
            } catch (error) {
                statusDiv.innerHTML = `
                    <div style="background: #7f1d1d; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                        ❌ Upload failed: ${error.message}
                    </div>
                `;
            } finally {
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                }, 3000);
            }
        });
    }
});