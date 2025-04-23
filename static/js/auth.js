function checkAuth(requiredUserType = 'Staff') {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const userType = localStorage.getItem('user_type');

    if (!token) {
        window.location.href = '/login/';
        return false;
    }

    if (userType !== requiredUserType) {
        window.location.href = '/login/';
        return false;
    }

    $.ajaxSetup({
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('access_token'));
        }
    });

    $(document).ajaxError(function (event, jqxhr, settings, thrownError) {
        if (jqxhr.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                refreshAccessToken(refreshToken).then(success => {
                    if (success) {
                        // Re-run the original request
                        $.ajax(settings);
                    } else {
                        handleSessionExpiry();
                    }
                });
            } else {
                handleSessionExpiry();
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
            console.log(response)
            localStorage.setItem('access_token', response.access);
            return true;
        })
        .catch(() => {
            return false;
        });
}

function handleSessionExpiry() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login/';
}
