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
            console.log(response.refresh)
            localStorage.setItem('refresh_token',response.refresh)
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
function logout() {
    const refreshToken = localStorage.getItem('refresh_token');

    // Call the logout API if refresh token is available
    if (refreshToken) {
        $.ajax({
            url: '/api/logout/', // Update to your actual logout endpoint if different
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ refresh_token: refreshToken }),
            complete: function () {
                // Clear tokens and redirect to login regardless of API success/failure
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user_type');
                window.location.href = '/login/';
            }
        });
    } else {
        // Just clear and redirect if no refresh token is available
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_type');
        window.location.href = '/login/';
    }
}

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
