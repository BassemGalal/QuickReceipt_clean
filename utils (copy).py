import re
import logging
import html
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


def validate_egyptian_phone(phone):
    """Validate Egyptian phone number format"""
    if not phone:
        return False
    phone = re.sub(r'[^\d]', '', phone)
    pattern = r'^01[0-9]{8,9}$'
    return bool(re.match(pattern, phone))


def format_phone_number(phone):
    """Format phone number for display"""
    if not phone:
        return ""
    phone = re.sub(r'[^\d]', '', phone)
    if len(phone) == 11 and phone.startswith('01'):
        return f"{phone[:3]} {phone[3:6]} {phone[6:]}"
    elif len(phone) == 10 and phone.startswith('01'):
        return f"{phone[:3]} {phone[3:6]} {phone[6:]}"
    return phone


def build_html_email(request_data):
    """Build HTML email content for hospitality request (with inlined styles for compatibility)"""
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>طلب استضافة جديد</title>
            <!-- Fallback styles for clients that support them -->
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; direction: rtl; background-color: #f8fafc; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: bold; }}
                .content {{ padding: 30px; }}
                .info-section {{ margin-bottom: 25px; padding: 20px; background-color: #f8fafc; border-radius: 8px; border-right: 4px solid #2563eb; }}
                .info-section h3 {{ color: #1e40af; margin: 0 0 15px 0; font-size: 18px; }}
                .info-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }}
                .info-label {{ font-weight: bold; color: #374151; min-width: 120px; }}
                .info-value {{ color: #1f2937; flex: 1; text-align: left; }}
                .notes-section {{ background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin-top: 20px; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; font-size: 14px; }}
            </style>
        </head>
        <body style="direction: rtl; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px;">
            <div class="container" style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                <div class="header" style="background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: bold;">🏠 طلب استضافة جديد</h1>
                </div>

                <div class="content" style="padding: 30px;">
                    <div class="info-section" style="margin-bottom: 25px; padding: 20px; background-color: #f8fafc; border-radius: 8px; border-right: 4px solid #2563eb;">
                        <h3 style="color: #1e40af; margin: 0 0 15px 0; font-size: 18px;">📋 معلومات المالك</h3>
                        <div class="info-row" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                            <span class="info-label" style="font-weight: bold; color: #374151; min-width: 120px;">اسم المالك:</span>
                            <span class="info-value" style="color: #1f2937; flex: 1; text-align: left;">{request_data.get('owner', 'غير محدد')}</span>
                        </div>
                        <div class="info-row" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0;">
                            <span class="info-label" style="font-weight: bold; color: #374151; min-width: 120px;">رقم العضوية:</span>
                            <span class="info-value" style="color: #1f2937; flex: 1; text-align: left;">{request_data.get('membership', 'غير محدد')}</span>
                        </div>
                    </div>

                    <div class="info-section" style="margin-bottom: 25px; padding: 20px; background-color: #f8fafc; border-radius: 8px; border-right: 4px solid #2563eb;">
                        <h3 style="color: #1e40af; margin: 0 0 15px 0; font-size: 18px;">📅 تفاصيل الحجز</h3>
                        <div class="info-row" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                            <span class="info-label" style="font-weight: bold; color: #374151; min-width: 120px;">أرقام الحجز:</span>
                            <span class="info-value" style="color: #1f2937; flex: 1; text-align: left;">{request_data.get('bookings', 'غير محدد')}</span>
                        </div>
                        <div class="info-row" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                            <span class="info-label" style="font-weight: bold; color: #374151; min-width: 120px;">تاريخ الوصول:</span>
                            <span class="info-value" style="color: #1f2937; flex: 1; text-align: left;">{format_date(request_data.get('from_date', ''))}</span>
                        </div>
                        <div class="info-row" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                            <span class="info-label" style="font-weight: bold; color: #374151; min-width: 120px;">تاريخ المغادرة:</span>
                            <span class="info-value" style="color: #1f2937; flex: 1; text-align: left;">{format_date(request_data.get('to_date', ''))}</span>
                        </div>
                        <div class="info-row" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0;">
                            <span class="info-label" style="font-weight: bold; color: #374151; min-width: 120px;">مدة الإقامة:</span>
                            <span class="info-value" style="color: #1f2937; flex: 1; text-align: left;">{calculate_duration(request_data.get('from_date', ''), request_data.get('to_date', ''))}</span>
                        </div>
                    </div>

                    <div class="info-section" style="margin-bottom: 25px; padding: 20px; background-color: #f8fafc; border-radius: 8px; border-right: 4px solid #2563eb;">
                        <h3 style="color: #1e40af; margin: 0 0 15px 0; font-size: 18px;">👥 معلومات الضيوف</h3>
                        <div class="info-row" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0;">
                            <span class="info-label" style="font-weight: bold; color: #374151; min-width: 120px;">أسماء الضيوف:</span>
                            <span class="info-value" style="color: #1f2937; flex: 1; text-align: left;">{request_data.get('guests', 'غير محدد')}</span>
                        </div>
                    </div>

                    {f'''
                    <div class="notes-section" style="background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin-top: 20px;">
                        <h4 style="color: #92400e; margin: 0 0 10px 0;">📝 ملاحظات إضافية:</h4>
                        <p>{request_data.get('notes', 'لا توجد ملاحظات')}</p>
                    </div>
                    ''' if request_data.get('notes') else ''}
                </div>

                <div class="footer" style="background-color: #f1f5f9; padding: 20px; text-align: center; color: #64748b; font-size: 14px;">
                    <p>تم إرسال هذا الطلب من نظام طلبات الاستضافة</p>
                    <p>التاريخ والوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
    except Exception as e:
        logger.error(f"Error building HTML email: {e}")
        return build_simple_email_text(request_data)


def build_simple_email_text(request_data):
    """Build simple text email content as fallback"""
    try:
        content = f"""
طلب استضافة جديد
==================

معلومات المالك:
- اسم المالك: {request_data.get('owner', 'غير محدد')}
- رقم العضوية: {request_data.get('membership', 'غير محدد')}
- رقم التليجرام: {request_data.get('telegram', 'غير محدد')}

تفاصيل الحجز:
- أرقام الحجز: {request_data.get('bookings', 'غير محدد')}
- تاريخ الوصول: {request_data.get('from_date', 'غير محدد')}
- تاريخ المغادرة: {request_data.get('to_date', 'غير محدد')}

معلومات الضيوف:
- الضيوف: {request_data.get('guests', 'غير محدد')}

ملاحظات:
{request_data.get('notes', 'لا توجد ملاحظات')}

--
تم إرسال هذا الطلب في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        return content
    except Exception as e:
        logger.error(f"Error building simple email text: {e}")
        return "حدث خطأ في إنشاء محتوى البريد الإلكتروني"


def format_date(date_string):
    """Format date string for display"""
    if not date_string:
        return "غير محدد"
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        month_names = {
            1: 'يناير',
            2: 'فبراير',
            3: 'مارس',
            4: 'أبريل',
            5: 'مايو',
            6: 'يونيو',
            7: 'يوليو',
            8: 'أغسطس',
            9: 'سبتمبر',
            10: 'أكتوبر',
            11: 'نوفمبر',
            12: 'ديسمبر'
        }
        day = date_obj.day
        month = month_names.get(date_obj.month, str(date_obj.month))
        year = date_obj.year
        return f"{day} {month} {year}"
    except ValueError:
        return date_string


def calculate_duration(from_date, to_date):
    """Calculate duration between two dates"""
    if not from_date or not to_date:
        return "غير محدد"
    try:
        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')
        duration = (end - start).days
        if duration == 1:
            return "يوم واحد"
        elif duration == 2:
            return "يومان"
        elif duration < 11:
            return f"{duration} أيام"
        else:
            return f"{duration} يوماً"
    except ValueError:
        return "غير محدد"


def sanitize_input(text):
    """Sanitize user input to prevent XSS and other attacks"""
    if not text:
        return ""
    text = html.escape(str(text))
    text = re.sub(r'<script.*?</script>',
                  '',
                  text,
                  flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    return text.strip()


def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def log_request(request_data, user_ip=None):
    """Log request for audit purposes"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'owner': request_data.get('owner', ''),
            'membership': request_data.get('membership', ''),
            'telegram': request_data.get('telegram', ''),
            'user_ip': user_ip,
            'from_date': request_data.get('from_date', ''),
            'to_date': request_data.get('to_date', '')
        }
        logger.info(f"New hospitality request: {log_entry}")
    except Exception as e:
        logger.error(f"Error logging request: {e}")


def generate_request_id():
    """Generate unique request ID"""
    return str(uuid.uuid4())


def is_valid_date_range(from_date, to_date):
    """Validate date range"""
    if not from_date or not to_date:
        return False
    try:
        start = datetime.strptime(from_date, '%Y-%m-%d')
        end = datetime.strptime(to_date, '%Y-%m-%d')
        today = datetime.now().date()
        if start.date() < today:
            return False
        if end <= start:
            return False
        duration = (end - start).days
        if duration > 30:
            return False
        return True
    except ValueError:
        return False


def get_file_extension(filename):
    """Get file extension from filename"""
    if not filename:
        return ""
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ""


def is_allowed_file(filename):
    """Check if file type is allowed"""
    if not filename:
        return False
    allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'}
    return get_file_extension(filename) in allowed_extensions


def format_file_size(size_bytes):
    """Format file size for display"""
    if not size_bytes:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
