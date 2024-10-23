function likePost(postId) {
    const csrftoken = getCookie('csrftoken');  // Get CSRF token
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Add CSRF token to headers
        },
        body: JSON.stringify({
            post_id: postId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const likeBtn = document.querySelector(`button[data-post-id="${postId}"]`);
            likeBtn.innerHTML = `Like (${data.likes_count})`;  // Update the like count dynamically
        }
    })
    .catch(error => console.error('Error:', error));
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
