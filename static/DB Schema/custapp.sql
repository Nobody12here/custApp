-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 19, 2025 at 03:19 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `custapp`
--

-- --------------------------------------------------------

--
-- Table structure for table `applications`
--

CREATE TABLE `applications` (
  `id` int(11) NOT NULL,
  `application_name` text NOT NULL,
  `responsible_dept_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `short_name` varchar(10) NOT NULL,
  `amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `default_responsible_employee_id` int(11) NOT NULL DEFAULT 1,
  `status` tinyint(4) NOT NULL DEFAULT 1,
  `application_desc` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `applications`
--

INSERT INTO `applications` (`id`, `application_name`, `responsible_dept_id`, `created_at`, `updated_at`, `short_name`, `amount`, `default_responsible_employee_id`, `status`, `application_desc`) VALUES
(1, 'Bona-Fide Application', 1, '2023-04-01 08:00:00', '2023-04-01 08:00:00', 'Bona-Fide', 500.00, 3, 1, ''),
(2, 'Fee Equivalence Request', 2, '2023-04-02 09:00:00', '2025-03-18 09:35:32', 'Fee_Equiva', 1000.00, 3, 1, 'this is an application'),
(3, 'English Proficiency Request', 3, '2023-04-03 10:00:00', '2023-04-03 10:00:00', 'English_Pr', 750.00, 3, 1, ''),
(5, 'Confirm Student', 1, '2025-03-18 05:29:24', '2025-03-18 05:32:21', 'ConfirmS', 500.00, 1, 1, 'This is to certify that {student_name} under Registration No. {registration_no} is a student of {department} in the degree program of {program}. Issued on {date} by {issuer_name}.'),
(6, 'Fee Eqv', 1, '2025-03-18 09:45:22', '2025-03-18 09:45:46', 'FE', 500.00, 1, 0, 'This is to certify that {student_name} under Registration No. {registration_no} is a student of {department} in the degree program of {program}. Issued on {date} by {issuer_name}.');

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add user', 4, 'add_user'),
(14, 'Can change user', 4, 'change_user'),
(15, 'Can delete user', 4, 'delete_user'),
(16, 'Can view user', 4, 'view_user'),
(17, 'Can add content type', 5, 'add_contenttype'),
(18, 'Can change content type', 5, 'change_contenttype'),
(19, 'Can delete content type', 5, 'delete_contenttype'),
(20, 'Can view content type', 5, 'view_contenttype'),
(21, 'Can add session', 6, 'add_session'),
(22, 'Can change session', 6, 'change_session'),
(23, 'Can delete session', 6, 'delete_session'),
(24, 'Can view session', 6, 'view_session'),
(25, 'Can add applications', 7, 'add_applications'),
(26, 'Can change applications', 7, 'change_applications'),
(27, 'Can delete applications', 7, 'delete_applications'),
(28, 'Can view applications', 7, 'view_applications'),
(29, 'Can add department', 8, 'add_department'),
(30, 'Can change department', 8, 'change_department'),
(31, 'Can delete department', 8, 'delete_department'),
(32, 'Can view department', 8, 'view_department'),
(33, 'Can add users', 9, 'add_users'),
(34, 'Can change users', 9, 'change_users'),
(35, 'Can delete users', 9, 'delete_users'),
(36, 'Can view users', 9, 'view_users'),
(37, 'Can add template attributes', 10, 'add_templateattributes'),
(38, 'Can change template attributes', 10, 'change_templateattributes'),
(39, 'Can delete template attributes', 10, 'delete_templateattributes'),
(40, 'Can view template attributes', 10, 'view_templateattributes'),
(41, 'Can add request', 11, 'add_request'),
(42, 'Can change request', 11, 'change_request'),
(43, 'Can delete request', 11, 'delete_request'),
(44, 'Can view request', 11, 'view_request');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
(1, 'pbkdf2_sha256$600000$sq5kNWyhh0mGfAZPUXS3Nk$cVtqUXl79xU0N/Zf/+rgZXTkv5F/6lq2UtxCuGOIJw8=', '2025-03-04 07:10:43.795571', 1, 'Admin', '', '', '', 1, 1, '2025-03-04 07:10:28.456582');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `department`
--

CREATE TABLE `department` (
  `dept_id` int(11) NOT NULL,
  `dept_name` varchar(255) NOT NULL,
  `dept_head_id` int(11) NOT NULL,
  `short_name` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `department`
--

INSERT INTO `department` (`dept_id`, `dept_name`, `dept_head_id`, `short_name`) VALUES
(1, 'Registration', 1, ''),
(2, 'Accounts', 2, ''),
(3, 'Examination', 3, ''),
(20, 'Software Engineering', 4, 'SE'),
(21, 'Electrical Engineering', 5, 'EE'),
(22, 'Mechanical Engineering', 6, 'ME'),
(23, 'Pharmacy', 7, 'PH');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'auth', 'user'),
(5, 'contenttypes', 'contenttype'),
(7, 'CUSTApp', 'applications'),
(8, 'CUSTApp', 'department'),
(11, 'CUSTApp', 'request'),
(10, 'CUSTApp', 'templateattributes'),
(9, 'CUSTApp', 'users'),
(6, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'CUSTApp', '0001_initial', '2025-03-04 07:06:30.830003'),
(2, 'contenttypes', '0001_initial', '2025-03-04 07:06:30.931054'),
(3, 'auth', '0001_initial', '2025-03-04 07:06:32.207161'),
(4, 'admin', '0001_initial', '2025-03-04 07:06:32.514631'),
(5, 'admin', '0002_logentry_remove_auto_add', '2025-03-04 07:06:32.610523'),
(6, 'admin', '0003_logentry_add_action_flag_choices', '2025-03-04 07:06:32.636456'),
(7, 'contenttypes', '0002_remove_content_type_name', '2025-03-04 07:06:32.831196'),
(8, 'auth', '0002_alter_permission_name_max_length', '2025-03-04 07:06:32.993130'),
(9, 'auth', '0003_alter_user_email_max_length', '2025-03-04 07:06:33.044988'),
(10, 'auth', '0004_alter_user_username_opts', '2025-03-04 07:06:33.096852'),
(11, 'auth', '0005_alter_user_last_login_null', '2025-03-04 07:06:33.242546'),
(12, 'auth', '0006_require_contenttypes_0002', '2025-03-04 07:06:33.250439'),
(13, 'auth', '0007_alter_validators_add_error_messages', '2025-03-04 07:06:33.288588'),
(14, 'auth', '0008_alter_user_username_max_length', '2025-03-04 07:06:33.343999'),
(15, 'auth', '0009_alter_user_last_name_max_length', '2025-03-04 07:06:33.386634'),
(16, 'auth', '0010_alter_group_name_max_length', '2025-03-04 07:06:33.410569'),
(17, 'auth', '0011_update_proxy_permissions', '2025-03-04 07:06:33.430546'),
(18, 'auth', '0012_alter_user_first_name_max_length', '2025-03-04 07:06:33.451459'),
(19, 'sessions', '0001_initial', '2025-03-04 07:06:33.564163'),
(20, 'CUSTApp', '0002_applications_letter_type_and_more', '2025-03-05 08:56:48.827905');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('i24u9v5mmym87xponmup0p1fpk6sxmu1', '.eJxVjDsOwjAQRO_iGllek0Q2JT1nsNb7wQHkSHFSIe5OIqWAZop5b-ZtEq5LSWuTOY1sLgbM6bfLSE-pO-AH1vtkaarLPGa7K_agzd4mltf1cP8OCrayrfPg9KwMSo4IFbMQEHsIqo4ZiWLvomDn2Q0UWToFryBhi8h9IPP5AjtkOdE:1tpMQN:XjNdEiP7CugxwQ_j88wVzR-TedeSXlbsgPaaSoJd5Jg', '2025-03-18 07:10:43.797603');

-- --------------------------------------------------------

--
-- Table structure for table `program`
--

CREATE TABLE `program` (
  `program_id` int(11) NOT NULL,
  `program_name` text NOT NULL,
  `short_name` text NOT NULL,
  `dept_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `program`
--

INSERT INTO `program` (`program_id`, `program_name`, `short_name`, `dept_id`) VALUES
(0, 'Bachelor of Science in Software Engineering', 'BSc SE', 1),
(0, 'Master of Science in Software Engineering', 'MSc SE', 1),
(0, 'Bachelor of Science in Electrical Engineering', 'BSc EE', 2),
(0, 'Master of Science in Electrical Engineering', 'MSc EE', 2),
(0, 'Bachelor of Science in Mechanical Engineering', 'BSc ME', 3),
(0, 'Master of Science in Mechanical Engineering', 'MSc ME', 3),
(0, 'Bachelor of Science in Pharmacy', 'BSc PH', 4),
(0, 'Master of Science in Pharmacy', 'MSc PH', 4);

-- --------------------------------------------------------

--
-- Table structure for table `request`
--

CREATE TABLE `request` (
  `request_id` int(11) NOT NULL,
  `application_id` int(11) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `applicant_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `comments` text DEFAULT NULL,
  `payment_status` varchar(50) NOT NULL DEFAULT 'Pending',
  `payment_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `request`
--

INSERT INTO `request` (`request_id`, `application_id`, `status`, `applicant_id`, `created_at`, `updated_at`, `comments`, `payment_status`, `payment_date`) VALUES
(1, 1, 'Pending', 1, '2023-04-05 11:00:00', '2023-04-05 11:00:00', 'Request for official document', 'Pending', NULL),
(2, 2, 'Approved', 2, '2023-04-06 12:00:00', '2023-04-06 12:00:00', 'Fee equivalence needed for visa', 'Paid', '2023-04-06 13:00:00'),
(3, 3, 'Rejected', 1, '2023-04-07 14:00:00', '2023-04-07 14:00:00', 'Incomplete documents', 'Pending', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `template_attributes`
--

CREATE TABLE `template_attributes` (
  `id` int(11) NOT NULL,
  `attribute_name` varchar(255) NOT NULL,
  `attribute_value` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `template_attributes`
--

INSERT INTO `template_attributes` (`id`, `attribute_name`, `attribute_value`, `created_at`, `updated_at`) VALUES
(1, 'template_Bona-Fide', 'This is to certify that {student_name} under Registration No. {registration_no} is a bona-fide student of Capital University of Science and Technology, Islamabad in the degree program of {program}. Issued on {date} by {issuer_name}.', '2023-04-05 11:00:00', '2023-04-05 11:00:00'),
(2, 'template_Fee_Equivalence', 'This certifies that {student_name} (Reg No. {registration_no}) is charged a fee of {amount} PKR for {program}. Issued on {date} by {issuer_name}.', '2023-04-06 12:00:00', '2023-04-06 12:00:00'),
(3, 'template_English_Proficiency', 'This certifies that {student_name} (Reg No. {registration_no}) is proficient in English for {program}. Issued on {date} by {issuer_name}.', '2023-04-07 14:00:00', '2023-04-07 14:00:00'),
(4, 'Addmission on Merit Letter', 'This is to certify that {student_name} under Registration No. {registration_no} has been granted admission on merit to Capital University of Science and Technology, Islamabad in the degree program of {program}.\\r\\n\\r\\nIssued on {date} by {issuer_name}.\"', '2025-03-13 07:12:33', '2025-03-13 07:12:33');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `uu_id` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `father_name` varchar(255) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `program_name` varchar(255) DEFAULT NULL,
  `dept_name` varchar(255) DEFAULT NULL,
  `gender` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `user_type` varchar(50) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `otp` varchar(10) DEFAULT NULL,
  `remark` text DEFAULT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `picture` varchar(255) DEFAULT NULL,
  `cgpa` decimal(3,2) DEFAULT NULL,
  `term` varchar(10) DEFAULT NULL,
  `DoB` date DEFAULT NULL,
  `CNIC` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `uu_id`, `name`, `father_name`, `address`, `program_name`, `dept_name`, `gender`, `status`, `email`, `created_at`, `updated_at`, `user_type`, `role`, `designation`, `otp`, `remark`, `phone_number`, `picture`, `cgpa`, `term`, `DoB`, `CNIC`) VALUES
(1, 'U001', 'Ali Khan', 'Zubair Khan', '123 University Road, Islamabad', 'Computer Science', 'CS Department', 'Male', 'Active', 'ali.khan@example.com', '2023-01-15 10:00:00', '2023-01-15 10:00:00', 'Student', 'Undergraduate', 'N/A', '123456', 'Good student', '0312-3456789', 'profile1.jpg', 3.50, 'Fall 2023', '1995-05-10', '12345-6789012-3'),
(2, 'U002', 'Sara Ahmed', 'Ahmed Ali', '456 Lane, Islamabad', 'Electrical Engineering', 'EE Department', 'Female', 'Active', 'sara.ahmed@example.com', '2023-02-20 12:00:00', '2023-02-20 12:00:00', 'Student', 'Undergraduate', 'N/A', '654321', 'Excellent performance', '0313-9876543', 'profile2.jpg', 3.75, 'Spring 202', '1996-08-15', '98765-4321098-4'),
(3, 'U003', 'Omar Farooq', 'Zain Farooq', '789 Street, Islamabad', 'Software Engineering', 'SE Department', 'Male', 'Inactive', 'omar.farooq@example.com', '2023-03-10 09:00:00', '2023-03-10 09:00:00', 'Staff', 'Admin', 'Registrar', NULL, 'Handles registrations', '0314-5678901', NULL, NULL, NULL, NULL, NULL),
(4, 'U004', 'Dr. John Smith', 'Mr. Smith', '101 Academic Lane, Islamabad', 'N/A', 'N/A', 'Male', 'Active', 'john.smith@example.com', '2025-03-14 12:52:55', '2025-03-14 12:52:55', 'Staff', 'Head', 'Department Head', NULL, 'Head of Software Engineering', '0315-1234567', 'profile3.jpg', NULL, NULL, '1980-01-01', '12345-6789012-4'),
(5, 'U005', 'Dr. Emily Johnson', 'Mr. Johnson', '102 Academic Lane, Islamabad', 'N/A', 'N/A', 'Female', 'Active', 'emily.johnson@example.com', '2025-03-14 12:52:55', '2025-03-14 12:52:55', 'Staff', 'Head', 'Department Head', NULL, 'Head of Electrical Engineering', '0315-2345678', 'profile4.jpg', NULL, NULL, '1985-02-02', '12345-6789012-5'),
(6, 'U006', 'Dr. Michael Brown', 'Mr. Brown', '103 Academic Lane, Islamabad', 'N/A', 'N/A', 'Male', 'Active', 'michael.brown@example.com', '2025-03-14 12:52:55', '2025-03-14 12:52:55', 'Staff', 'Head', 'Department Head', NULL, 'Head of Mechanical Engineering', '0315-3456789', 'profile5.jpg', NULL, NULL, '1990-03-03', '12345-6789012-6'),
(7, 'U007', 'Dr. Sarah Davis', 'Mr. Davis', '104 Academic Lane, Islamabad', 'N/A', 'N/A', 'Female', 'Active', 'sarah.davis@example.com', '2025-03-14 12:52:55', '2025-03-14 12:52:55', 'Staff', 'Head', 'Department Head', NULL, 'Head of Pharmacy', '0315-4567890', 'profile6.jpg', NULL, NULL, '1992-04-04', '12345-6789012-7');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `applications`
--
ALTER TABLE `applications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `responsible_dept_id` (`responsible_dept_id`),
  ADD KEY `default_responsible_employee_id` (`default_responsible_employee_id`);

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `department`
--
ALTER TABLE `department`
  ADD PRIMARY KEY (`dept_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `request`
--
ALTER TABLE `request`
  ADD PRIMARY KEY (`request_id`),
  ADD KEY `application_id` (`application_id`),
  ADD KEY `applicant_id` (`applicant_id`);

--
-- Indexes for table `template_attributes`
--
ALTER TABLE `template_attributes`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `uu_id` (`uu_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `applications`
--
ALTER TABLE `applications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT for table `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `department`
--
ALTER TABLE `department`
  MODIFY `dept_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `request`
--
ALTER TABLE `request`
  MODIFY `request_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `template_attributes`
--
ALTER TABLE `template_attributes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `applications`
--
ALTER TABLE `applications`
  ADD CONSTRAINT `applications_ibfk_1` FOREIGN KEY (`responsible_dept_id`) REFERENCES `department` (`dept_id`),
  ADD CONSTRAINT `applications_ibfk_2` FOREIGN KEY (`default_responsible_employee_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `department`
--
ALTER TABLE `department`
  ADD CONSTRAINT `department_ibfk_1` FOREIGN KEY (`dept_head_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `request`
--
ALTER TABLE `request`
  ADD CONSTRAINT `request_ibfk_1` FOREIGN KEY (`application_id`) REFERENCES `applications` (`id`),
  ADD CONSTRAINT `request_ibfk_2` FOREIGN KEY (`applicant_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
