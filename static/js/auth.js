function checkAuth(requiredUserType = 'Staff') {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const userType = localStorage.getItem('user_type');

    if (!token) {
        swal("Unauthorized", "You must be logged in to continue.", "warning")
            .then(() => {
                window.location.href = '/login/';
            });
        return false;
    }

    if (userType !== requiredUserType) {
        swal("Access Denied", "You are not authorized to access this page.", "error")
            .then(() => {
                window.location.href = '/login/';
            });
        return false;
    }

    // Setup AJAX to include token and handle 401 errors
    $.ajaxSetup({
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('access_token'));
        },
        statusCode: {
            401: function () {
                // Try refreshing the token
                console.log(refreshToken)
                if (refreshToken) {
                    refreshAccessToken(refreshToken).then(success => {
                        if (success) {
                            location.reload(); // retry the last action if necessary
                        } else {
                            handleSessionExpiry();
                        }
                    });
                } else {
                    handleSessionExpiry();
                }
            }
        }
    });

    return true;
}

function refreshAccessToken(refreshToken) {
    return $.ajax({
        url: '/api/token/refresh/', // Update this to your actual refresh endpoint
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ refresh: refreshToken })
    })
    .then(response => {
        localStorage.setItem('access_token', response.access);
        return true;
    })
    .catch(() => {
        return false;
    });
}

function handleSessionExpiry() {

    swal("Session Expired", "Please log in again.", "warning")
        .then(() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/';
        });
}
