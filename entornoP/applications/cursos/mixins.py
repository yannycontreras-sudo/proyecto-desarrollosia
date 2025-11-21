from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class TeacherRequiredMixin(LoginRequiredMixin):
    """Permite solo a usuarios con rol teacher o admin_role."""

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        # Ajusta según tus métodos en User
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Si en tu modelo User tienes role y métodos helpers:
        if hasattr(user, "role") and user.role in ("teacher", "admin"):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("No tienes permiso para acceder a esta página.")