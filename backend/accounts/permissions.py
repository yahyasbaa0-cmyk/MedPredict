from rest_framework import permissions


class IsAdminOrDoctorOrSecretary(permissions.BasePermission):
    """
    Full CRUD for any authenticated staff member (ADMIN, DOCTOR, SECRETARY).
    Used on Patients and Appointments — the secretary's core responsibilities.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role in ['ADMIN', 'DOCTOR', 'SECRETARY']


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Full CRUD for DOCTOR and ADMIN only.
    SECRETARY is blocked from all operations (including reads).
    Used on Consultations — medical acts that secretaries should not access.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'role') and request.user.role in ['ADMIN', 'DOCTOR']


class IsSecretaryReadOnly(permissions.BasePermission):
    """
    Read-only access for SECRETARY role; full CRUD for DOCTOR and ADMIN.
    Used on Prescriptions — secretaries can view and download PDFs
    but cannot create, edit, or delete prescriptions.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'role') or request.user.role not in ['ADMIN', 'DOCTOR', 'SECRETARY']:
            return False

        # Allow any safe method (GET, HEAD, OPTIONS) for staff
        if request.method in permissions.SAFE_METHODS:
            return True

        # Block SECRETARY from write operations (only DOCTOR, ADMIN can write)
        if request.user.role == 'SECRETARY':
            return False

        return True
