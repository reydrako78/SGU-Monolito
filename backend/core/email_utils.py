"""
Utilidades de email para notificaciones del sistema.

Todas las funciones son resilientes: si el envío falla (SMTP no
configurado, error de red, etc.) se captura la excepción y se
loguea como WARNING en lugar de propagar el error al usuario.
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags, escape as _html_escape

logger = logging.getLogger(__name__)


def _safe_send(subject: str, html_body: str, recipient: str) -> bool:
    """
    Envía un email HTML con fallback a texto plano.
    Retorna True si se envió, False si hubo error.
    """
    if not recipient:
        logger.warning('email_utils: destinatario vacío, email omitido.')
        return False
    try:
        text_body = strip_tags(html_body)
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_body,
            fail_silently=False,
        )
        logger.info(f'Email enviado a {recipient}: {subject}')
        return True
    except Exception as exc:
        logger.warning(f'Email NO enviado a {recipient} ({subject}): {exc}')
        return False


# ─────────────────────────────────────────────────────────────────
# Notificación: cambio de estado de admisión
# ─────────────────────────────────────────────────────────────────

STATUS_SUBJECT = {
    'in_review':  'Tu expediente está siendo revisado — UPEL',
    'approved':   '¡Felicitaciones! Has sido admitido/a — UPEL',
    'rejected':   'Resultado del proceso de admisión — UPEL',
    'waitlisted': 'En lista de espera — Proceso de Admisión UPEL',
}

STATUS_COLOR = {
    'in_review':  '#0a6782',
    'approved':   '#155724',
    'rejected':   '#842029',
    'waitlisted': '#41464b',
}

STATUS_ICON = {
    'in_review':  '🔍',
    'approved':   '🎉',
    'rejected':   '📋',
    'waitlisted': '⏳',
}

STATUS_BODY = {
    'in_review': (
        'Tu expediente de admisión ha pasado a la fase de <strong>revisión</strong>. '
        'El equipo de Control de Estudios estará evaluando los documentos que has consignado. '
        'Te notificaremos cuando haya una decisión.'
    ),
    'approved': (
        '¡Tu solicitud de admisión ha sido <strong>aprobada</strong>! '
        'Ya puedes acceder al sistema como estudiante y ver los detalles de tu inscripción.'
    ),
    'rejected': (
        'Lamentablemente tu solicitud de admisión <strong>no fue aprobada</strong> en este proceso. '
        'Si tienes dudas, puedes comunicarte con Control de Estudios de tu sede.'
    ),
    'waitlisted': (
        'Tu solicitud ha sido colocada en <strong>lista de espera</strong>. '
        'Serás notificado/a si hay cupos disponibles. Mantente atento/a a tu correo.'
    ),
}


def notify_admission_status_change(aspirant, new_status: str) -> bool:
    """
    Envía un email al aspirante cuando cambia su estado de admisión.
    Solo envía para estados significativos (in_review, approved, rejected, waitlisted).
    Retorna True si el email fue enviado exitosamente.
    """
    subject = STATUS_SUBJECT.get(new_status)
    if not subject:
        return False  # 'pending' no genera notificación

    color   = STATUS_COLOR.get(new_status, '#343a40')
    icon    = STATUS_ICON.get(new_status, '📬')
    body    = STATUS_BODY.get(new_status, '')
    career  = aspirant.admitted_career_name if new_status == 'approved' else ''

    # Determinar URL del portal según estado
    if new_status == 'approved':
        portal_url = '/student/dashboard/'
        portal_label = 'Ir a mi portal de estudiante'
    else:
        portal_url = '/aspirant/dashboard/'
        portal_label = 'Ver mi expediente'

    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:30px 0;">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
            <!-- Header -->
            <tr>
              <td style="background:{color};padding:24px 32px;">
                <h1 style="margin:0;color:#ffffff;font-size:1.3rem;">
                  {icon}&nbsp; {subject}
                </h1>
              </td>
            </tr>
            <!-- Body -->
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px;color:#333;font-size:.97rem;line-height:1.6;">
                  Hola, <strong>{_html_escape(aspirant.get_full_name())}</strong>:
                </p>
                <p style="margin:0 0 16px;color:#333;font-size:.95rem;line-height:1.6;">
                  {body}
                </p>
                {'<p style="margin:0 0 16px;color:#155724;font-size:.95rem;"><strong>Carrera admitida:</strong> ' + _html_escape(career) + '</p>' if career else ''}
                <p style="margin:0 0 16px;color:#555;font-size:.85rem;">
                  Código de aspirante: <code style="background:#f8f9fa;padding:2px 6px;border-radius:4px;">{_html_escape(aspirant.code)}</code>
                </p>
                <!-- CTA Button -->
                <table cellpadding="0" cellspacing="0" style="margin:24px 0;">
                  <tr>
                    <td style="background:{color};border-radius:6px;">
                      <a href="{portal_url}"
                         style="display:inline-block;padding:12px 28px;color:#ffffff;text-decoration:none;font-size:.9rem;font-weight:bold;">
                        {portal_label}
                      </a>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <!-- Footer -->
            <tr>
              <td style="background:#f8f9fa;padding:16px 32px;border-top:1px solid #e9ecef;">
                <p style="margin:0;color:#6c757d;font-size:.78rem;line-height:1.5;">
                  Este mensaje fue generado automáticamente por el sistema de admisiones de la UPEL.<br>
                  Si no esperabas este correo, por favor ignóralo.
                </p>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    return _safe_send(subject, html_body, aspirant.email)


# ─────────────────────────────────────────────────────────────────
# Notificación: perfil incompleto (recordatorio)
# ─────────────────────────────────────────────────────────────────

def notify_certificate_status(cert_request, new_status: str) -> bool:
    """
    Notifica al estudiante cuando cambia el estado de su solicitud de constancia.
    Solo envía para estados significativos (processing, ready, rejected).
    """
    CERT_SUBJECTS = {
        'processing': 'Tu solicitud de constancia está en proceso — UPEL',
        'ready':      '✅ Tu constancia está lista para retirar — UPEL',
        'rejected':   'Solicitud de constancia no procesada — UPEL',
    }
    subject = CERT_SUBJECTS.get(new_status)
    if not subject:
        return False

    CERT_COLORS = {
        'processing': '#0a6782',
        'ready':      '#155724',
        'rejected':   '#842029',
    }
    CERT_ICONS = {
        'processing': '🔄',
        'ready':      '✅',
        'rejected':   '❌',
    }
    CERT_BODIES = {
        'processing': (
            f'Tu solicitud de <strong>{_html_escape(cert_request.get_cert_type_display())}</strong> '
            f'(código <code>{_html_escape(cert_request.code)}</code>) está siendo procesada por '
            f'Control de Estudios. Te avisaremos cuando esté lista.'
        ),
        'ready': (
            f'¡Tu <strong>{_html_escape(cert_request.get_cert_type_display())}</strong> está lista! '
            f'Puedes retirarla en Control de Estudios presentando tu carnet y este código: '
            f'<code style="background:#f0f0f0;padding:2px 6px;border-radius:4px;">{_html_escape(cert_request.code)}</code>.'
        ),
        'rejected': (
            f'Tu solicitud de <strong>{_html_escape(cert_request.get_cert_type_display())}</strong> '
            f'no pudo ser procesada. Revisa las notas del personal en tu portal y '
            f'comunícate con Control de Estudios si tienes dudas.'
        ),
    }

    color  = CERT_COLORS.get(new_status, '#343a40')
    icon   = CERT_ICONS.get(new_status, '📬')
    body   = CERT_BODIES.get(new_status, '')
    staff_note = cert_request.staff_notes
    recipient  = cert_request.user.email

    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:30px 0;">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
            <tr>
              <td style="background:{color};padding:24px 32px;">
                <h1 style="margin:0;color:#ffffff;font-size:1.3rem;">
                  {icon}&nbsp; {subject}
                </h1>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px;color:#333;font-size:.97rem;line-height:1.6;">
                  Hola, <strong>{_html_escape(cert_request.user.get_full_name())}</strong>:
                </p>
                <p style="margin:0 0 16px;color:#333;font-size:.95rem;line-height:1.6;">
                  {body}
                </p>
                {'<div style="background:#f8f9fa;border-left:3px solid ' + color + ';padding:10px 14px;border-radius:4px;margin:16px 0;"><small style=\'color:#555;font-size:.85rem;\'><strong>Nota de Control de Estudios:</strong><br>' + _html_escape(staff_note) + '</small></div>' if staff_note else ''}
                <table cellpadding="0" cellspacing="0" style="margin:24px 0;">
                  <tr>
                    <td style="background:{color};border-radius:6px;">
                      <a href="/student/constancias/"
                         style="display:inline-block;padding:12px 28px;color:#ffffff;text-decoration:none;font-size:.9rem;font-weight:bold;">
                        Ver mis solicitudes
                      </a>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="background:#f8f9fa;padding:16px 32px;border-top:1px solid #e9ecef;">
                <p style="margin:0;color:#6c757d;font-size:.78rem;line-height:1.5;">
                  Este mensaje fue generado automáticamente por el sistema UPEL.<br>
                  Si no esperabas este correo, por favor ignóralo.
                </p>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

    return _safe_send(subject, html_body, recipient)


def notify_incomplete_profile(aspirant) -> bool:
    """
    Recordatorio al aspirante de que su perfil está incompleto.
    """
    subject = 'Completa tu perfil de aspirante — UPEL'
    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:30px 0;">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0"
                 style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
            <tr>
              <td style="background:#1a237e;padding:24px 32px;">
                <h1 style="margin:0;color:#ffffff;font-size:1.3rem;">
                  📝&nbsp; Completa tu perfil de aspirante
                </h1>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px;color:#333;font-size:.97rem;line-height:1.6;">
                  Hola, <strong>{_html_escape(aspirant.first_name or aspirant.email)}</strong>:
                </p>
                <p style="margin:0 0 16px;color:#333;font-size:.95rem;line-height:1.6;">
                  Notamos que aún no has completado tu perfil de aspirante. Para que tu solicitud de
                  admisión pueda ser procesada, necesitas completar tus datos personales, seleccionar
                  tu sede y la carrera de tu preferencia.
                </p>
                <table cellpadding="0" cellspacing="0" style="margin:24px 0;">
                  <tr>
                    <td style="background:#1a237e;border-radius:6px;">
                      <a href="/aspirant/complete-profile/"
                         style="display:inline-block;padding:12px 28px;color:#ffffff;text-decoration:none;font-size:.9rem;font-weight:bold;">
                        Completar mi perfil ahora
                      </a>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="background:#f8f9fa;padding:16px 32px;border-top:1px solid #e9ecef;">
                <p style="margin:0;color:#6c757d;font-size:.78rem;">
                  Mensaje automático del sistema de admisiones UPEL.
                </p>
              </td>
            </tr>
          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """
    return _safe_send(subject, html_body, aspirant.email)
