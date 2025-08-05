from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from models import Users
import pandas as pd
from serializers import UsersSerializer, UserUpdateSerializer
from rest_framework.response import Response


class AllUsersListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = Users.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response(serializer.data)


# Generic API Views
class UsersList(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

    def get_queryset(self):
        department = self.request.query_params.get("department")
        user_type = self.request.query_params.get("user_type")
        show_all = self.request.query_params.get("all", "False").lower() == "true"

        if show_all:
            return Users.objects.all()

        queryset = Users.objects.all()

        if department:
            queryset = queryset.filter(dept=department)
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        if department or user_type:
            return queryset.order_by("name")

        try:
            return Users.objects.filter(user_id=self.request.user.user_id)
        except Users.DoesNotExist:
            return Users.objects.none()


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Users.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "user_id"

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.user_id != user.user_id:
            return Response(
                {"error": "The user can only update his profile!"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User data updated sucessfully"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCSVUploadAPIView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get("file")

        # Validate file
        if not excel_file:
            return Response(
                {"error": "Please upload a file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (excel_file.name.endswith(".xlsx") or excel_file.name.endswith(".xls")):
            return Response(
                {"error": "Please upload a valid Excel file (xlsx or xls)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Use pandas for faster Excel reading
            df = pd.read_excel(excel_file, engine="openpyxl")

            # Convert all column names to string and strip whitespace
            df.columns = df.columns.astype(str).str.strip()

            # Check required columns
            required_columns = ["Name", "Father Name", "Reg #", "CGPA", "Academic Term"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return Response(
                    {
                        "error": f"Required columns not found in the Excel file: {', '.join(missing_columns)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            created_users = []
            users_to_create = []

            errors = []

            # Preprocess the dataframe
            df = df.replace({pd.NA: None})

            # Process in bulk using transaction for better performance
            for index, row in df.iterrows():
                try:
                    # Skip empty rows
                    if pd.isna(row["Reg #"]):
                        continue

                    reg_no = str(row["Reg #"]).strip()
                    if not reg_no:
                        errors.append(
                            f"Row {index + 2}: Registration number is required"
                        )
                        continue

                    student_data = {
                        "name": str(row["Name"]).strip() if row["Name"] else "",
                        "father_name": (
                            str(row["Father Name"]).strip().capitalize()
                            if row["Father Name"]
                            else ""
                        ),
                        "uu_id": reg_no,
                        "cgpa": float(row["CGPA"]) if row["CGPA"] is not None else 0.0,
                        "term": (
                            str(row["Academic Term"]).strip()
                            if row["Academic Term"]
                            else ""
                        ),
                        "email": (
                            str(row["Official Email"]).lower().strip()
                            if "Official Email" in df.columns and row["Official Email"]
                            else f"{reg_no.lower()}@cust.pk"
                        ),
                        "gender": (
                            str(row["Gender"]).strip().capitalize()
                            if "Gender" in df.columns and row["Gender"]
                            else "Male"
                        ),
                        "user_type": "Student",
                        "role": "Undergraduate",
                        "designation": "N/A",
                    }

                    # Validate and save
                    serializer = UsersSerializer(data=student_data)
                    if serializer.is_valid():
                        users_to_create.append(serializer.validated_data)
                    else:
                        errors.append(f"Row {index + 2}: {str(serializer.errors)}")

                except Exception as e:
                    errors.append(f"Row {index + 2}: Error processing - {str(e)}")
                    continue
            if users_to_create:
                try:
                    created_users = UsersSerializer.bulk_create(users_to_create)
                except Exception as e:
                    errors.append(f"Bulk create failed: {str(e)}")
            if errors:
                return Response(
                    {
                        "message": f"Upload completed with {len(errors)} errors",
                        "created_count": len(created_users),
                        "errors": errors,
                        "data": created_users,
                    },
                    status=status.HTTP_207_MULTI_STATUS,
                )

            return Response(
                {
                    "message": f"Successfully uploaded {len(created_users)} students.",
                    "data": created_users,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
