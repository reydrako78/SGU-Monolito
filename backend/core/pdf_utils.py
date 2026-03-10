import io
import uuid
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from .models import Authority, CertificateRequest, CustomUser

def generate_certificate_pdf(certificate_request):
    """
    Genera un archivo PDF en memoria (BytesIO) para una solicitud de constancia específica.
    """
    buffer = io.BytesIO()
    
    user = certificate_request.user
    doc_type = certificate_request.get_cert_type_display()
    
    # Get active authorities
    authorities = Authority.objects.filter(is_active=True).order_by('order')
    
    # Generate UUID if not present (although CertificateRequest has `code`, 
    # we can use that or a new UUID for validation)
    doc_uuid = str(uuid.uuid4())
    validation_url = f"https://protectospy.edu.ve/validate/{doc_uuid}"
    
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header UPEL
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2.0, height - 80, "REPÚBLICA BOLIVARIANA DE VENEZUELA")
    c.drawCentredString(width / 2.0, height - 100, "UNIVERSIDAD PEDAGÓGICA EXPERIMENTAL LIBERTADOR")
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2.0, height - 120, "INSTITUTO PEDAGÓGICO")
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 170, doc_type.upper())
    
    # Body text formulation based on typical UPEL format
    c.setFont("Helvetica", 12)
    
    # Current Date
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    now = datetime.now()
    fecha_text = f"a los {now.day} días del mes de {meses[now.month - 1]} del año {now.year}."
    
    cargo_principal = authorities.first().position if authorities.exists() else "La autoridad competente"
    
    # Formatting text (basic wrapping)
    tipo = certificate_request.cert_type
    
    if tipo == 'constancia_estudios':
        text = (
            f"Quien suscribe, {cargo_principal}, hace constar por medio de la presente que el (la) "
            f"ciudadano(a) {user.get_full_name()}, titular de la Cédula de Identidad Nro. "
            f"{certificate_request.student_carnet or 'N/A'}, es estudiante regular de esta institución, "
            f"en la Especialidad de {certificate_request.student_career or 'Educación'}, "
            f"cursando el {certificate_request.student_semester or 'N/A'} Semestre correspondiente "
            f"al Período Académico en curso."
        )
    elif tipo == 'record_notas':
        text = (
            f"Quien suscribe, {cargo_principal}, certifica por medio de la presente que el (la) "
            f"ciudadano(a) {user.get_full_name()}, titular de la Cédula de Identidad Nro. "
            f"{certificate_request.student_carnet or 'N/A'}, cursante de la Especialidad de "
            f"{certificate_request.student_career or 'Educación'}, ha solicitado su récord "
            f"académico, el cual está fundamentado en el sistema integral de notas de la "
            f"institución y su archivo físico."
        )
    elif tipo == 'constancia_egresado':
        text = (
            f"Quien suscribe, {cargo_principal}, hace constar por medio de la presente que el (la) "
            f"ciudadano(a) {user.get_full_name()}, titular de la Cédula de Identidad Nro. "
            f"{certificate_request.student_carnet or 'N/A'}, ha cumplido a cabalidad con todas "
            f"las obligaciones y requisitos de ley académicos, obteniendo el estatus de Egresado(a) "
            f"de la Especialidad de {certificate_request.student_career or 'Educación'}."
        )
    elif tipo == 'buena_conducta':
        text = (
            f"Quien suscribe, {cargo_principal}, certifica que el (la) ciudadano(a) "
            f"{user.get_full_name()}, titular de la Cédula de Identidad Nro. "
            f"{certificate_request.student_carnet or 'N/A'}, estudiante de la Especialidad de "
            f"{certificate_request.student_career or 'Educación'}, ha observado en todo momento "
            f"una buena conducta, respetando las normativas de sana convivencia universitarias "
            f"durante su permanencia en esta ilustre casa de estudios."
        )
    elif tipo == 'carga_academica':
        text = (
            f"Quien suscribe, {cargo_principal}, hace constar que el (la) ciudadano(a) "
            f"{user.get_full_name()}, titular de la Cédula de Identidad Nro. "
            f"{certificate_request.student_carnet or 'N/A'}, tiene formalizada su "
            f"carga académica (unidades de crédito y horarios) para el período actual, "
            f"inherente a la Especialidad de {certificate_request.student_career or 'Educación'}."
        )
    else:
        text = (
            f"Quien suscribe, {cargo_principal}, expide la presente certificación a favor del (la) "
            f"ciudadano(a) {user.get_full_name()}, titular de la Cédula de Identidad Nro. "
            f"{certificate_request.student_carnet or 'N/A'}, de la Especialidad de "
            f"{certificate_request.student_career or 'Educación'}, para los fines consiguientes."
        )    
    # Just a simple wrapper for paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.lib.enums import TA_JUSTIFY
    
    styles = getSampleStyleSheet()
    style_body = ParagraphStyle('BodyParagraph', parent=styles['Normal'], fontSize=12, leading=16, alignment=TA_JUSTIFY)
    
    p = Paragraph(text, style_body)
    p.wrapOn(c, width - 200, height)
    p.drawOn(c, 100, height - 280)
    
    # Footer issue paragraph
    p2_text = f"Constancia que se expide a petición de la parte interesada, en la ciudad respectiva, {fecha_text}"
    p2 = Paragraph(p2_text, style_body)
    p2.wrapOn(c, width - 200, height)
    p2.drawOn(c, 100, height - 340)
    
    # Drawing signatures
    y_sig = height - 480
    if not authorities.exists():
        c.drawString(100, y_sig, "_________________________")
        c.drawString(100, y_sig - 15, "(Sin autoridades registradas)")
    else:
        x_positions = [100, width - 280]
        # Dibujar hasta 2 autoridades lado a lado o una sola centrada
        for i, auth in enumerate(authorities[:2]):
            x = x_positions[i % 2] if authorities.count() > 1 else (width/2.0 - 100)
            c.drawCentredString(x + 100, y_sig, "_________________________")
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(x + 100, y_sig - 15, f"{auth.name}")
            c.setFont("Helvetica", 10)
            c.drawCentredString(x + 100, y_sig - 30, f"{auth.position}")

    # Draw QR code
    qr_img = qrcode.make(validation_url)
    qr_io = io.BytesIO()
    qr_img.save(qr_io, format='PNG')
    qr_io.seek(0)
    # Bottom right or bottom center
    c.drawImage(ImageReader(qr_io), width - 150, 50, width=90, height=90)
    
    # Document footer validation info
    c.setFont("Helvetica-Bold", 8)
    c.drawString(50, 90, "DOCUMENTO EMITIDO ELECTRÓNICAMENTE")
    c.setFont("Helvetica", 8)
    c.drawString(50, 80, f"Código Único de Validación: {doc_uuid}")
    c.drawString(50, 70, f"Propósito declarado: {certificate_request.get_purpose_display()}")
    c.drawString(50, 60, f"Verifique la autenticidad escaneando el código QR o ingresando a:")
    c.drawString(50, 50, validation_url)
    
    c.save()
    buffer.seek(0)
    return buffer
