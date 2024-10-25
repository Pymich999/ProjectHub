// JavaScript function to handle the like button click
function likePost(postId) {
    const csrftoken = getCookie('csrftoken');  // Get CSRF token from cookies

    fetch(`/post/${postId}/like/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Add the CSRF token to the request headers
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the like button with the new like count
            const likeBtn = document.querySelector(`button[data-post-id="${postId}"]`);
            likeBtn.innerHTML = `Like (${data.likes_count})`;
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to retrieve the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

