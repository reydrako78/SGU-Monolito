import logging
import requests
from datetime import datetime
from django.conf import settings
from rest_framework import serializers
from .models import (
    CustomUser, SystemSettings, Aspirant, SystemRole, RolePermission, 
    Sede, Nucleo, Authority, DocumentAttachment, CertificateRequest
)


# ─────────────────────────────────────────────
# Usuarios
# ─────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    # ── Scope (solo lectura) ──────────────────
    scope_display    = serializers.SerializerMethodField()
    scope_sede_name  = serializers.CharField(source='scope_sede.name', read_only=True, default=None)
    scope_nucleo_name = serializers.CharField(source='scope_nucleo.name', read_only=True, default=None)

    def get_scope_display(self, obj):
        return obj.scope_display if hasattr(obj, 'scope_display') else ''

    class Meta:
        model  = CustomUser
        fields = (
            'id', 'code', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'can_access_django_admin', 'date_joined', 'last_login',
            'scope_level', 'scope_sede', 'scope_sede_name',
            'scope_nucleo', 'scope_nucleo_name', 'scope_display',
        )
        read_only_fields = ('id', 'code', 'date_joined', 'last_login', 'scope_display', 'scope_sede_name', 'scope_nucleo_name')


class UserCreateSerializer(serializers.ModelSerializer):
    """Creación de usuarios — solo accesible para administradores."""
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    scope_sede   = serializers.PrimaryKeyRelatedField(
        queryset=Sede.objects.all(), required=False, allow_null=True,
    )
    scope_nucleo = serializers.PrimaryKeyRelatedField(
        queryset=Nucleo.objects.all(), required=False, allow_null=True,
    )

    class Meta:
        model  = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role', 'password', 'password2',
            'scope_level', 'scope_sede', 'scope_nucleo',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        # Validación cruzada scope
        scope_level  = attrs.get('scope_level', 'global')
        scope_sede   = attrs.get('scope_sede')
        scope_nucleo = attrs.get('scope_nucleo')
        if scope_level == 'sede' and not scope_sede:
            raise serializers.ValidationError({'scope_sede': 'Debe asignar una sede para el nivel "Sede".'})
        if scope_level == 'nucleo' and not scope_nucleo:
            raise serializers.ValidationError({'scope_nucleo': 'Debe asignar un núcleo para el nivel "Núcleo".'})
        if scope_level == 'nucleo' and scope_nucleo and scope_sede and scope_nucleo.sede != scope_sede:
            raise serializers.ValidationError({'scope_nucleo': 'El núcleo no pertenece a la sede indicada.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ─────────────────────────────────────────────
# Configuración del Sistema
# ─────────────────────────────────────────────

class SystemSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SystemSettings
        fields = ('system_name', 'university_name', 'primary_color', 'secondary_color', 'logo', 'logo_url', 'updated_at')
        read_only_fields = ('updated_at',)

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
        return None


# ─────────────────────────────────────────────
# Aspirantes
# ─────────────────────────────────────────────

class DocumentAttachmentSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    file_size_display = serializers.CharField(read_only=True)

    class Meta:
        model = DocumentAttachment
        fields = ('id', 'doc_type', 'doc_type_display', 'file', 'original_filename', 'file_size', 'file_size_display', 'notes', 'uploaded_at')
        read_only_fields = ('id', 'original_filename', 'file_size', 'uploaded_at')


class AspirantSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    user_code = serializers.CharField(source='user.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    admission_status_display = serializers.CharField(source='get_admission_status_display', read_only=True)
    admission_type_display = serializers.CharField(source='get_admission_type_display', read_only=True)
    sede_name = serializers.CharField(source='sede.name', read_only=True)
    nucleo_name = serializers.CharField(source='nucleo.name', read_only=True)
    documents = DocumentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Aspirant
        fields = (
            'id', 'code', 'full_name', 'first_name', 'last_name',
            'national_id', 'email', 'phone', 'birth_date', 'address',
            'sede', 'sede_name', 'nucleo', 'nucleo_name',
            'career_id', 'career_name',
            'career_id_2', 'career_name_2',
            'career_id_3', 'career_name_3',
            'admission_type', 'admission_type_display',
            'admission_status', 'admission_status_display', 'admission_notes',
            'admitted_career_id', 'admitted_career_name', 'admitted_option',
            'user_code', 'status', 'status_display', 'registered_at', 'updated_at',
            'documents',
        )
        read_only_fields = ('id', 'code', 'national_id', 'registered_at', 'updated_at', 'user_code', 'reviewed_at')


class AspirantRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Aspirant
        fields = ('username', 'password', 'first_name', 'last_name', 'national_id', 'email')

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        
        # 1. Crear el usuario CustomUser con rol aspirant
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='aspirant',
            is_active=True
        )

        # 2. Crear el perfil de Aspirante asociado
        aspirant = Aspirant.objects.create(
            user=user,
            **validated_data
        )
        return aspirant


class AspirantUpdateSerializer(serializers.ModelSerializer):
    """Para actualización del perfil vía API — national_id solo se permite si está vacío."""
    class Meta:
        model = Aspirant
        fields = (
            'first_name', 'last_name', 'phone', 'birth_date', 'address',
            'sede', 'nucleo', 'admission_type',
            'career_id', 'career_name',
            'career_id_2', 'career_name_2',
            'career_id_3', 'career_name_3',
            'national_id', 'admission_status', 'admission_notes', 
            'admitted_career_id', 'admitted_career_name', 'admitted_option'
        )

    def validate_national_id(self, value):
        if self.instance and self.instance.national_id and self.instance.national_id != value:
            raise serializers.ValidationError("La cédula no puede ser modificada una vez registrada.")
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if not request:
            return attrs  # Si no hay request (ej: tests internos), permitir
        user = request.user
        ADMIN_ROLES = ('admin', 'secretaria', 'coordinacion', 'control_estudios', 'director')
        is_admin = user.is_staff or user.is_superuser or getattr(user, 'role', '') in ADMIN_ROLES
        
        # Campos restringidos a administradores
        restricted = ['admission_status', 'admission_notes', 'admitted_career_id', 'admitted_career_name', 'admitted_option']
        for field in restricted:
            if field in attrs and not is_admin:
                raise serializers.ValidationError({field: "Solo el personal administrativo puede modificar este campo."})
        
        return attrs

    def update(self, instance, validated_data):
        old_status = getattr(instance, 'admission_status', 'pending')
        instance = super().update(instance, validated_data)
        
        # Promoción a Estudiante cuando se APRUEBA (status = 'approved')
        if instance.admission_status == 'approved' and old_status != 'approved':
            self._promote_to_student(instance)
            
        return instance

    def _promote_to_student(self, aspirant):
        """Dispara el cambio de rol y la creación del expediente en Students Service."""
        import random, string
        from datetime import datetime as dt
        user = aspirant.user
        user.role = 'student'
        user.is_active = True
        user.save(update_fields=['role', 'is_active'])

        # Generar carnet único: YY+P-SEQ (ej: 261-4F2)
        year_short = dt.now().strftime('%y')
        period = "1" if dt.now().month < 6 else "2"
        rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        carnet = f"{year_short}{period}-{rand_str}"

        career_id = aspirant.admitted_career_id or aspirant.career_id
        if not career_id:
            logging.warning(f"Aspirante {aspirant.code} sin carrera definida, expediente no creado en Students.")
            return

        try:
            url = f"{settings.STUDENTS_SERVICE_URL.rstrip('/')}/api/students/"
            payload = {
                "user_id": user.id,
                "carnet": carnet,
                "career": career_id,
                "enrollment_date": dt.now().date().isoformat(),
                "phone": aspirant.phone or "",
                "address": aspirant.address or "",
                "birth_date": aspirant.birth_date.isoformat() if aspirant.birth_date else None,
                "national_id": aspirant.national_id,
                "status": "active",
                "semester": 1,
            }
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code not in [200, 201]:
                logging.error(f"Error sincronizando estudiante ({response.status_code}): {response.text[:200]}")
            else:
                logging.info(f"Estudiante creado OK para aspirante {aspirant.code}, carnet={carnet}")
        except Exception as e:
            logging.error(f"Falla critica en Students Service: {str(e)}")


# ─────────────────────────────────────────────
# RBAC: Roles y Permisos
# ─────────────────────────────────────────────

class AspirantAdmissionSerializer(serializers.ModelSerializer):
    """Específico para que los administradores procesen una admisión."""
    class Meta:
        model = Aspirant
        fields = (
            'admission_status', 'admission_notes', 
            'admitted_career_id', 'admitted_career_name', 'admitted_option'
        )

    def update(self, instance, validated_data):
        # Al aprobar, podríamos disparar la creación de un número de carnet o expediente definitivo
        return super().update(instance, validated_data)


class RolePermissionSerializer(serializers.ModelSerializer):
    service_display = serializers.CharField(source='get_service_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = RolePermission
        fields = ('id', 'service', 'service_display', 'action', 'action_display', 'allowed')


class SystemRoleSerializer(serializers.ModelSerializer):
    permissions = RolePermissionSerializer(many=True, read_only=True)
    permissions_count = serializers.SerializerMethodField()

    class Meta:
        model = SystemRole
        fields = ('id', 'name', 'description', 'is_active', 'permissions_count', 'permissions', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_permissions_count(self, obj):
        return obj.permissions.filter(allowed=True).count()


class RolePermissionBulkSerializer(serializers.Serializer):
    """Para asignar permisos en lote a un rol."""
    permissions = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )

    def validate_permissions(self, value):
        from .models import SERVICE_CHOICES, ACTION_CHOICES
        valid_services = [s[0] for s in SERVICE_CHOICES]
        valid_actions = [a[0] for a in ACTION_CHOICES]
        for perm in value:
            if perm.get('service') not in valid_services:
                raise serializers.ValidationError(f"Servicio inválido: {perm.get('service')}")
            if perm.get('action') not in valid_actions:
                raise serializers.ValidationError(f"Acción inválida: {perm.get('action')}")
        return value


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ('id', 'name', 'sigla', 'city', 'address', 'is_active')


class AuthoritySerializer(serializers.ModelSerializer):
    sede_name = serializers.CharField(source='sede.name', read_only=True, default='Rectorado')

    class Meta:
        model = Authority
        fields = ('id', 'name', 'position', 'sede', 'sede_name', 'is_active', 'order')


class NucleoSerializer(serializers.ModelSerializer):
    sede_name = serializers.CharField(source='sede.name', read_only=True)

    class Meta:
        model = Nucleo
        fields = ('id', 'sede', 'sede_name', 'name', 'address', 'is_active')

# ─────────────────────────────────────────────
# Constancias y Certificaciones
# ─────────────────────────────────────────────

class CertificateRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    cert_type_display = serializers.CharField(source='get_cert_type_display', read_only=True)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)

    class Meta:
        model = CertificateRequest
        fields = (
            'id', 'code', 'user', 'user_name', 'user_email',
            'student_carnet', 'student_career', 'student_semester',
            'cert_type', 'cert_type_display', 'purpose', 'purpose_display',
            'copies', 'period_ref', 'student_notes',
            'status', 'status_display', 'staff_notes',
            'processed_by', 'processed_by_name', 'processed_at',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'code', 'user', 'status', 'staff_notes',
            'processed_by', 'processed_at', 'created_at', 'updated_at'
        )
