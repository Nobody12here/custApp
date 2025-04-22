// /static/js/auth.js

function checkAuth(requiredUserType = 'Staff') {
    const token = localStorage.getItem('access_token');
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

    // Add token to all AJAX requests
    $.ajaxSetup({
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + token);
        },
        statusCode: {
            401: function () {
                swal("Session Expired", "Please log in again.", "warning")
                    .then(() => {
                        localStorage.removeItem('access_token'); // optional: clear token
                        window.location.href = '/login/';
                    });
            }
        }
    });

    return true;
}
