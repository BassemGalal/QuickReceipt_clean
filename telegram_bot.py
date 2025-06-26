import os
import json
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8050331002:AAGTmnGjeUSAH6bkiWQYbuXwyBjxO0CwZEI")
TELEGRAM_USERS_MAP = "telegram_users.json"
PENDING_FILE = "pending_replies.json"

# Admin chat IDs (add your admin chat IDs here)
ADMIN_CHAT_IDS = [
    # Add admin chat IDs here, e.g., [123456789, 987654321]
]

class HospitalityBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("pending", self.pending_command))
        self.application.add_handler(CommandHandler("approve", self.approve_command))
        self.application.add_handler(CommandHandler("reject", self.reject_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🏠 مرحباً بك في نظام طلبات الاستضافة

هذا البوت يساعد في إدارة طلبات الاستضافة.

الأوامر المتاحة:
/help - عرض المساعدة
/pending - عرض الطلبات المعلقة (للمديرين)
/approve <رقم الطلب> - الموافقة على طلب (للمديرين)
/reject <رقم الطلب> - رفض طلب (للمديرين)

للحصول على المساعدة، استخدم الأمر /help
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📋 <b>مساعدة نظام طلبات الاستضافة</b>

<b>للمستخدمين العاديين:</b>
• يمكنك إرسال طلب استضافة من خلال الموقع الإلكتروني
• ستصلك إشعارات بحالة طلبك عبر هذا البوت

<b>للمديرين:</b>
• /pending - عرض جميع الطلبات المعلقة
• /approve [رقم الطلب] - الموافقة على طلب محدد
• /reject [رقم الطلب] - رفض طلب محدد

<b>ملاحظة:</b> تأكد من أن رقم التليجرام المستخدم في النموذج مطابق لرقم حسابك في التليجرام.
        """
        await update.message.reply_text(help_message, parse_mode=ParseMode.HTML)
    
    async def pending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command - show pending requests"""
        chat_id = update.effective_chat.id
        
        # Check if user is admin
        if not self.is_admin(chat_id):
            await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا الأمر")
            return
        
        try:
            pending_requests = self.load_pending_requests()
            
            if not pending_requests:
                await update.message.reply_text("📭 لا توجد طلبات معلقة حالياً")
                return
            
            # Filter only pending requests
            pending_only = [req for req in pending_requests if req.get('status', 'pending') == 'pending']
            
            if not pending_only:
                await update.message.reply_text("📭 لا توجد طلبات معلقة حالياً")
                return
            
            message = "📋 <b>الطلبات المعلقة:</b>\n\n"
            
            for i, request in enumerate(pending_only[:10], 1):  # Show first 10 requests
                message += f"<b>{i}. طلب رقم:</b> {request.get('id', 'غير محدد')[:8]}...\n"
                message += f"<b>المالك:</b> {request.get('owner', 'غير محدد')}\n"
                message += f"<b>العضوية:</b> {request.get('membership', 'غير محدد')}\n"
                message += f"<b>التاريخ:</b> {request.get('from_date', '')} - {request.get('to_date', '')}\n"
                message += f"<b>التليجرام:</b> {request.get('telegram', 'غير محدد')}\n"
                message += f"<b>وقت الطلب:</b> {self.format_timestamp(request.get('timestamp', ''))}\n"
                message += "➖➖➖➖➖➖➖➖➖\n\n"
            
            if len(pending_only) > 10:
                message += f"... و {len(pending_only) - 10} طلب آخر\n\n"
            
            message += "💡 لإدارة الطلبات:\n"
            message += "• /approve [رقم الطلب] للموافقة\n"
            message += "• /reject [رقم الطلب] للرفض"
            
            await update.message.reply_text(message, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Error in pending_command: {e}")
            await update.message.reply_text("❌ حدث خطأ في عرض الطلبات المعلقة")
    
    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /approve command"""
        chat_id = update.effective_chat.id
        
        # Check if user is admin
        if not self.is_admin(chat_id):
            await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا الأمر")
            return
        
        if not context.args:
            await update.message.reply_text("❌ يرجى تحديد رقم الطلب\nمثال: /approve 12345678")
            return
        
        request_id = context.args[0]
        result = await self.update_request_status(request_id, 'approved', chat_id)
        
        if result['success']:
            await update.message.reply_text(f"✅ تمت الموافقة على الطلب {request_id[:8]}...")
            # Notify the requester
            await self.notify_requester(result['request'], 'approved')
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    async def reject_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reject command"""
        chat_id = update.effective_chat.id
        
        # Check if user is admin
        if not self.is_admin(chat_id):
            await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا الأمر")
            return
        
        if not context.args:
            await update.message.reply_text("❌ يرجى تحديد رقم الطلب\nمثال: /reject 12345678")
            return
        
        request_id = context.args[0]
        result = await self.update_request_status(request_id, 'rejected', chat_id)
        
        if result['success']:
            await update.message.reply_text(f"❌ تم رفض الطلب {request_id[:8]}...")
            # Notify the requester
            await self.notify_requester(result['request'], 'rejected')
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        message_text = update.message.text
        chat_id = update.effective_chat.id
        
        # Register user phone number if it looks like an Egyptian phone number
        if self.is_egyptian_phone(message_text):
            self.register_user_phone(chat_id, message_text)
            await update.message.reply_text(
                f"✅ تم تسجيل رقم التليجرام: {message_text}\n"
                "سيتم إرسال إشعارات طلبات الاستضافة إلى هذا الحساب."
            )
        else:
            await update.message.reply_text(
                "مرحباً! يمكنك إرسال رقم التليجرام المصري الخاص بك لتسجيله في النظام.\n"
                "أو استخدم الأوامر المتاحة: /help للمساعدة"
            )
    
    def is_admin(self, chat_id):
        """Check if user is admin"""
        return chat_id in ADMIN_CHAT_IDS or len(ADMIN_CHAT_IDS) == 0  # Allow all if no admins set
    
    def is_egyptian_phone(self, text):
        """Check if text is Egyptian phone number"""
        import re
        return bool(re.match(r'^01[0-9]{8,9}$', text.strip()))
    
    def register_user_phone(self, chat_id, phone):
        """Register user's chat ID with their phone number"""
        try:
            users_map = {}
            if os.path.exists(TELEGRAM_USERS_MAP):
                with open(TELEGRAM_USERS_MAP, 'r', encoding='utf-8') as f:
                    users_map = json.load(f)
            
            users_map[phone] = chat_id
            
            with open(TELEGRAM_USERS_MAP, 'w', encoding='utf-8') as f:
                json.dump(users_map, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error registering user phone: {e}")
    
    def load_pending_requests(self):
        """Load pending requests from file"""
        try:
            if os.path.exists(PENDING_FILE):
                with open(PENDING_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading pending requests: {e}")
            return []
    
    def save_pending_requests(self, requests):
        """Save pending requests to file"""
        try:
            with open(PENDING_FILE, 'w', encoding='utf-8') as f:
                json.dump(requests, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving pending requests: {e}")
    
    async def update_request_status(self, request_id, status, admin_chat_id):
        """Update request status"""
        try:
            requests = self.load_pending_requests()
            
            for request in requests:
                if request.get('id', '').startswith(request_id):
                    request['status'] = status
                    request['updated_by'] = admin_chat_id
                    request['updated_at'] = self.get_current_timestamp()
                    
                    self.save_pending_requests(requests)
                    return {'success': True, 'request': request}
            
            return {'success': False, 'message': f'لم يتم العثور على طلب برقم {request_id}'}
            
        except Exception as e:
            logger.error(f"Error updating request status: {e}")
            return {'success': False, 'message': 'حدث خطأ في تحديث حالة الطلب'}
    
    async def notify_requester(self, request, status):
        """Notify the requester about their request status"""
        try:
            telegram_phone = request.get('telegram', '')
            
            # Load users map
            users_map = {}
            if os.path.exists(TELEGRAM_USERS_MAP):
                with open(TELEGRAM_USERS_MAP, 'r', encoding='utf-8') as f:
                    users_map = json.load(f)
            
            chat_id = users_map.get(telegram_phone)
            
            if chat_id:
                status_text = "✅ تمت الموافقة على" if status == 'approved' else "❌ تم رفض"
                
                message = f"""
🏠 <b>تحديث حالة طلب الاستضافة</b>

{status_text} طلبك للاستضافة

<b>تفاصيل الطلب:</b>
• <b>اسم المالك:</b> {request.get('owner', 'غير محدد')}
• <b>رقم العضوية:</b> {request.get('membership', 'غير محدد')}
• <b>تاريخ الإقامة:</b> {request.get('from_date', '')} - {request.get('to_date', '')}
• <b>الضيوف:</b> {request.get('guests', 'غير محدد')}

{"🎉 يمكنك الآن الاستعداد لرحلتك!" if status == 'approved' else "📞 يمكنك التواصل معنا لمزيد من التفاصيل."}
                """
                
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
                
        except Exception as e:
            logger.error(f"Error notifying requester: {e}")
    
    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return timestamp
    
    def get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def send_new_request_notification(self, request_data):
        """Send notification to admins about new request"""
        try:
            if not ADMIN_CHAT_IDS:
                return
            
            message = f"""
🆕 <b>طلب استضافة جديد</b>

<b>تفاصيل الطلب:</b>
• <b>اسم المالك:</b> {request_data.get('owner', 'غير محدد')}
• <b>رقم العضوية:</b> {request_data.get('membership', 'غير محدد')}
• <b>أرقام الحجز:</b> {request_data.get('bookings', 'غير محدد')}
• <b>تاريخ الإقامة:</b> {request_data.get('from_date', '')} - {request_data.get('to_date', '')}
• <b>عدد الضيوف:</b> {request_data.get('guests', 'غير محدد')}
• <b>رقم التليجرام:</b> {request_data.get('telegram', 'غير محدد')}
• <b>الملاحظات:</b> {request_data.get('notes', 'لا توجد ملاحظات')}

💡 <b>لإدارة الطلب:</b>
• /approve {request_data.get('id', '')[:8]} للموافقة
• /reject {request_data.get('id', '')[:8]} للرفض
            """
            
            for admin_id in ADMIN_CHAT_IDS:
                try:
                    await self.application.bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    logger.error(f"Error sending notification to admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending new request notification: {e}")
    
    async def run(self):
        """Run the bot"""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Telegram bot started successfully")
            
            # Keep the bot running
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            await self.application.stop()

# Global bot instance
bot_instance = None

async def start_bot():
    """Start the Telegram bot"""
    global bot_instance
    bot_instance = HospitalityBot()
    await bot_instance.run()

def get_bot_instance():
    """Get the bot instance for sending notifications"""
    return bot_instance

if __name__ == "__main__":
    # Run the bot
    asyncio.run(start_bot())
