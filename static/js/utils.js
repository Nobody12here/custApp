function fetchUserProfilePicture() {
  $.ajax({
    url: `/users/`,
    type: "GET",
    success: function (data) {
      console.log(data);
      userId = data.user_id;
      $("#name").val(data.name || "");
      $("#email").val(data.email || "");
      $("#phone").val(data.phone_number || "");
      $("#cnic").val(data.CNIC || "");
      $("#designation").val(data.designation || "");

      if (data.picture) {
        console.log(data.picture);
        $("#profileImagePreview").attr("src", data.picture);
      }
      if (data.signature) {
        $("#signatureImagePreview").attr("src", data.signature);
      }
    },
    error: function () {
      alert("Failed to load profile data.");
    },
  });
}

function fetchDepartments() {
  $.ajax({
    url: "/departments/",
    type: "GET",
    dataType: "json",
    success: function (data) {
      const $departmentSelect = $("#department");
      $departmentSelect.html(`<option value="">Select Department</option>`);
      data.forEach(department => {
        $departmentSelect.append(
          `<option value="${department.dept_id}">${department.dept_name}</option>`
        );
      });
    },
    error: function (xhr, status, error) {
      console.error("Error fetching departments:", error);
      $("#department").html(`<option value="">Failed to load departments</option>`);
    }
  });
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

function populateDepartmentHead() {
  const departmentId = $("#department").val();
  $.ajax({
    url: `/users/?department=${departmentId}&user_type=Staff`,
    dataType: 'json',
    success: function (data) {
      const deptHead = $('#dept_head');
      deptHead.empty();
      deptHead.prop('disabled', false);
      deptHead.append('<option value="">Select Staff</option>');
      data.forEach(user => {
        deptHead.append(`<option value="${user.user_id}">${user.name}</option>`);
      });
    },
    error: function (xhr, status, error) {
      console.error(error)
    }
  })
}