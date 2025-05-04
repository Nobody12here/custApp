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
