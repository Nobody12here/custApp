// Validation functions
function showValidationFeedback(inputId, isValid, message) {
    const input = $(`#${inputId}`);
    const feedbackElement = input.siblings('.invalid-feedback, .valid-feedback');

    // Remove existing classes
    input.removeClass('is-valid is-invalid');
    feedbackElement.remove();

    if (isValid) {
        input.addClass('is-valid');
        if (message) {
            input.after(`<div class="valid-feedback">${message}</div>`);
        }
    } else {
        input.addClass('is-invalid');
        input.after(`<div class="invalid-feedback">${message}</div>`);
    }
}

function validateDates() {
    const registrationDate = $('#registrationDate').val();
    const registrationDeadline = $('#registrationDeadline').val();
    const rehearsalDate = $('#rehearsalDate').val();
    const convocationDate = $('#convocationDate').val();
    let isValid = true;

    if (registrationDate && registrationDeadline) {
        if (new Date(registrationDate) >= new Date(registrationDeadline)) {
            showValidationFeedback('registrationDeadline', false, 'Deadline must be after registration start date');
            isValid = false;
        } else {
            showValidationFeedback('registrationDeadline', true, '');
        }
    }

    if (registrationDeadline && rehearsalDate) {
        if (new Date(registrationDeadline) > new Date(rehearsalDate)) {
            showValidationFeedback('rehearsalDate', false, 'Rehearsal date should be after registration deadline');
            isValid = false;
        } else {
            showValidationFeedback('rehearsalDate', true, '');
        }
    }
    if (rehearsalDate && convocationDate) {
        if (new Date(rehearsalDate) >= new Date(convocationDate)) {
            console.log("Rehearsal date:", rehearsalDate, "Convocation date:", convocationDate, " Not valid");
            showValidationFeedback('convocationDate', false, 'Convocation date should be after rehearsal date');
            isValid = false;
        } else {
            console.log("Rehearsal date:", rehearsalDate, "Convocation date:", convocationDate, " Valid");
            showValidationFeedback('convocationDate', true, '');
        }
        return isValid;
    }
}
function validateForm() {
    let isFormValid = true;

    // Validate required fields
    const requiredFields = ['convocationTitle', 'academicYear', 'registrationDate', 'registrationDeadline', 'rehearsalDate', 'rehearsalTime',];

    requiredFields.forEach(fieldId => {
        const value = $(`#${fieldId}`).val();
        if (!value || value.trim() === '') {
            showValidationFeedback(fieldId, false, 'This field is required');
            isFormValid = false;
        } else {
            showValidationFeedback(fieldId, true, '');
        }
    });

    // Validate dates
    if (!validateDates()) {
        isFormValid = false;
    }

    return isFormValid;
}

function loadConvocations(searchTerm = '', showActiveOnly = false) {
    let url = '/convocation/';
    if (showActiveOnly) {
        url += '?active_only=true';
    }

    $.ajax({
        url: url,
        method: 'GET',
        success: function (data) {
            const tbody = $('#convocationTableBody');
            tbody.empty();

            const filteredConvocations = searchTerm ? data.filter(convocation => {
                const searchStr = `${convocation.title} ${convocation.academic_year} ${convocation.status}`.toLowerCase();
                return searchStr.includes(searchTerm.toLowerCase());
            }) : data;

            if (filteredConvocations.length === 0) {
                tbody.html('<tr><td colspan="6" class="text-center">No convocation instances found</td></tr>');
                return;
            }

            filteredConvocations.forEach(convocation => {
                const registrationDeadline = new Date(convocation.registration_deadline);
                const rehearsalDate = new Date(convocation.rehearsal_date);
                const rehearsalTime = convocation.rehearsal_time;

                const deadlineStr = registrationDeadline.toLocaleDateString();
                const rehearsalDateStr = rehearsalDate.toLocaleDateString();

                        let dropdownItems = '';
                        dropdownItems += `<a class="dropdown-item" href="#" onclick="openStudentUploadModal(${convocation.id})">
                            <i class="material-icons">cloud_upload</i> Upload Student Data
                        </a>`;
                        dropdownItems += `<a class="dropdown-item" href="#" onclick="openLetterGenerationModal(${convocation.id})">
                            <i class="material-icons">description</i> Generate Letters
                        </a>`;

                        // If only one convocation instance, add a dummy disabled item for spacing
                        if (filteredConvocations.length === 1) {
                            dropdownItems += `<a class="dropdown-item disabled" tabindex="-1" style="opacity:0;pointer-events:none;">&nbsp;</a>`;
                        }

                        const extraPadding = (filteredConvocations.length === 1) ? 'style="padding-bottom:48px;"' : '';
                        const row = `
                            <tr>
                                <td>${convocation.title}</td>
                                <td>${convocation.academic_year}</td>
                                <td>${deadlineStr}</td>
                                <td>${rehearsalDateStr} ${rehearsalTime}</td>
                                <td>
                                    <span class="status-badge ${convocation.status.toLowerCase()}">
                                        ${convocation.status}
                                    </span>
                                </td>
                                <td ${extraPadding}>
                                    <button class="btn btn-info btn-sm" onclick="viewConvocationDetails(${convocation.id})">
                                        <i class="material-icons">visibility</i> View
                                    </button>
                                    <div class="dropdown d-inline-block ml-2">
                                        <button class="btn btn-secondary btn-sm dropdown-toggle" type="button" id="dropdownMenuButton${convocation.id}" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                            <i class="material-icons">more_vert</i>
                                        </button>
                                        <div class="dropdown-menu" aria-labelledby="dropdownMenuButton${convocation.id}">
                                            ${dropdownItems}
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        `;
                        tbody.append(row);
                    });

                    // Add extra spacing below the table if only one convocation instance
                    const tableContainer = $('#convocationTable').parent();
                    if (filteredConvocations.length === 1) {
                        if ($('#convocation-table-spacer').length === 0) {
                            tableContainer.append('<div id="convocation-table-spacer" style="height: 80px;"></div>');
                        }
                    } else {
                        $('#convocation-table-spacer').remove();
                    }
        },
        error: function () {
            $('#convocationTableBody').html('<tr><td colspan="6" class="text-center">Error loading convocation instances</td></tr>');
        }
    });
}

// File upload functionality
function handleFileUpload() {
    const fileInput = $('#studentDataFile')[0];
    const file = fileInput.files[0];
    console.log(file);
    if (!file) {
        showUploadStatus('error', 'Please select a file to upload');
        return;
    }

    // Validate file type
    const allowedTypes = ['.xlsx', '.xls'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(fileExtension)) {
        showUploadStatus('error', 'Invalid file type. Please select a CSV or Excel file.');
        return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showUploadStatus('error', 'File size too large. Maximum allowed size is 10MB.');
        return;
    }

    const formData = new FormData();
    formData.append('convocation_data', file);

    // Get current convocation ID from modal (you might need to store this when opening modal)
    const convocationId = $('#studentUploadModal').data('convocation-id');
    console.log("Convocation ID:", convocationId);
    if (convocationId) {
        formData.append('convocation_id', convocationId);
    }

    // Show upload progress
    showUploadStatus('info', 'Uploading file...', true);
    $('#uploadStudentDataBtn').prop('disabled', true).html('<i class="material-icons">hourglass_empty</i> Uploading...');

    $.ajax({
        url: '/api/upload-convocation-data/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: formData,
        processData: false,
        contentType: false,
        xhr: function () {
            const xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function (evt) {
                if (evt.lengthComputable) {
                    const percentComplete = Math.round((evt.loaded / evt.total) * 100);
                    updateUploadProgress(percentComplete);
                }
            }, false);
            return xhr;
        },
        success: function (response) {
            const processedCount = response.result.modified || 0;
            const errorCount = response.result.total || 0;

            if (errorCount > 0) {
                showUploadStatus('warning',
                    `File uploaded with ${errorCount} errors. ${processedCount} records processed successfully.`);
            } else {
                showUploadStatus('success',
                    `File uploaded successfully! ${processedCount} student records processed.`);
            }

            // Reset file input
            fileInput.value = '';
            $('#uploadStudentDataBtn').prop('disabled', true);

            // Show detailed results if available
            if (response.errors && response.errors.length > 0) {
                showDetailedErrors(response.errors);
            }
        },
        error: function (xhr) {
            let errorMessage = 'Failed to upload file';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            } else if (xhr.status === 413) {
                errorMessage = 'File too large. Please reduce file size and try again.';
            } else if (xhr.status === 400) {
                errorMessage = 'Invalid file format or data. Please check your file and try again.';
            }
            showUploadStatus('error', errorMessage);
        },
        complete: function () {
            $('#uploadStudentDataBtn').prop('disabled', false).html('<i class="material-icons">cloud_upload</i> Upload File');
            hideUploadProgress();
        }
    });
}

function showUploadStatus(type, message, showProgress = false) {
    const statusDiv = $('#uploadStatus');
    const messageSpan = $('#uploadStatusMessage');
    const alertDiv = statusDiv.find('.alert');

    // Remove existing alert classes
    alertDiv.removeClass('alert-success alert-danger alert-info alert-warning');

    // Add appropriate class
    switch (type) {
        case 'success':
            alertDiv.addClass('alert-success');
            break;
        case 'error':
            alertDiv.addClass('alert-danger');
            break;
        case 'warning':
            alertDiv.addClass('alert-warning');
            break;
        default:
            alertDiv.addClass('alert-info');
    }

    messageSpan.text(message);
    statusDiv.show();

    if (showProgress) {
        showUploadProgress();
    }

    // Auto-hide success/error messages after 8 seconds
    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusDiv.fadeOut();
        }, 8000);
    }
}

function showUploadProgress() {
    const progressHtml = `
            <div class="upload-progress mt-2">
                <div class="progress">
                    <div class="progress-bar bg-primary" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                        <span class="sr-only">0% Complete</span>
                    </div>
                </div>
                <small class="text-muted">Uploading... <span id="progress-percent">0%</span></small>
            </div>
        `;
    $('#uploadStatus .alert').after(progressHtml);
}

function updateUploadProgress(percent) {
    const progressBar = $('.progress-bar');
    const progressText = $('#progress-percent');

    progressBar.css('width', percent + '%').attr('aria-valuenow', percent);
    progressText.text(percent + '%');

    // Update progress bar color based on completion
    if (percent < 50) {
        progressBar.removeClass('bg-warning bg-success').addClass('bg-primary');
    } else if (percent < 90) {
        progressBar.removeClass('bg-primary bg-success').addClass('bg-warning');
    } else {
        progressBar.removeClass('bg-primary bg-warning').addClass('bg-success');
    }
}

function hideUploadProgress() {
    $('.upload-progress').remove();
}

function showDetailedErrors(errors) {
    if (errors.length === 0) return;

    const errorModal = `
            <div class="modal fade" id="uploadErrorModal" tabindex="-1" role="dialog">
                <div class="modal-dialog modal-lg" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Upload Errors</h5>
                            <button type="button" class="close" data-dismiss="modal">
                                <span>&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            <p class="text-muted">The following errors occurred during file processing:</p>
                            <div class="error-list" style="max-height: 400px; overflow-y: auto;">
                                ${errors.slice(0, 20).map(error => `<div class="alert alert-warning small">${error}</div>`).join('')}
                            </div>
                            ${errors.length > 20 ? `<p class="text-muted"><em>... and ${errors.length - 20} more errors</em></p>` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

    // Remove existing error modal if any
    $('#uploadErrorModal').remove();

    // Add and show new error modal
    $('body').append(errorModal);
    $('#uploadErrorModal').modal('show');

    // Auto-remove modal when hidden
    $('#uploadErrorModal').on('hidden.bs.modal', function () {
        $(this).remove();
    });
}

function viewConvocationDetails(convocationId) {
    $.ajax({
        url: `/convocation/${convocationId}/`,
        method: 'GET',
        success: function (convocation) {
            const registrationDate = new Date(convocation.registration_date);
            const registrationDeadline = new Date(convocation.registration_deadline);
            const rehearsalDate = new Date(convocation.rehearsal_date);
            const convocationDate = new Date(convocation.convocation_date);
            $('#detail-title').text(convocation.title);
            $('#detail-academic-year').text(convocation.academic_year);
            $('#detail-status').text(convocation.status)
                .removeClass('active inactive upcoming')
                .addClass(convocation.status.toLowerCase());
            $('#detail-registration-date').text(registrationDate.toLocaleDateString());
            $('#detail-registration-deadline').text(registrationDeadline.toLocaleDateString());
            $('#detail-convocation-datetime').text(`${convocationDate.toLocaleDateString()}`);
            $('#detail-rehearsal-datetime').text(`${rehearsalDate.toLocaleDateString()} at ${convocation.rehearsal_time}`);
            $('#detail-form-link').attr('href', convocation.registration_form_link);
            $('#detail-description').text(convocation.description || 'No description provided');

            $('#viewDetailsModal').modal('show');
        },
        error: function (xhr) {
            alert('Failed to load convocation details');
            console.error(xhr);
        }
    });
}

// New functions for separate modals
function openStudentUploadModal(convocationId) {
    $.ajax({
        url: `/convocation/${convocationId}/`,
        method: 'GET',
        success: function (convocation) {
            $('#upload-convocation-title').text(convocation.title);
            $('#upload-academic-year').text(convocation.academic_year);

            // Store convocation ID
            $('#studentUploadModal').data('convocation-id', convocationId);

            // Reset upload section
            $('#modalStudentDataFile').val('');
            $('#modalUploadStudentDataBtn').prop('disabled', true);
            $('#modalUploadStatus').hide();

            // Load assigned students
            loadAssignedStudents(convocationId);

            $('#studentUploadModal').modal('show');
        },
        error: function (xhr) {
            alert('Failed to load convocation details');
            console.error(xhr);
        }
    });
}

function openLetterGenerationModal(convocationId) {
    $.ajax({
        url: `/convocation/${convocationId}/`,
        method: 'GET',
        success: function (convocation) {
            $('#letter-convocation-title').text(convocation.title);
            $('#letter-academic-year').text(convocation.academic_year);

            // Store convocation ID
            $('#letterGenerationModal').data('convocation-id', convocationId);

            // Load application templates
            loadApplicationTemplatesForModal();

            $('#letterGenerationModal').modal('show');
        },
        error: function (xhr) {
            alert('Failed to load convocation details');
            console.error(xhr);
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

// Application Letter Template Functions
function loadApplicationTemplates() {
    const button = $('#loadApplicationsBtn');
    const originalText = button.html();
    const select = $('#applicationLetterSelect');
    const countSpan = $('#applicationCount');

    button.disabled = true;
    button.html('<i class="material-icons">hourglass_empty</i> Loading...');

    $.ajax({
        url: '/api/application',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        success: function (response) {
            // Clear existing options
            select.empty();
            select.append('<option value="">Select an application letter template...</option>');
            const data = response.filter(app => app.dept_name === 'Examination');
            if (data.length > 0) {
                data.forEach(function (app) {
                    const option = `<option value="${app.id}" data-name="${app.name}" data-description="${app.description}">
                            ${app.short_name}
                        </option>`;
                    select.append(option);
                });

                countSpan.text(data.length);
                select.prop('disabled', false);
            } else {
                select.append('<option value="" disabled>No exam department applications found</option>');
                countSpan.text('0');
                select.prop('disabled', true);
            }
        },
        error: function (xhr) {
            let errorMessage = 'Failed to load application templates';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }

            select.empty();
            select.append('<option value="" disabled>Error loading templates</option>');
            countSpan.text('0');
            select.prop('disabled', true);

            console.error('Error loading applications:', errorMessage);
            alert(errorMessage);
        },
        complete: function () {
            button.disabled = false;
            button.html(originalText);
        }
    });
}

function getSelectedApplicationTemplate() {
    const select = $('#applicationLetterSelect');
    const selectedValue = select.val();

    if (!selectedValue) {
        return null;
    }

    const selectedOption = select.find('option:selected');
    return {
        id: selectedValue,
        name: selectedOption.data('name'),
        description: selectedOption.data('description')
    };
}

// Functions for modal-based operations
function loadApplicationTemplatesForModal() {
    const button = $('#modalLoadApplicationsBtn');
    const originalText = button.html();
    const select = $('#modalApplicationLetterSelect');
    const countSpan = $('#modalApplicationCount');

    button.disabled = true;
    button.html('<i class="material-icons">hourglass_empty</i> Loading...');

    $.ajax({
        url: '/api/application/',
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        success: function (response) {
            select.empty();
            select.append('<option value="">Select an application letter template...</option>');
            const data = response.filter(app => app.dept_name === 'Examination');

            if (response.length > 0) {
                data.forEach(function (app) {
                    const option = `<option value="${app.id}" data-name="${app.name}" data-description="${app.description}">
                            ${app.application_name}
                        </option>`;
                    select.append(option);
                });

                countSpan.text(data.length);
                select.prop('disabled', false);
            } else {
                select.append('<option value="" disabled>No exam department applications found</option>');
                countSpan.text('0');
                select.prop('disabled', true);
            }
        },
        error: function (xhr) {
            let errorMessage = 'Failed to load application templates';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }

            select.empty();
            select.append('<option value="" disabled>Error loading templates</option>');
            countSpan.text('0');
            select.prop('disabled', true);

            console.error('Error loading applications:', errorMessage);
            alert(errorMessage);
        },
        complete: function () {
            button.disabled = false;
            button.html(originalText);
        }
    });
}

function getSelectedApplicationTemplateFromModal() {
    const select = $('#modalApplicationLetterSelect');
    const selectedValue = select.val();

    if (!selectedValue) {
        return null;
    }

    const selectedOption = select.find('option:selected');
    return {
        id: selectedValue,
        name: selectedOption.data('name'),
        description: selectedOption.data('description')
    };
}

function handleModalFileUpload() {
    const fileInput = $('#modalStudentDataFile')[0];
    const file = fileInput.files[0];

    if (!file) {
        showUploadStatusModal('error', 'Please select a file to upload');
        return;
    }

    // Validate file type
    const allowedTypes = ['.xlsx', '.xls'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(fileExtension)) {
        showUploadStatusModal('error', 'Invalid file type. Please select a CSV or Excel file.');
        return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showUploadStatusModal('error', 'File size too large. Maximum allowed size is 10MB.');
        return;
    }

    const formData = new FormData();
    formData.append('convocation_data', file);

    const convocationId = $('#studentUploadModal').data('convocation-id');
    if (convocationId) {
        formData.append('convocation_id', convocationId);
    }

    showUploadStatusModal('info', 'Uploading file...', true);
    $('#modalUploadStudentDataBtn').prop('disabled', true).html('<i class="material-icons">hourglass_empty</i> Uploading...');

    $.ajax({
        url: '/api/upload-convocation-data/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            const processedCount = response.result.modified || 0;
            const errorCount = response.result.total || 0;

            if (errorCount > 0) {
                showUploadStatusModal('warning',
                    `File uploaded!, ${processedCount} records processed successfully.${errorCount} records were not uploaded`);

            } else {
                showUploadStatusModal('success',
                    `File uploaded successfully! ${processedCount} student records processed.`);
            }

            fileInput.value = '';
            $('#modalUploadStudentDataBtn').prop('disabled', true);
        },
        error: function (xhr) {
            let errorMessage = 'Failed to upload file';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            showUploadStatusModal('error', errorMessage);
        },
        complete: function () {
            $('#modalUploadStudentDataBtn').prop('disabled', false).html('<i class="material-icons">cloud_upload</i> Upload File');
        }
    });
}

function showUploadStatusModal(type, message, showProgress = false) {
    const statusDiv = $('#modalUploadStatus');
    const messageSpan = $('#modalUploadStatusMessage');
    const alertDiv = statusDiv.find('.alert');

    alertDiv.removeClass('alert-success alert-danger alert-info alert-warning');

    switch (type) {
        case 'success':
            alertDiv.addClass('alert-success');
            break;
        case 'error':
            alertDiv.addClass('alert-danger');
            break;
        case 'warning':
            alertDiv.addClass('alert-warning');
            break;
        default:
            alertDiv.addClass('alert-info');
    }

    messageSpan.text(message);
    statusDiv.show();

    if (type === 'success' || type === 'error') {
        setTimeout(() => {
            statusDiv.fadeOut();
        }, 8000);
    }
}

// Convocation Letter Generation Functions
function generateConvocationLetter() {
    const convocationId = $('#viewDetailsModal').data('convocation-id');
    if (!convocationId) {
        alert('No convocation selected');
        return;
    }

    // Check if application template is selected
    const selectedTemplate = getSelectedApplicationTemplate();
    if (!selectedTemplate) {
        alert('Please select an application letter template first');
        return;
    }

    // For sample, we'll use a test student ID - in real scenario, you might want to select a student
    const studentId = prompt('Enter student registration number (e.g., BSE203110) for sample letter:');
    if (!studentId) {
        return;
    }

    $.ajax({
        url: '/api/generate-convocation-letter/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        data: {
            convocation_id: convocationId,
            student_id: studentId,
            application_id: selectedTemplate.id
        },
        xhrFields: {
            responseType: 'blob'
        },
        success: function (data) {
            // Create blob and download
            const blob = new Blob([data], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `Convocation_Letter_${studentId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            alert('Convocation letter generated and downloaded successfully!');
        },
        error: function (xhr, status, error) {
            console.log(xhr);
            console.log(status);
            console.log(error);
            let errorMessage = 'Failed to generate convocation letter';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            alert(errorMessage);
        }
    });
}

function bulkGenerateLetters() {
    const convocationId = $('#viewDetailsModal').data('convocation-id');
    if (!convocationId) {
        alert('No convocation selected');
        return;
    }

    if (!confirm('This will generate convocation letters for all students in this convocation. Continue?')) {
        return;
    }

    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="material-icons">hourglass_empty</i> Generating...';

    $.ajax({
        url: '/api/bulk-generate-convocation-letters/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        data: {
            convocation_id: convocationId
        },
        success: function (response) {
            alert(`Successfully generated ${response.generated_count} convocation letters. ${response.error_count > 0 ? response.error_count + ' errors occurred.' : ''}`);
            if (response.errors && response.errors.length > 0) {
                console.log('Generation errors:', response.errors);
            }
        },
        error: function (xhr) {
            let errorMessage = 'Failed to generate convocation letters';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            alert(errorMessage);
        },
        complete: function () {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    });
}

function sendConvocationEmails() {
    const convocationId = $('#viewDetailsModal').data('convocation-id');

    if (!convocationId) {
        alert('No convocation selected');
        return;
    }
    // Check if application template is selected
    const selectedTemplate = getSelectedApplicationTemplate();
    if (!selectedTemplate) {
        alert('Please select an application letter template first');
        return;
    }
    if (!confirm('This will send convocation invitation emails to all students. Continue?')) {
        return;
    }

    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="material-icons">hourglass_empty</i> Sending...';

    $.ajax({
        url: '/api/send-convocation-emails/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        data: {
            convocation_id: convocationId,
            application_id: selectedTemplate.id
        },
        success: function (response) {
            alert(`Successfully sent ${response.sent_count} convocation emails. ${response.error_count > 0 ? response.error_count + ' emails failed to send.' : ''}`);
            if (response.errors && response.errors.length > 0) {
                console.log('Email errors:', response.errors);
            }
        },
        error: function (xhr) {
            let errorMessage = 'Failed to send convocation emails';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            alert(errorMessage);
        },
        complete: function () {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    });
}

// Letter generation functions for modal
function generateConvocationLetterFromModal() {
    const convocationId = $('#letterGenerationModal').data('convocation-id');
    if (!convocationId) {
        alert('No convocation selected');
        return;
    }

    const selectedTemplate = getSelectedApplicationTemplateFromModal();
    if (!selectedTemplate) {
        alert('Please select an application letter template first');
        return;
    }

    const studentId = prompt('Enter student registration number (e.g., BSE203110) for sample letter:');
    if (!studentId) {
        return;
    }

    $.ajax({
        url: '/api/generate-convocation-letter/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        data: {
            convocation_id: convocationId,
            student_id: studentId,
            application_id: selectedTemplate.id
        },
        xhrFields: {
            responseType: 'blob'
        },
        success: function (data) {
            const blob = new Blob([data], { type: 'application/pdf' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `Convocation_Letter_${studentId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            alert('Convocation letter generated and downloaded successfully!');
        },
        error: function (xhr, status, error) {
            console.log(xhr);
            console.log(xhr.status);
            console.log(xhr.responseJSON);
            let errorMessage = 'Failed to generate convocation letter : ' + error;
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            alert(errorMessage);
        }
    });
}

function bulkGenerateLettersFromModal() {
    const convocationId = $('#letterGenerationModal').data('convocation-id');
    if (!convocationId) {
        alert('No convocation selected');
        return;
    }

    const selectedTemplate = getSelectedApplicationTemplateFromModal();
    if (!selectedTemplate) {
        alert('Please select an application letter template first');
        return;
    }

    if (!confirm(`This will generate convocation letters for all students using the template "${selectedTemplate.name}". Continue?`)) {
        return;
    }

    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="material-icons">hourglass_empty</i> Generating...';

    $.ajax({
        url: '/api/bulk-generate-convocation-letters/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        data: {
            convocation_id: convocationId,
            application_id: selectedTemplate.id
        },
        success: function (response) {
            alert(`Successfully generated ${response.generated_count} convocation letters. ${response.error_count > 0 ? response.error_count + ' errors occurred.' : ''}`);
            if (response.errors && response.errors.length > 0) {
                console.log('Generation errors:', response.errors);
            }
        },
        error: function (xhr) {
            let errorMessage = 'Failed to generate convocation letters';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            alert(errorMessage);
        },
        complete: function () {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    });
}

function sendConvocationEmailsFromModal() {
    const convocationId = $('#letterGenerationModal').data('convocation-id');
    // Check if application template is selected
    const selectedTemplate = getSelectedApplicationTemplateFromModal();
    if (!selectedTemplate) {
        alert('Please select an application letter template first');
        return;
    }

    if (!convocationId) {
        alert('No convocation selected');
        return;
    }

    if (!confirm('This will send convocation invitation emails to all students. Continue?')) {
        return;
    }

    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="material-icons">hourglass_empty</i> Sending...';

    $.ajax({
        url: '/api/send-convocation-emails/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        data: {
            convocation_id: convocationId,
            application_id: selectedTemplate.id
        },
        success: function (response) {
            alert(`Successfully sent ${response.sent_count} convocation emails. ${response.error_count > 0 ? response.error_count + ' emails failed to send.' : ''}`);
            if (response.errors && response.errors.length > 0) {
                console.log('Email errors:', response.errors);
            }
        },
        error: function (xhr) {
            let errorMessage = 'Failed to send convocation emails';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            alert(errorMessage);
        },
        complete: function () {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    });
}

// --- Student Table Search, Add, Remove ---
let assignedStudentsCache = [];

// Update loadAssignedStudents to support cache and remove button
function loadAssignedStudents(convocationId) {
    const tableBody = $('#assignedStudentsTableBody');
    const totalCount = $('#totalStudentsCount');
    tableBody.html(`
        <tr>
            <td colspan="6" class="text-center text-muted">
                <i class="material-icons">hourglass_empty</i>
                Loading students...
            </td>
        </tr>
    `);
    totalCount.text('0');
    $.ajax({
        url: `/convocation/students/?convocation_id=${convocationId}`,
        method: 'GET',
        success: function (response) {
            assignedStudentsCache = response || [];
            renderAssignedStudentsTable(assignedStudentsCache);
        },
        error: function (xhr) {
            console.error('Failed to load students:', xhr);
            tableBody.html(`
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="material-icons">error_outline</i>
                        Failed to load students. Please try again.
                    </td>
                </tr>
            `);
            totalCount.text('0');
        }
    });
}

function renderAssignedStudentsTable(students) {
    const tableBody = $('#assignedStudentsTableBody');
    const totalCount = $('#totalStudentsCount');
    tableBody.empty();
    if (!students || students.length === 0) {
        tableBody.html(`
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="material-icons">people_outline</i>
                    No students assigned to this convocation yet
                </td>
            </tr>
        `);
        totalCount.text('0');
        return;
    }
    students.forEach((student, index) => {
        const statusBadge = getStudentStatusBadge(student.status || 'registered');
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${student.uu_id || student.regno || 'N/A'}</td>
                <td>${student.name || 'N/A'}</td>
                <td>${student.email || 'N/A'}</td>
                <td>${statusBadge}</td>
                <td><button class="btn btn-sm btn-danger remove-student-btn" data-student-id="${student.uu_id}"><i class="material-icons">delete</i> Remove</button></td>
            </tr>
        `;
        tableBody.append(row);
    });
    totalCount.text(students.length);
}

// Search filter
$(document).on('input', '#studentSearchInput', function () {
    const search = $(this).val().toLowerCase();
    const filtered = assignedStudentsCache.filter(s =>
        (s.uu_id && s.uu_id.toLowerCase().includes(search)) ||
        (s.regno && s.regno.toLowerCase().includes(search)) ||
        (s.name && s.name.toLowerCase().includes(search)) ||
        (s.email && s.email.toLowerCase().includes(search))
    );
    renderAssignedStudentsTable(filtered);
});

// Remove student
$(document).on('click', '.remove-student-btn', function () {
    const studentId = $(this).data('student-id');
    const convocationId = $('#studentUploadModal').data('convocation-id');
    if (!studentId || !convocationId) return;
    if (!confirm('Remove this student from the convocation?')) return;
    $.ajax({
        url: `/api/upload-convocation-data/`,
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        contentType: 'application/json',
        data: { student_id: studentId },
        success: function () {
            loadAssignedStudents(convocationId);
        },
        error: function (xhr) {
            alert('Failed to remove student.');
        }
    });
});

// Function to get status badge HTML
function getStudentStatusBadge(status) {
    const statusClass = {
        'registered': 'badge-success',
        'pending': 'badge-warning',
        'confirmed': 'badge-primary',
        'attended': 'badge-info',
        'absent': 'badge-secondary'
    };

    const statusText = {
        'registered': 'Registered',
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'attended': 'Attended',
        'absent': 'Absent'
    };

    const badgeClass = statusClass[status] || 'badge-secondary';
    const badgeText = statusText[status] || status.charAt(0).toUpperCase() + status.slice(1);

    return `<span class="badge ${badgeClass}">${badgeText}</span>`;
}

// --- End Student Table Search, Add, Remove ---

// --- Student Search and Add from /users/ endpoint ---
let studentSearchTimeout = null;

$(document).on('input', '#studentSearchInput', function () {
    const search = $(this).val().trim();

    if (search.length === 0) {
        $('#studentSearchRow').hide();
        $('#studentSearchResultsBody').html('<tr><td colspan="4" class="text-center text-muted">Type to search students...</td></tr>');
        renderAssignedStudentsTable(assignedStudentsCache);
        return;
    }
    $('#studentSearchRow').show();
    $('#studentSearchResultsBody').html('<tr><td colspan="4" class="text-center text-muted"><i class="material-icons">hourglass_empty</i> Searching...</td></tr>');
    clearTimeout(studentSearchTimeout);
    studentSearchTimeout = setTimeout(function () {
        $.ajax({
            url: `/users/?user_type=student&search=${encodeURIComponent(search)}`,
            method: 'GET',
            success: function (users) {
                if (!users || users.length === 0) {
                    $('#studentSearchResultsBody').html('<tr><td colspan="4" class="text-center text-muted">No students found.</td></tr>');
                    return;
                }
                let html = '';
                users.forEach(user => {
                    html += `<tr>
                        <td>${user.uu_id || user.regno || 'N/A'}</td>
                        <td>${user.name || 'N/A'}</td>
                        <td>${user.email || 'N/A'}</td>
                        <td><button class="btn btn-sm btn-success add-student-btn" data-student-id="${user.uu_id}"><i class="material-icons">person_add</i> Add</button></td>
                    </tr>`;
                });
                $('#studentSearchResultsBody').html(html);
            },
            error: function () {
                $('#studentSearchResultsBody').html('<tr><td colspan="4" class="text-center text-danger">Failed to search students.</td></tr>');
            }
        });
    }, 300); // debounce
});

// Add student from search result
$(document).on('click', '.add-student-btn', function () {
    const studentId = $(this).data('student-id');
    const convocationId = $('#studentUploadModal').data('convocation-id');
    if (!studentId || !convocationId) return;
    $.ajax({
        url: `/api/upload-convocation-data/`, //Add this student to convocation
        method: 'PUT',
        contentType: 'application/json',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        data: JSON.stringify({ convocation_id: convocationId, student_id: studentId }),
        success: function () {
            loadAssignedStudents(convocationId);
            alert("user added successfully")
            $('#studentSearchInput').val('');
            $('#studentSearchRow').hide();
        },
        error: function () {
            alert('Failed to add student.');
        }
    });
});
// --- End Student Search and Add ---
