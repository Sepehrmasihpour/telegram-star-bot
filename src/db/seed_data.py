SEED_TELEGRAM_OUTPUTS = {
    "buttons": [
        # ===== shared auth buttons =====
        {
            "name": "btn_send_validation_code",
            "text": "📱 send verification code to phone number",
            "callback_data": "send_validation_code",
        },
        {
            "name": "btn_edit_phone_number",
            "text": "📝 Edit phone number",
            "callback_data": "edit_phone_number",
        },
        {
            "name": "btn_return_to_menu",
            "text": "🔁 return to menu",
            "callback_data": "return_to_menu",
        },
        # login button needs placeholder (phone_number) in callback_data
        {
            "name": "btn_login_to_account",
            "text": "🚪 Login",
            "callback_data": "login_to_acount:{phone_number}",
        },
        # ===== pricing / products =====
        {
            "name": "btn_show_prices",
            "text": "💰 Show prices",
            "callback_data": "show_prices",
        },
        {
            "name": "btn_show_terms",
            "text": "📜 Show terms of service",
            "callback_data": "show_terms",
        },
        {
            "name": "btn_support",
            "text": "🆘 Support",
            "callback_data": "support",
        },
        # ===== payment flow =====
        # IMPORTANT: this will become a URL button at runtime via map_url/url_map
        # so callback_data is a safe dummy; it won't be used when url is present.
        {
            "name": "btn_pay_invoice",
            "text": "💳 Pay Invoice",
            "callback_data": "noop",
        },
        {
            "name": "btn_i_paid",
            "text": "✅ I Paid",
            "callback_data": "confirm_payment:{order_id}",
        },
        {
            "name": "btn_cancel_order",
            "text": "❌ Cancel Order",
            "callback_data": "cancel_order:{order_id}",
        },
        # ===== terms =====
        {
            "name": "btn_read_the_terms",
            "text": "✅ I read the terms",
            "callback_data": "read_the_terms",
        },
        {
            "name": "btn_accepted_terms",
            "text": "✅ I agree and accept",
            "callback_data": "accepted_terms",
        },
        {
            "name": "btn_show_terms_for_acceptance",
            "text": "📜 See terms of service",
            "callback_data": "show_terms_for_acceptance",
        },
        # ===== support section =====
        {
            "name": "btn_contact_support",
            "text": "📞 contact with support",
            "callback_data": "contact_support",
        },
        {
            "name": "btn_common_questions",
            "text": "❓ commonly asked questions",
            "callback_data": "common_questions",
        },
        {
            "name": "btn_return_to_support",
            "text": "📞 Return to Support",
            "callback_data": "return_to_support",
        },
    ],
    "chat_outputs": [
        # ---------------- basic / auth ----------------
        {
            "name": "unsupported_command",
            "text": "❌ Unsupported command.",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "phone_number_input",
            "text": """
🌟 **Welcome to the testing bot!**

📱 **To start, please enter your phone number:**
• Enter the phone number in the `09123456789` format
• The phone number must belong to you
• This phone number is used for verifying your identity and direct payment

💡 **Keep note:**
• Your phone number will remain safe and secret
• It will only be used for verifying your identity and payment
• You can change it at any time

🔐 **Security:**
• All your information is stored using encryption
• No data will be shared with a third party
""",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "phone_number_verification_needed",
            "text": """
❌ **Your phone number ({phone_number}) has not been verified**
📱 In order to continue, please verify your phone number.
""",
            "placeholders": [{"name": "phone_number", "type": "inline"}],
            "buttons": [
                {"button_name": "btn_send_validation_code", "number": 1},
                {"button_name": "btn_edit_phone_number", "number": 2},
                {"button_name": "btn_return_to_menu", "number": 3},
            ],
        },
        {
            "name": "authentication_failed",
            "text": "*authentication failed*",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "max_attempt_reached",
            "text": "❌ *failed 3 times. canceled*",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "invalid_phone_number",
            "text": "❌ *phone number is invalid*",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "invalid_otp",
            "text": "❌ *validation code is invalid*",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "chat_verification_needed",
            "text": """
We need to make sure that this chat belongs to the user with this phone number:
`{phone_number}`
""",
            "placeholders": [{"name": "phone_number", "type": "inline"}],
            "buttons": [
                {"button_name": "btn_send_validation_code", "number": 1},
                {"button_name": "btn_edit_phone_number", "number": 2},
                {"button_name": "btn_return_to_menu", "number": 3},
            ],
        },
        {
            "name": "login_to_acount",
            "text": """
⚠️ **There is already a user with this phone number ({phone_number}).**
Do you want to login to this account or edit your phone number?
""",
            "placeholders": [{"name": "phone_number", "type": "inline"}],
            "buttons": [
                {"button_name": "btn_login_to_account", "number": 1},
                {"button_name": "btn_edit_phone_number", "number": 2},
                {"button_name": "btn_return_to_menu", "number": 3},
            ],
        },
        {
            "name": "already_logged_in",
            "text": """
❌ **You are already logged in**
You are currently logged in to the account with phone number: `{phone_number}`
""",
            "placeholders": [{"name": "phone_number", "type": "inline"}],
            "buttons": [
                {"button_name": "btn_return_to_menu", "number": 1},
            ],
        },
        {
            "name": "phone_numebr_verification",
            "text": """
✅ **The verification code has been sent to your phone number.**
Please enter the code.

💳 **Important points about bank accounts:**
• The account you use for payment must belong to the owner of the phone number
• The system verifies whether the phone number and the account number belong to the same person
• If they don't, your payment will not go through
• If the account belongs to someone else, please use another account
""",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "phone_number_verified",
            "text": """
✅ **Phone number successfully verified!**
🌟 Showing the products...
""",
            "placeholders": [],
            "buttons": [],
        },
        # ---------------- custom / prices ----------------
        {
            "name": "loading_prices_message",
            "text": "💰 please wait a moment to get the most up to date prices",
            "placeholders": [],
            "buttons": [],
        },
        {
            "name": "get_prices",
            "text": """
📊 **Current Prices:**

{prices_block}
""",
            "placeholders": [{"name": "prices_block", "type": "outline"}],
            "buttons": [
                {"button_name": "btn_return_to_menu", "number": 1},
            ],
        },
        # ---------------- dynamic keyboards (append template) ----------------
        {
            "name": "return_to_menu",
            "text": """
🌟 *Welcome to the test bot!*

━━━━━━━━━━━━━━━━━━━━

💡 Choose a product below:

{products_block}

━━━━━━━━━━━━━━━━━━━━
""",
            "placeholders": [{"name": "products_block", "type": "outline"}],
            "buttons": [
                # these are "static actions" appended after dynamic product buttons
                {"button_name": "btn_show_prices", "number": 100},
                {"button_name": "btn_show_terms", "number": 101},
                {"button_name": "btn_support", "number": 102},
            ],
        },
        {
            "name": "buy_product",
            "text": """
🎉 *Buying {product_name}!*

**List of prices** 📋

{prices_block}

💡 *To choose the desired product, press the relevant button.*
""",
            "placeholders": [
                {"name": "product_name", "type": "inline"},
                {"name": "prices_block", "type": "outline"},
            ],
            "buttons": [
                {"button_name": "btn_return_to_menu", "number": 100},
            ],
        },
        # ---------------- checkout ----------------
        {
            "name": "buy_product_version",
            "text": """
🛒 **Chosen product:**
📦 {product_name} — **{product_version_name}**

💰 Price: {price}

━━━━━━━━━━━━━━━━━━━━
💳 Please choose your payment method:
""",
            "placeholders": [
                {"name": "product_name", "type": "inline"},
                {"name": "product_version_name", "type": "inline"},
                {"name": "price", "type": "inline"},
                {"name": "order_id", "type": "inline"},
            ],
            "buttons": [
                # NOTE: you removed crypto from the new code. So keep only gateway/cancel unless you add it back.
                {
                    "button_name": "btn_pay_invoice",
                    "number": 1,
                },  # will be URL in payment_gateway, not here
                {"button_name": "btn_cancel_order", "number": 2},
                {"button_name": "btn_return_to_menu", "number": 3},
            ],
        },
        {
            "name": "payment_gateway",
            "text": """
💻 **Pay via Payment Gateway (Test Gateway)**

📦 Product: {product_name}
💰 Amount: {amount}

━━━━━━━━━━━━━━━━━━━━

📝 **Instructions:**
1️⃣ Tap **"Pay Invoice"**
2️⃣ Review the invoice details
3️⃣ Tap **Online Payment** on the invoice page
4️⃣ You will be redirected to the payment gateway
5️⃣ Enter your card/bank details
6️⃣ After a successful payment, tap **"I Paid"** here

🆔 Invoice ID: `{order_id}`

━━━━━━━━━━━━━━━━━━━━
""",
            "placeholders": [
                {"name": "product_name", "type": "inline"},
                {"name": "amount", "type": "inline"},
                {"name": "order_id", "type": "inline"},
            ],
            "buttons": [
                {
                    "button_name": "btn_pay_invoice",
                    "number": 1,
                },  # runtime url_map turns this into url button
                {"button_name": "btn_i_paid", "number": 2},
                {"button_name": "btn_cancel_order", "number": 3},
            ],
        },
        {
            "name": "payment_confirmed",
            "text": """
✅ **Payment Confirmed**

Thank you. Your payment has been successfully verified.
Your order is now marked as **PAID** and will be processed.

━━━━━━━━━━━━━━━━━━━━
🆔 Order ID: `{order_id}`

If you need anything else, you can return to the main menu.
""",
            "placeholders": [{"name": "order_id", "type": "inline"}],
            "buttons": [
                {"button_name": "btn_return_to_menu", "number": 1},
            ],
        },
        {
            "name": "payment_not_confirmed",
            "text": """
⏳ **Payment Not Found**

We could not verify any successful payment for this order yet.
This may happen if:
• The payment is still being processed
• The payment failed or was canceled
• You have not completed the payment

━━━━━━━━━━━━━━━━━━━━
🆔 Order ID: `{order_id}`

Please complete the payment and then press **"I Paid"** again.
""",
            "placeholders": [{"name": "order_id", "type": "inline"}],
            "buttons": [
                {
                    "button_name": "btn_pay_invoice",
                    "number": 1,
                },  # if you want "Try again" text, make a separate button
                {"button_name": "btn_cancel_order", "number": 2},
                {"button_name": "btn_return_to_menu", "number": 3},
            ],
        },
        # ---------------- terms ----------------
        {
            "name": "terms_and_conditions",
            "text": """
**Terms and Conditions**

By using the test bot you are obligated to follow our terms of service.
If you agree to the terms, press the *'agree and accept'* button.
""",
            "placeholders": [],
            "buttons": [
                {"button_name": "btn_accepted_terms", "number": 1},
                {"button_name": "btn_show_terms_for_acceptance", "number": 2},
            ],
        },
        {
            "name": "show_terms_condititons",
            "text": """
📜 **Terms of service agreement**

🔰 **Terms of Using the Test Bot:**

1️⃣ **General Rules:**
• This service is intended for purchasing Telegram Stars and Telegram Premium.
• The user is required to provide accurate and complete information.
• Any misuse of the service is prohibited.

2️⃣ **Payment Rules:**
• Payments are non-refundable.
• By order of the Cyber Police (FATA), some transactions may require up to 72 hours
  for verification before the product is delivered.

3️⃣ **Privacy:**
• Your personal information will be kept confidential.
• The information is used for identity and payment verification.
• Information will not be shared with any third party.

4️⃣ **Responsibilities:**
• We are committed to delivering products intact and on time.
• The user is responsible for the accuracy of the information they provide.
• Any form of fraud will result in being banned from the service.

5️⃣ **Support:**
• Support is available to you.
• Response time: up to 2 hours.
• Support contact: @TestSupport.

⚠️ **Note:** By using this service, you accept all of the above terms.
""",
            "placeholders": [],
            "buttons": [
                {"button_name": "btn_read_the_terms", "number": 1},
                {"button_name": "btn_return_to_menu", "number": 2},
            ],
        },
        # ---------------- support ----------------
        {
            "name": "support",
            "text": """
🆘 **Test bot support section**

━━━━━━━━━━━━━━━━━━━━

In order to receive help, pick one of the options below:

📞 *Contact with support* – contact info.
❓ *Commonly asked questions* – common answers.
🔁 *Return to main menu* – returns to the main menu.

━━━━━━━━━━━━━━━━━━━━

💡 **Note:** For faster support, first look at commonly asked questions.
""",
            "placeholders": [],
            "buttons": [
                {"button_name": "btn_contact_support", "number": 1},
                {"button_name": "btn_common_questions", "number": 2},
                {"button_name": "btn_return_to_menu", "number": 3},
            ],
        },
        {
            "name": "contact_support_info",
            "text": """
📞 **Support Contact Information**

━━━━━━━━━━━━━━━━━━━━

👤 **Telegram Support:**
• @TestSupport

━━━━━━━━━━━━━━━━━━━━

⏰ **Working Hours:**
• 24/7 (Available around the clock)

💡 **Important Notes:**
• For the fastest response, provide your invoice ID
• In case of payment issues, send your transaction details
• For delivery tracking, include your delivery reference

━━━━━━━━━━━━━━━━━━━━

🔗 **Useful Links:**
• Official Channel: @TestBot
""",
            "placeholders": [],
            "buttons": [
                {"button_name": "btn_return_to_menu", "number": 1},
                {"button_name": "btn_return_to_support", "number": 2},
            ],
        },
        {
            "name": "common_questions",
            "text": """
❔ **Commonly asked Q&A**

━━━━━━━━━━━━━━━━━━━━

1) ...
2) ...
3) ...
4) ...

━━━━━━━━━━━━━━━━━━━━
""",
            "placeholders": [],
            "buttons": [
                {"button_name": "btn_return_to_menu", "number": 1},
                {"button_name": "btn_return_to_support", "number": 2},
            ],
        },
    ],
}
