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

function submitRating(bookId) {
    const ratingValue = document.getElementById(`rating-${bookId}`).value;
    const csrftoken = getCookie('csrftoken');

    fetch(`/rate-book/${bookId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'rating': ratingValue })  // Send rating data as JSON
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Rating submitted! New Rating: ${data.new_rating} stars`);
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => console.error('Error:', error));
}
